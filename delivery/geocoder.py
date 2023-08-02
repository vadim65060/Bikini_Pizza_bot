from functools import lru_cache

from yandex_geocoder import Client

client = Client("e3bce2b1-53dc-4e02-a181-76a5c208c3ec")
city = 'калининград'.lower()


@lru_cache()
def coordinates(address: str):
    if address.lower().find(city) == -1:
        address = city + ' ' + address
    return client.coordinates(address)
