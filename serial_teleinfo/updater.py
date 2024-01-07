import logging
import threading
from typing import Dict

from serial_teleinfo import Client, ParserException, UnknownKeyException, Value

logger = logging.getLogger(__name__)

MAX_CONSECUTIVE_ERRORS = 16


class ValueUpdater:
    """Helper class updating the values in a background thread
    and providing the result through the values property.
    """

    def __init__(self, port):
        # Config
        self._port = port

        # State
        self._values = {}
        self._connected = False
        self._end_of_frame_count = 0
        self._ignored_keys = []  # Unknown keys already logged

        # Thread stuffs
        self._thread = None
        self._stop_event = None

    def start(self):
        """Starts the background thread"""
        if self._thread is not None:
            raise RuntimeError("Method start() can only be called once.")

        self._stop_event = threading.Event()
        self._thread = threading.Thread(
            target=self._update_loop, name=f"{self._port} teleinfo updater", daemon=True
        )
        self._thread.start()

    def stop(self):
        """Stops the background thread and waits for its death."""
        self._stop_event.set()
        self._thread.join()

    def update_value(self, value: Value):
        """This method can be overriden to access values soon as they are read"""
        self._values[value.key] = value

        if value.end_of_frame:
            self._end_of_frame_count += 1

    def _update_loop(self):
        while True:
            try:
                logger.debug(f"Opening serial connection to {self._port}")
                with Client(self._port) as client:
                    self._update(client)
            except Exception as e:
                logger.error(
                    f"Error while updating values : {e}\n\nTrying to reconnect in 10 seconds..."
                )

            logger.debug(f"Disconnected from {self._port}")
            self._connected = False
            self._end_of_frame_count = 0

            if self._stop_event.wait(10):
                return  # We were asked to stop

    def _update(self, client):
        """Reads the values and updates the values dict continuoulsy.

        Raises:
            TeleinfoException: If more than 16 consecutive lines coulds not be read.
            serial.SerialException: If the serial connection had an error.
        """
        consecutive_read_errors = 0

        while True:
            try:
                # Exit if the thread should stop
                if self._stop_event.is_set():
                    return

                # Actually read the value
                value = client.read_value()

                # Log if we succesfully read our first value
                if not self._connected:
                    self._connected = True
                    logger.info("Connected to Teleinfo")

                # Update table
                self.update_value(value)

                # Reset counters
                consecutive_read_errors = 0
            except UnknownKeyException as e:
                if e.key not in self._ignored_keys:
                    self._ignored_keys.append(e.key)

                    logger.warn(
                        f"Unable to find a parser for {e.key}. This key will be ignored."
                    )
            except ParserException as e:
                logger.debug(str(e))
                consecutive_read_errors += 1

                if consecutive_read_errors > MAX_CONSECUTIVE_ERRORS:
                    # Will be catched in
                    raise Exception(
                        f"Encountered too many unreadable lines while reading on {self._port}."
                    )

    @property
    def values(self) -> Dict[str, Value]:
        """Returns a copy of the current values dictionnary"""
        return dict(self._values)

    @property
    def port(self) -> str:
        return self._port

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def ready(self) -> bool:
        # We gathered all the values only once we had the
        # first end of frame marker (partial update) and a
        # second one
        return self._end_of_frame_count >= 2
