# maintainer info
FROM python:3.12-slim
LABEL maintainer="carrergt@gmail.com"

RUN apt update && apt install -y libmagic-dev libgl1 libglib2.0-0 && pip3 install uv

# copy app files if mounting is not used
# COPY ./app  /app
# COPY ./start.sh /app

COPY ./pyproject.toml /
RUN uv sync

WORKDIR /app

CMD ["bash", "start.sh"]
