FROM python:3-slim

WORKDIR /app/
COPY requirements.txt requirements-server.txt /app/
RUN pip install -r requirements.txt -r requirements-server.txt

COPY serial_teleinfo /app/serial_teleinfo/
COPY serial_teleinfo_server /app/serial_teleinfo_server/
COPY docker/entrypoint.sh /app/

ENV TELEINFO_DEVICE /dev/ttyUSB0
ENV TELEINFO_LOGLEVEL INFO
ENV HTTP_LISTEN 0.0.0.0:8000
ENV USERS_USER apiuser
ENV USERS_PASSWORD apipassword

EXPOSE 8000

ENTRYPOINT /app/entrypoint.sh