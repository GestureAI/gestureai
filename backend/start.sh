#!/bin/bash

# activate the virtual environment
source /.venv/bin/activate

# run app
cd /app
fastapi run --port 3000