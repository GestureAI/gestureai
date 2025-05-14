#!/bin/bash

# activate the virtual environment
source /.venv/bin/activate

# copy app to /tmp/app specifically if using mounting
# this is to avoid the error of "Permission denied" when using docker
# when the app is mounted from the host machine
if [ -d "/tmp/app" ]; then
  rm -rf /tmp/app
fi
cp /app /tmp/app -r

# run app
fastapi run --port 8000