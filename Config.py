import sqlite3
import logging
connection = sqlite3.connect('people.db3', check_same_thread=False)
cursor = connection.cursor()
token = '6440713219:AAEGHlY5rSfB2PBxhVtYE57Q1eLcSX_N3tc'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
