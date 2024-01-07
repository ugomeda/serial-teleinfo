import asyncio
from typing import Dict

from aiohttp import web

from serial_teleinfo import ValueUpdater
from serial_teleinfo.server.routes import routes


async def start_value_updater(app):
    app["updater"].start()


async def stop_value_updater(app):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, app["updater"].stop)


def app_factory(device: str, users: Dict[str, str]):
    app = web.Application()
    app.add_routes(routes)

    app["updater"] = ValueUpdater(device)
    app.on_startup.append(start_value_updater)
    app.on_cleanup.append(stop_value_updater)

    app["users"] = users

    return app
