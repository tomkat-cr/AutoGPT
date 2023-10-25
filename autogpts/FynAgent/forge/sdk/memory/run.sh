#!/bin/sh
ENV_FILE="../../../.env"
set -o allexport; source ${ENV_FILE}; set +o allexport ;
poetry run python -m weaviate_memstore
