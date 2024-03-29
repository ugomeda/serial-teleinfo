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
        print(f"Ready : {updater.ready}")
        for value in updater.values.values():
            print(value)

        time.sleep(2)
finally:
    updater.stop()
