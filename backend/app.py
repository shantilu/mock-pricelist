#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
from datetime import datetime
from random import randint
import websockets
import json
from settings import SETTINGS

update_frequency_milliseconds = SETTINGS["update_frequency_milliseconds"]
symbol_list = SETTINGS["symbols"]

class LighthouseToyServer:
    def __init__(self, symbols=None, update_frequency_milliseconds=500, elements_per_update=50):
        self.symbols = symbols or SETTINGS["symbols"]
        self.update_frequency = update_frequency_milliseconds
        self.elements_per_update = elements_per_update


async def consumer_handler(websocket, path):
    global update_frequency_milliseconds
    async for message in websocket:
        data = json.loads(message)
        print(data)
        frequency = data.get('frequency', None)
        if frequency is not None:
            try:
                update_frequency_milliseconds = int(frequency)
                await websocket.send(json.dumps({"type": "notice", "msg": frequency}))
            except:
                print("error")


async def producer():
    result = []
    for i in range(SETTINGS['elements_per_update']):
        result.append({"symbol": symbol_list[i%4], "price": 100 + randint(1, 10),
                       "time": datetime.utcnow().isoformat() + "Z"})
    return json.dumps(result)


async def producer_handler(websocket, path):
    while True:
        message = await producer()
        await websocket.send(message)
        await asyncio.sleep(update_frequency_milliseconds / 1000)


async def handler(websocket, path):
    consumer_task = asyncio.ensure_future(
        consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(
        producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


start_server = websockets.serve(handler, "127.0.0.1", 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
