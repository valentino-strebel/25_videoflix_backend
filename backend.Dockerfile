# -----------------------------------------------------------------------------
# Base Image
# -----------------------------------------------------------------------------
# Using Python 3.12 on Alpine for a small, production-friendly container.
FROM python:3.12-alpine

# -----------------------------------------------------------------------------
# Metadata
# -----------------------------------------------------------------------------
LABEL maintainer="mihai@developerakademie.com"
LABEL version="1.0"
LABEL description="Python 3.12 Alpine image for Videoflix backend"

# -----------------------------------------------------------------------------
# App Directory
# -----------------------------------------------------------------------------
WORKDIR /app
COPY . .

# -----------------------------------------------------------------------------
# System Dependencies & Python Packages
# -----------------------------------------------------------------------------
RUN sed -i 's/\r$//' backend.entrypoint.sh && \
    apk update && \
    apk add --no-cache --upgrade bash && \
    apk add --no-cache postgresql-client ffmpeg && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    chmod +x backend.entrypoint.sh

# -----------------------------------------------------------------------------
# Network
# -----------------------------------------------------------------------------
EXPOSE 8000

# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------
ENTRYPOINT [ "bash", "-c", "sed -i 's/\r$//' backend.entrypoint.sh && bash backend.entrypoint.sh" ]
