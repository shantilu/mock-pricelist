#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
from datetime import datetime, timedelta
from random import randint
import websockets
import json
from settings import SETTINGS

update_frequency_milliseconds = SETTINGS["update_frequency_milliseconds"]
symbol_list = SETTINGS["symbols"]

DATA_STORAGE = []


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
        time_range = data.get("range", None)
        if time_range is not None:
            result = query_range(time_range[0], time_range[1])
            await websocket.send(json.dumps({"type": "query", "data": result}))


def add_new_data(item):
    DATA_STORAGE.append(item)
    if DATA_STORAGE[0]["timestamp"] < (int(datetime.now().timestamp()) - 400):
        DATA_STORAGE.pop(0)


def query_range(start, end):
    start_time = int(datetime.now().timestamp()) + start
    end_time = int(datetime.now().timestamp()) + end
    result = [-4, -1]
    for i in range(len(DATA_STORAGE)):
        if DATA_STORAGE[i]["timestamp"] > start_time:
            result[0] = i
            break
    for j in range(len(DATA_STORAGE)):
        if DATA_STORAGE[len(DATA_STORAGE) - 1 - j]["timestamp"] < end_time:
            result[1] = len(DATA_STORAGE) - 1 - j
            break
    if result[0] < result[1]:
        return DATA_STORAGE[result[0]:result[1]]
    return DATA_STORAGE[-4:]


async def producer():
    result = []
    d = datetime.now()
    for i in range(SETTINGS['elements_per_update']):
        item = {"symbol": symbol_list[i % 4], "price": 100 + randint(1, 10), "time": d.isoformat() + "Z",
                "timestamp": int(d.timestamp())}
        result.append(item)
        add_new_data(item)
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
