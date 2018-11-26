#!/usr/bin/env bash

TARBALL=${1:-cub-attendance.tar.gz}

tar --exclude "*/node_modules" \
	--exclude "*/__pycache__" \
	--exclude "*/.venv" \
	--exclude "*test*" \
	--exclude "*~" \
	-cvzf $TARBALL \
	.env \
	build-and-run.sh \
  	docker-compose.yml \
	traefik \
	app/* \
	celery-queue/* \
	prod.cfg

scp $TARBALL cub_attendance.digital_ocean:
rm $TARBALL
