#! /bin/sh -e

cat <<EOF >/app/teleinfo.ini
[teleinfo]
device=$TELEINFO_DEVICE
loglevel=$TELEINFO_LOGLEVEL

[http]
listen=$HTTP_LISTEN

[users]
$USERS_USER=$USERS_PASSWORD
EOF

exec python -m serial_teleinfo_server /app/teleinfo.ini