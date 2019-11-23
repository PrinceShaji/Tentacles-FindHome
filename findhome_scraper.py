#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import datetime, pytz
from dbman import mongodb
from time import sleep


class scraper():
    def __init__(self):
        self.headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15',
                        'Accept': '*/*',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Origin': 'https://www.findhome.com',
                        'DNT': '1',
                        'Connection': 'close',
                        'Referer': 'https://www.findhome.com/property-for-sale-in-ernakulam/srp'
                    }
        self.district_url = 'https://www.findhome.com/property-for-{}-in-{}/srp'
        self.district_codes = {}
        self.query_url = 'https://www.findhome.com/search/ajaxSearchResults/'
        self.query_parameters = 'is_ajax=1&languageID=1&languageKey=en&searchCountryID=&searchCountryKey=&state=&city=&searchPropertyTypeKey=&searchPropertyAdded=&searchKeyword=&searchRegion=2-1&searchPropertyPurpose=Sell&searchMinPrice=0&searchMaxPrice=0&searchPropertyTypeID=&searchAttributesStr=&searchType=normal&searchCityIDs=&searchAgencyIDs=&sortBy=&limitFrom={}&limitTo={}&suggested=0&mainTab=listTab&searchLat=&searchLong=&searchRadius=1&itemType=Property&searchUserTypeID=&url=https://www.findhome.com/property-for-sale-in-ernakulam/srp&Coordinates=&possessionStatus='
        self.total_listings = self.get_total_listings()
        self.start_number = 0
        self.end_number = 10000   # current
        self.query_increment = 10
    
    def get_total_listings(self):
        response = requests.get(self.district_url.format('sale', 'ernakulam'), headers=self.headers)
        title = str(BeautifulSoup(response.text, 'lxml').title)
        total_numbers = title.split(" ")[2]
        return int(total_numbers)

    def get_pagination(self, total_listings, current):
        """ To get the new pagination """
        if (current + self.query_increment) < total_listings:
            self.start_number = 0 if current == 0 else current + 1
            self.end_number = current + self.query_increment
            
        elif (current + self.query_increment) > total_listings and current != total_listings:
            self.start_number = current + 1
            self.end_number = total_listings
        
    def scrape_all_listings(self):
        """ Scrape all the listings (Not detailed scrape). """
        scraped_data = []

        while self.end_number != self.total_listings:
            self.get_pagination(self.total_listings, self.end_number)
            print(f'Scraping data from {self.start_number} to {self.end_number}. {self.total_listings - self.end_number} remaining.')
            query = self.query_parameters.format(self.start_number, self.end_number)
            response = requests.post(self.query_url, headers=self.headers, data=query)
            print(f' status code: {response.status_code}')
            # Beautiful Soup
            soup = BeautifulSoup(response.text, 'lxml')
            listings = soup.find_all(class_='listing-block')
            print(f'listings: {len(listings)}')

            # Packaging the data.
            for ads in listings:
                template = {
                            'district': 'ernakulam',
                            'listing_id': '',
                            'listing_url': '',
                            'detailed_scrape_status': False,
                            'scrape_timestamp': datetime.datetime.now(tz=pytz.utc)
                            }
                
                # Scraping data
                a_tags = ads.find_all('a')
                a_url = a_tags[0].get('href')
                target_url = 'https://www.findhome.com' + a_url
                id = target_url.split('/')[-2].upper()

                # populating template
                # template['district'] = district =====================================> New feature.
                template['listing_id'] = id
                template['listing_url'] = target_url

                scraped_data.append(template)

            # print('sleeping')
            # sleep(10)

        if len(scraped_data) > 1:
            return scraped_data
        elif len(scraped_data) == 1:
            scraped_data = scraped_data[0]
            return scraped_data

if __name__ == "__main__":
    database = mongodb()
    scraper = scraper()

    data = scraper.scrape_all_listings()
    database.write_all_listings(data)