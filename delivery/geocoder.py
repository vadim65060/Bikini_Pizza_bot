from functools import lru_cache
from decimal import Decimal

from bot_create import config
from yandex_geocoder import Client

client = Client(config.geocoder_token)
city = 'калининград'.lower()


@lru_cache()
def coordinates(address: str):
    if address.lower().find(city) == -1:
        address = city + ' ' + address
    return client.coordinates(address)


@lru_cache()
def address(longitude: Decimal, latitude: Decimal) -> str:
    return client.address(longitude, latitude)
