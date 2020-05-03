# Serial Teleinfo

This project provides Python utilities to access data from Enedis energy meters using a serial converter :

- `serial_teleinfo` provides the classes to read and parse data
- `serial_teleinfo.server` is a simple web-server to access live readings through a JSON api

You will need a serial adapter such as the [Micro Teleinfo](https://www.tindie.com/products/hallard/micro-teleinfo-v20/)
to use this package.

## Running the server

The web server exposes a JSON API providing live data read from the energy meter :

```json
{
   "connected":true,
   "values":{
      "ISOUSC": [30, "A"],
      "BASE": [804220, "Wh"],
      "PTEC": ["TH", null],
      "IINST": [1, "A"],
      "IMAX": [90, "A"],
      "PAPP": [340, "VA"],
      "HHPHC": ["A", null],
      "MOTDETAT": ["000000", null],
      "ADCO": ["012345678901", null],
      "OPTARIF": ["BASE", null]
   }
}
```

### Configuration file

The configuration is as follows :

```ini
[teleinfo]
device=/dev/ttyUSB0
loglevel=INFO

[http]
listen=127.0.0.1:8000

[users]
apiuser=apipassword
```

- `teleinfo/device` : The path to the serial port.
- `teleinfo/loglevel` *(optionnal)* : Modifies the log verbosity, it can be `DEBUG`, `INFO`, `WARNING`, `ERROR`. Default is `INFO`.
- `http/listen` : The host and port to listen to.
- `users` : A list of user/password allowed to use the API (using basic authentification).

### Using python

Install the package :

```bash
pip install serial-teleinfo[server]
```

Create a configuration file `teleinfo.ini` as described above and run the command :

```bash
python -m serial_teleinfo.server teleinfo.ini
```

Once the server is running, you can access the values at [http://apiuser:apipassword@localhost:8000/status.json](http://apiuser:apipassword@localhost:8000/status.json).

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

Install the package :

```bash
pip install serial-teleinfo
```

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

This utility class manages a background thread to update values indefinitely.
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