from functools import lru_cache
from decimal import Decimal

from yandex_geocoder import Client

client = Client("e3bce2b1-53dc-4e02-a181-76a5c208c3ec")
city = 'калининград'.lower()


@lru_cache()
def coordinates(address: str):
    if address.lower().find(city) == -1:
        address = city + ' ' + address
    return client.coordinates(address)


@lru_cache()
def address(longitude: Decimal, latitude: Decimal) -> str:
    return client.address(longitude, latitude)
