# -*- coding: utf-8 -*-
"""
Created on Fri Dec 14 10:54:49 2018

@author: Anton
"""

import requests
from bs4 import BeautifulSoup as bs

url = r"https://sp.booking.com/searchresults.ru.html?aid=1535069&label=ruru-edge-ntp-topsites&sid=56850882b961a5e91c2feeb032e73d17&ac_click_type=b&ac_position=0&checkin_month=12&checkin_monthday=8&checkin_year=2018&checkout_month=12&checkout_monthday=9&checkout_year=2018&class_interval=1&dest_id=-3023495&dest_type=city&dtdisc=0&from_sf=1&group_adults=2&group_children=0&iata=TJM&inac=0&index_postcard=0&label_click=undef&no_rooms=1&postcard=0&raw_dest_type=city&room1=A%2CA&sb_price_type=total&search_selected=1&shw_aparth=1&slp_r_match=0&src=index&src_elem=sb&srpvid=80ac25a446fd0079&ss=%D0%A2%D1%8E%D0%BC%D0%B5%D0%BD%D1%8C%2C%20%D0%A2%D1%8E%D0%BC%D0%B5%D0%BD%D1%81%D0%BA%D0%B0%D1%8F%20%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C%2C%20%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F&ss_all=0&ss_raw=%D1%82%D1%8E%D0%BC%D0%B5%D0%BD%D1%8C&ssb=empty&sshis=0&rows=40&offset=40"

while True:
    headers = {'User-Agent': 
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36' 
    } 
    r = requests.get(url, headers=headers) 
    soup = bs(r.content,"html.parser")
    hotelNames=soup.find_all("span", {"class":"sr-hotel__name "})

    for hotelName in hotelNames: 
            print(hotelName.get_text().strip())

    nextPage = soup.find("a", title="Next page")
    if nextPage !=None:
        url ="https://www.booking.com/" + nextPage.attrs["href"]
        print("Обработка следующей страницы.....")
    else:
        break