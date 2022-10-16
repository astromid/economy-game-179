#!/usr/bin/env bash
docker run --rm --detach -p 3306:3306 -h 0.0.0.0  --env-file .env mariadb:latest
sleep 5
alembic upgrade head
