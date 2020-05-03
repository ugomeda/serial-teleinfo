FROM python:3-slim

WORKDIR /app/
RUN pip install aiohttp http_basic_auth pyserial

COPY serial_teleinfo /app/serial_teleinfo/
COPY entrypoint.sh /app/

ENV TELEINFO_DEVICE /dev/ttyUSB0
ENV TELEINFO_LOGLEVEL INFO
ENV HTTP_LISTEN 0.0.0.0:8000
ENV USERS_USER apiuser
ENV USERS_PASSWORD apipassword

EXPOSE 8000

ENTRYPOINT /app/entrypoint.sh
