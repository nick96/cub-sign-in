#!/usr/bin/env bash

echo "Killing old Docker processes"
docker-compose rm -fs

echo "Building Docker containers"
docker-compose up --build
