#!/bin/bash
# Check if the container exists
if [ "$(docker ps -q -f name=calibrecli)" ]; then
  #If the container exists, stop and remove it
  docker stop calibrecli
  docker rm calibrecli
fi
docker run \
  -d\
  --name=calibrecli \
  -e PUID=1000 \
  -e PGID=100 \
  -e TZ=Europe/Paris \
  -v /Users/olivier.fostier/Dev_project/calibre-web/library:/library \
  -v ./:/code\
  lscr.io/linuxserver/calibre:latest

docker exec -it calibrecli calibre-debug /code/run.py
# docker stop calibrecli
# docker rm calibrecli 
