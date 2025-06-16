
import apiclient
import preprocessing
import os
from dotenv import load_dotenv

load_dotenv()  

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")
api_key = os.getenv("API_KEY")

apiclient.fetch_data()
preprocessing.process_data()
