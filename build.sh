#!/usr/bin/env bash

export TRAEFIK_FRONTEND_RULE=Host:nspain.me
docker-compose build --parallel

docker-compose up -d
