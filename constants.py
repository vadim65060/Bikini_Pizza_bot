from enum import Enum
import datetime as dt
from middleware.functions import dt_to_dtdict, dtdict_to_str, ACCUSATIVE_TIME_UNITS_FORMS

import pytz

MAX_FULLNAME_LEN = 300
TZ = pytz.timezone("Europe/Moscow")
DATETIME_FORMAT = "%d.%m.%Y %H.%M"
LOG_DATETIME_FORMAT = "%d.%m.%Y %H.%M.%S"
SUPPORT_TIMEDELTA = dt.timedelta(minutes=120)
SUPPORT_TIMEDELTA_ACCUSATIVE_STR = dtdict_to_str(dt_to_dtdict(SUPPORT_TIMEDELTA), ACCUSATIVE_TIME_UNITS_FORMS)
PREVIOUS_REGISTERED_BOT_REWARD = 150
LETTERING_PERIOD = 0.5

ADMIN_BOT_NAME = 'AdminBot'
USER_BOT_NAME = 'UserBot'

LOGO_PATH = "logo.jpg"
MINIATURE_NAME = "logo.jpg"

STORE_PATH = "misc/store/"

DELIVERY_MAP_FILE = 'delivery/delivery_map.geojson.json'
DELIVERY_SETTINGS_FILE = 'delivery/delivery_settings.json'

PERIOD_TYPES = ['ч', 'д']

LETTERING_ADMIN_ID = 769074534

CASHBACK_PERCENT = 0.05


class OrderStates(Enum):
    ORDER_ACCEPTED = 0
    ORDER_COOKING = 1
    ORDER_DONE = 2
    ORDER_DELIVERY = 3
    ORDER_DELIVERED = 4
    ORDER_ISSUED = 10


class TransactionTypes(Enum):
    CREATE_STUFF = 'create_stuff'
    UPDATE_STUFF = 'update_stuff'
    DELETE_STUFF = 'delete_stuff'
    CREATE_STUFF_CATEGORY = 'create_stuff_category'
    UPDATE_STUFF_CATEGORY = 'update_stuff_category'
    DELETE_STUFF_CATEGORY = 'delete_stuff_category'
    USER_REGISTER = "user_register"
    SUPPORT_REQUEST = "support_request"  # Запрос в тех. поддержку
    PROMO_USAGE = "promo_usage"
    PROMO_CREATE = "create_promo"
    MONEY_GET = "money_get"
    ADMIN_GAVE = "admin_gave"
    PURCHASE_SUCCESS = "purchase_success"
    PURCHASE_FAIL = "purchase_fail"
    ADMIN_TAKE_OUT = "admin_take_out"
    ISSUE_MERCH = "merch_issue"
    MERCH_RETURN_BACK = "merch_return_back"
    ISSUE_MERCH_FAIL = "issue_merch_fail"
    MERCH_RETURN_BACK_FAIL = "merch_return_back_fail"


HELP_TEXT = """<b>Справка по боту</b>"""
