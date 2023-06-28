#!/bin/bash

# Configure replicaSet, create admin user and app user

mongosh -- <<EOF
var cfg = { _id: "replicaSetName", version: 1, protocolVersion: 1, members: [{ _id: 0, host: "localhost:27017", arbiterOnly: false, buildIndexes: true, hidden: false, priority: 10 }]}
rs.initiate(cfg);
EOF

sleep 20

mongosh -- <<EOF
use admin
db.createUser({user: "mongodb_cluster_admin",pwd: "${MONGODB_CLUSTER_ADMIN_PASSWORD}",roles: [{ role: "userAdminAnyDatabase", db: "admin"},{ role: "dbAdminAnyDatabase", db: "admin"},{ role: "readWriteAnyDatabase", db: "admin"},{ role: "root", db: "admin"}]});
EOF

sleep 5

mongosh -u mongodb_cluster_admin -p ${MONGODB_CLUSTER_ADMIN_PASSWORD} <<EOF
use admin
db.createUser({user: "pickle_admin", pwd: "${MONGODB_USER_PASSWORD}", roles: [{ role: "readWrite", db: "dbname1" },{ role: "dbAdmin", db: "dbname1" },{ role: "readWrite", db: "dbname2" },{ role: "dbAdmin", db: "dbname2" }]});

EOF

# Create file in /data/configdb when this is complete to ensure this script is not re-run if container is deleted
if [[ $? -eq 0 ]]; then
    echo "Creating lock file..."
    touch /data/configdb/preconfigured
    echo "Done"
fi


