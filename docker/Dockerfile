FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY assets/ ./assets/
COPY pages/ ./pages/

COPY app.py .
COPY cron.py .

# Config
COPY myconfig.py .
COPY mylibrary.py .
COPY notifications.json .

# Allows running the Docker image with args "app" or "cron"
COPY docker/entrypoint.sh /entrypoint.sh
ENV TI_MONITORING_FILE_NAME=/data/data.hdf5

ENTRYPOINT ["/entrypoint.sh"]
# Default to running Web-App
CMD ["app"]
