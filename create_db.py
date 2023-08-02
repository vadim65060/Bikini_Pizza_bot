from classes import Config
from database import admin_db_funcs

config = Config("config.json")
data_base = admin_db_funcs.AdminDataBase(config.db_path)
