#!/usr/bin/env bash
set -eo pipefail
docker run --rm --detach -p 3306:3306 -h 0.0.0.0  --env-file .env mariadb:latest
sleep 10
alembic upgrade head
