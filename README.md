# Serial Teleinfo

This repository provides 2 python packages to read data from ENEDIS energy meters.

- `serial-teleinfo-server` : A simple web-server providing live readings through a JSON api
- `serial-teleinfo` : A package providing the methods to read and parse data

You will need a serial adapter such as the [Micro Teleinfo](https://www.tindie.com/products/hallard/micro-teleinfo-v20/).

## Running the server

### Configuration file

The configuration is as follows :

```ini
[teleinfo]
device=/dev/ttyUSB0

[http]
listen=127.0.0.1:8000

[users]
apiuser=apipassword
```

You can add a `loglevel` entry to modify the log verbosity. It can be `DEBUG`, `INFO`, `WARNING`, `ERROR`. Default is `INFO`.

```ini
[teleinfo]
device=/dev/ttyUSB0
loglevel=DEBUG
```

### Using python

Install the package :

```bash
pip install serial-teleinfo-server
```

Create a configuration file `teleinfo.ini` as described above and run the command :

```bash
python -m serial-teleinfo-server teleinfo.ini
```

You can access the values at [http://apiuser:apipassword@localhost:8000/status.json](http://apiuser:apipassword@localhost:8000/status.json).

### Using Docker

A docker image is provided, here's an example `docker-compose.yml` :

```yaml
version: '3'
services:
  teleinfo:
    image: teleinfo
    restart: always
    devices:
      - /dev/ttyUSB0
    environment:
      HTTP_LISTEN: "0.0.0.0:7777"
      USERS_PASSWORD: "Str0ngPa55w0rd!"
      TELEINFO_LOGLEVEL: "DEBUG"
    ports:
      - "7777:7777"
```

You can access the values at [http://apiuser:Str0ngPa55w0rd!@SERVERIP:7777/status.json](http://apiuser:Str0ngPa55w0rd!@SERVERIP:7777/status.json).

The environment variables are :

| Variable          | Default value |
|-------------------|---------------|
| TELEINFO_DEVICE   | /dev/ttyUSB0  |
| TELEINFO_LOGLEVEL | INFO          |
| HTTP_LISTEN       | 0.0.0.0:8000  |
| USERS_USER        | apiuser       |
| USERS_PASSWORD    | apipassword   |


## Using the library

### serial_teleinfo.Client

This class provides direct access to the values read on the serial port.

Here's an example usage :

```python
import serial
from serial_teleinfo import Client, TeleinfoException

try:
    with Client("/dev/ttyUSB0") as client:
        while True:
            print(client.read_value())
except TeleinfoException as e:
    print(e)
except serial.SerialException as e:
    print(e)
```

You can also refer to the `serial_teleinfo.ValueUpdater` implementation.

### serial_teleinfo.ValueUpdater

This utility class manages a background thread to update values undefinitely.
It will automatically handle reconnection to the serial port and ignore temporary errors or
reccuring unknown keys.

It provides a `values` property and a `connected` property.

You can also override the `update_value` method to access the read values as they are read.

Heres an example usage :

```python
import time
from serial_teleinfo import ValueUpdater

class MyValueUpdater(ValueUpdater):
    def update_value(self, value):
        print(f"Updated {value.key}")

        super().update_value(value)

updater = MyValueUpdater("/dev/ttyUSB0")
updater.start()

try:
    while True:
        print(f"Connected : {updater.connected}")
        for value in updater.values.values():
            print(value)
        
        time.sleep(5)
finally:
    updater.stop()
```
