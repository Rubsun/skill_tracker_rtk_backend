#!/bin/bash

docker run \
  --name pgsql-test \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test  \
  -e POSTGRES_DB=test \
  -p 5433:5432 \
  -d postgres:16.0-alpine3.18


sleep 10
