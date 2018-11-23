#!/usr/bin/env bash

tar --exclude "*/node_modules" \
	--exclude "*/__pycache__" \
	--exclude "*/.venv" \
	--exclude "*test*" \
	--exclude "*~" \
	-cvzf cub-attendance.tar.gz \
	.env \
	build.sh \
  	docker-compose.yml \
	traefik \
	app/.env \
	app/*
	

