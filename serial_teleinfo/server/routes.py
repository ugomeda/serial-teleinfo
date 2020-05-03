from aiohttp import web
from http_basic_auth import parse_header, BasicAuthException

routes = web.RouteTableDef()


@routes.get("/status.json")
async def status(request):
    # Chech authorization
    try:
        authorization = request.headers.get("Authorization", "")
        login, password = parse_header(authorization)

        if login not in request.app["users"] or request.app["users"][login] != password:
            raise BasicAuthException()
    except BasicAuthException:
        raise web.HTTPUnauthorized(headers={"WWW-Authenticate": "Basic"})

    # Fetch and return data
    client = request.app["updater"]
    json_values = {
        key: [value.value, value.unit] for key, value in client.values.items()
    }

    return web.json_response({"connected": client.connected, "values": json_values})
