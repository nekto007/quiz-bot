import os

import redis

HOST = os.environ['HOST']
PORT = os.environ['PORT']
PASSWORD = os.environ['PASSWORD']


def connection(PORT, HOST, PASSWORD):
    connection = redis.Redis(
        host=HOST,
        port=PORT,
        password=PASSWORD)
    return connection
