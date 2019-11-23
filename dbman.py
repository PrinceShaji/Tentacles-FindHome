#!/usr/bin/env python3

import pymongo
from pymongo import MongoClient
from datetime import datetime
import pytz

class mongodb:
    """dbman class"""

    def __init__(self):    
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['findhome']
        
        # All listings
        self.all_listings = self.db['all_listings']

        # District wise listing (detailed scrapes).
        self.alapuzha = self.db['alapuzha']
        self.ernakulam = self.db['ernakulam']
        self.idukki = self.db['idukki']
        self.kannur = self.db['kannur']
        self.kasaragod = self.db['kasaragod']
        self.kollam = self.db['kollam']
        self.kottayam = self.db['kottayam']
        self.kozhikode = self.db['kozhikode']
        self.malappuram = self.db['malappuram']
        self.palakkad = self.db['palakkad']
        self.pathanamthitta = self.db['pathanamthitta']
        self.thiruvananthapuram = self.db['thiruvananthapuram']
        self.thrissur = self.db['thrissur']
        self.wayanad = self.db['wayanad']
        # Example template.
        self.all_listing_template = {
            'district': 'Name of the district',
            'listing_id': 'ID of the listing',
            'scrape_status': False,
            'timestamp': 'timestamp utc'
            }
    def write_all_listings(self, data):
        """  """
        if isinstance(data, dict):
            self.all_listings.insert_one(data)
        elif isinstance(data, list):
            self.all_listings.insert_many(data)
        else:
            print('something is wrong')
    