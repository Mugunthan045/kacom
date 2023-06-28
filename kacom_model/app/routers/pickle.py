import redis
import datetime
import glob
import json
import os
import pickle
import re
import shutil
import traceback

import aiofiles
import numpy as np
from app.db import db
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, File, Form, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..dependencies import get_current_user
from ..exceptions import *
from .model import Features, FileUploadResponse, Message, PredictResponse
from ..redis_client import redis_client

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 50
COLLECTION = "pickle_model"

router = APIRouter()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    responses={500: {"model": Message}},
    status_code=status.HTTP_201_CREATED,
    description="Upload pickle models",
    tags=["Endpoint Category"],
)
async def save_pickle(
    token: str = Depends(get_current_user),
    version: float = Form(...),
    pickle_file: UploadFile = File(...),
):
    try:
        if pickle_file.content_type != "application/octet-stream":
            return UNSUPPORTED_MEDIA_EXCEPTION
        allowed_extension = ["pkl", "pcl"]
        file_extension = pickle_file.filename.split(".")[-1]
        if file_extension not in allowed_extension:
            return UNSUPPORTED_MEDIA_EXCEPTION

        filename = pickle_file.filename
        filepath = "/tmp/" + filename
        # Upload file
        async with aiofiles.open(filepath, "wb") as f:
            while chunk := await pickle_file.read(DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
        model = load_model(filepath)
        features = model.features_name
        if not features:
            # Delete file
            os.remove(filepath)
            return CONTENT_NOTFOUND_EXCEPTION
        check_version = await db[COLLECTION].find_one(
            {"version": version, "filename": filename}
        )
        if check_version:
            return VERSION_CONFLICT_EXCEPTION
        pickle_file.file.close()
        post = {
            "filename": filename,
            "filepath": filepath,
            "version": version,
            "features": features,
            "date": datetime.datetime.utcnow(),
        }

        # Entry in MongoDB
        result = await db[COLLECTION].insert_one(post)
        insert_id = result.inserted_id
    except Exception:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": "error uploading"})

    return {"id": insert_id, "features": jsonable_encoder(features)}


@router.post(
    "/predict",
    response_model=PredictResponse,
    responses={500: {"model": Message}},
    status_code=status.HTTP_200_OK,
    description="Predict values",
    tags=["Endpoint Category"],
)
async def prediction(
    token: str = Depends(get_current_user), features_input: Features = Body(...)
):
    try:
        features_byte = pickle.dumps(features_input)
        prediction = redis_client.get(features_byte)
        if prediction is not None:
            return {"predicted": prediction}
        values = []
        model_db = await db[COLLECTION].find_one({"_id": ObjectId(features_input.id)})
        if not model_db:
            return INVALID_TOKEN_EXCEPTION
        model_path = model_db["filepath"]
        model = load_model(model_path)
        for feature in model_db["features"]:
            values.append(features_input.features[0][feature])
        output = model.predict(np.array(values).reshape(1, -1))
        prediction = output[0]
        redis_client.set(features_byte, prediction)
        return {"predicted": prediction}
    except Exception:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": "error predicting"})


# Loading model
def load_model(model_path):
    model = pickle.load(open(model_path, "rb"))
    return model
