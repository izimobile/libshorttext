#!/usr/bin/env bash

PROTO_DIR="../../src/config/serve_env/protos"
PLUGIN=`which grpc_python_plugin`

protoc -I $PROTO_DIR --python_out=. --grpc_out=. --plugin=protoc-gen-grpc=$PLUGIN $PROTO_DIR/tagRpc.proto
