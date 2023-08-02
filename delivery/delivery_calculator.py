import json

from aiogram.types import Location
from shapely.geometry import shape, Point

from constants import DELIVERY_MAP_FILE, DELIVERY_SETTINGS_FILE


class DeliveryCalculator:
    def __init__(self, map_path: str, settings_path: str):
        with open(map_path, 'r', encoding='utf-8') as map_file:
            self.delivery_map = json.load(map_file)
        with open(settings_path, 'r', encoding='utf-8') as settings_file:
            self.delivery_settings = json.load(settings_file)

    async def get_delivery_zone(self, point: Point):
        zone = None
        for feature in self.delivery_map['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                zone = feature
        return zone

    async def get_delivery_settings(self, zone_id):
        for settings in self.delivery_settings['delivery_settings']:
            for zone in settings['zones']:
                if zone == zone_id:
                    return settings
        return None

    async def get_delivery_price(self, point: Point | Location | tuple, order_price: int):
        if isinstance(point, Location):
            point = Point(point.longitude, point.latitude)
        if isinstance(point, tuple):
            point = Point(point[0], point[1])
        zone = await self.get_delivery_zone(point)
        if zone is None:
            return None, 'Вне зоны доставки'
        zone_id = zone['id']
        settings = await self.get_delivery_settings(zone_id)
        if settings['min_price'] > order_price:
            return None, zone['properties']['description']
        if settings['max_paid_delivery_price'] > order_price:
            return settings['delivery_price'], zone['properties']['description']
        return 0, zone['properties']['description']


delivery_calculator = DeliveryCalculator(DELIVERY_MAP_FILE, DELIVERY_SETTINGS_FILE)
