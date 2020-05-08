import requests
from bs4 import BeautifulSoup as bs
import pymongo
import  re
import json

with open('entities.json', encoding='utf-8') as f:
    templates = json.load(f)

headers = {'accept': '*/*',
           'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 YaBrowser/20.3.0.2220 Yowser/2.5 Safari/537.36'}
db_name = templates['db_name']
coll_name = templates['coll_name']
url = templates['url']
adv_type = templates['adv_type']
API_key = templates['API_key']
default_city = templates['default_city']
connect = templates['connect']


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": API_key, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    if places_found != []:
        most_relevant = places_found[0] 
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    else:
        lon = ""
        lat = ""
    return lon, lat
	
	
def db_format_element(advert):
    doc = {"rooms_number": advert[0],
               "footage": advert[1],
               "flat_floor": advert[2],
               "total_floor": advert[3],
               "price": advert[4],
               "metro": advert[5],
               "address": advert[6],
               "lat": advert[7],
               "Long": advert[8],
               "property_type": advert[9]
          }
    return doc
	
	
def avito_parse(base_url, connect, header, db_name, coll_name, adv_type, default_city, api_key):
    conn = pymongo.MongoClient(connect)
    db = conn[db_name]
    coll = db[coll_name]
    coll.delete_many({"property_type": adv_type})
    
    jobs_loc = []
    page_counter = 1
    session = requests.Session()
    request = session.get(base_url, headers=header, cookies={'from-my': 'browser'})
    if request.status_code == 200:
        last_page = False
        while not(last_page):
            soup = bs(request.content, 'html.parser')
            divs = soup.find_all('div', attrs={'class': 'snippet-horizontal item item_table clearfix js-catalog-item-enum item-with-contact js-item-extended'})
            if divs == []:
                print("avito website is down for parsing?")
            for div in divs:
                title = (div.find('a', attrs={'class': 'snippet-link'}).text).split(",")
                rooms_number = title[0].replace("-к квартира","")
                footage = title[1].replace("м²","").strip()
                floor = title[2].strip().replace("эт.","").split("/")
                current_floor = floor[0].strip()
                total_floor = floor[1].strip()
                price = (div.find('span', attrs={'data-marker': 'item-price'}).text).replace("\n ","").replace("₽","").strip()
                address = (div.find('span', attrs={'class': 'item-address__string'}).text).replace("\n ","")
                if address.find("Москва") == -1:
                    address = default_city + ", " + address
                metro = div.find('span', attrs={'class': 'item-address-georeferences-item__content'})
                if metro == None:
                    metro = ''
                else:
                    metro = (div.find('span', attrs={'class': 'item-address-georeferences-item__content'}).text).replace("\n ","")
                long, lat = fetch_coordinates(API_key, address)
                property_type = adv_type 
                advert_db = db_format_element([rooms_number, footage, current_floor, total_floor, price, metro, address, lat, long, property_type])
                coll.insert_one(advert_db)
            nextPage = soup.find("span", {"data-marker": "pagination-button/next"})
            print(str(page_counter) + "%")
            if str(nextPage).find("readonly") == -1 or page_counter <=100:
                page_counter += 1
                base_url = base_url[:-1] + str(page_counter)
                request = session.get(base_url, headers=header)
            else:
                last_page = True
    else:
        print('error')


avito_parse(url, connect, headers, db_name, coll_name, adv_type, default_city, API_key)