import streamlit as st
import pandas as pd
import pymongo
from pymongo import MongoClient
from pymongoarrow.api import Schema
from pymongoarrow.monkey import patch_all
from bson import ObjectId

DB_KEY = st.secrets["db_key"]
BASIC_SCHEMA = {
    '_id': ObjectId,
    'url': str,
    'Τιμή': int,
    'Εμβαδόν': int,
    'loc_lat': float,
    'loc_long': float,
    'Location': str,
    'Όροφος': int,
    'Έτος κατασκευής': int,
    'Δημοσίευση Αγγελίας': str,
    'DateScrape': str,
    'Τύπος': str,
}
COLLECTION_NAME = 'clean'
# FULL_SCHEMA = pma.api.Schema({'_id': ObjectId, 'Τιμή': int, 'Εμβαδόν': int, 'loc_lat': float, 'loc_long': float, 'Location': str,
#                               'Όροφος': int, 'Type': str, 'Έτος_κατασκευής': int, 'Δημοσίευση_Αγγελίας': str, 'dateScrape': str})


class Database:
    def __init__(self, collection_name: str = COLLECTION_NAME, schema: dict = BASIC_SCHEMA, test: bool = False):
        self.test = test
        self.collection_name = collection_name
        self.schema = schema

    def connect_db(self) -> pymongo.collection.Collection:
        collection_name = self.collection_name

        cluster = MongoClient(DB_KEY)
        db = cluster['housing']

        collection = db[collection_name]
        if self.test:
            collection = db['test']

        return collection

    def search_data(self, collection: pymongo.collection.Collection, schema: dict = BASIC_SCHEMA) -> pd.DataFrame:
        full_schema = Schema(schema)

        data = collection.find_pandas_all(
            {'Τιμή': {'$not': {'$eq': None}}}, schema=full_schema)

        columns = [
            'id',
            'url',
            'price',
            'squared_meters',
            'location_lat',
            'location_long',
            'location',
            'floor',
            'year',
            'listing_date',
            'scrape_date',
            'type'
        ]
        data.columns = columns

        return data

    def fetch_data(self) -> pd.DataFrame:
        schema = self.schema

        collection = self.connect_db()
        patch_all()
        return self.search_data(collection, schema)
