import configparser
import argparse
import sys
import logging
from aiohttp import web

from serial_teleinfo_server.server import app_factory

# Fetch arguments
parser = argparse.ArgumentParser()
parser.add_argument("config_path")
args = parser.parse_args()

# Parse configuration
try:
    try:
        config = configparser.ConfigParser()
        config.read(args.config_path)

        device = config["teleinfo"]["device"]
        http_listen = config["http"]["listen"]
        users = config["users"]
    except KeyError as e:
        raise Exception(f"Could not find the key {e}")

    # Parse listen field
    try:
        http_host, http_port = http_listen.split(":", 2)
        http_port = int(http_port)
    except Exception as e:
        raise Exception(f"Could not parse http/listen field {http_listen}: {e}")

    # Parse loglevel
    try:
        loglevel = getattr(logging, config["teleinfo"].get("loglevel", "INFO"))
    except Exception as e:
        raise Exception(f"Could not parse the field loglevel : {e}")
except Exception as e:
    print(
        f"Error while loading configuration, please check {args.config_path}",
        file=sys.stderr,
    )
    print(str(e), file=sys.stderr)
    sys.exit(1)


# Configure logging
logging.basicConfig(level=loglevel)

# Create the client
server = app_factory(device, users)
web.run_app(server, port=http_port, host=http_host, access_log=None)
