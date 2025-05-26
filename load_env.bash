#!/bin/bash
set -a
[ -f .env ] && . .env
set +a

echo "Loaded environment variables from .env file"