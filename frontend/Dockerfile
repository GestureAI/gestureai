# maintainer info
FROM node:24-slim AS dependencies
LABEL maintainer="carrergt@gmail.com"

COPY ./app /app
COPY ./start.sh /app

WORKDIR /app
RUN npm i && npm run build

# start command
CMD ["bash","start.sh"]
