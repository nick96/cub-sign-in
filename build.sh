#!/usr/bin/env bash
source .env
docker-compose build
docker-compose up -d
