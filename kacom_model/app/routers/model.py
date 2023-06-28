from typing import List

from bson import ObjectId
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class FileUploadResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="id")
    features: List

    class Config:
        allow_population_by_field_name = True
        arbitary_type_allowed = True
        json_encoders = {ObjectId: str}


class PredictResponse(BaseModel):
    predicted: str


class Features(BaseModel):
    id: str
    features: List[dict]
