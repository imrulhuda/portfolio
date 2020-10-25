#!/user/user1/ih2344/.conda/envs/angellist/bin/python

import time
import json
import glob
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup


def parse_optional_extras(h_id, optional_extras):
    keys = list()
    vals = list()
    for i in optional_extras.find_all("p"):
        if i.find("strong"):
            keys.append(i.find("strong").get_text())  # what if no bold face?
            vals.append(i.get_text())
    if len(keys) > 0:
        d = dict(zip(keys, vals))
        d['hotel_id'] = h_id
        return d
    return None


def parse_mandatory_fees(h_id, mandatory_fees):
    keys = list()
    vals = list()
    if mandatory_fees.stripped_strings:
        for i in mandatory_fees.stripped_strings:
            if i.startswith("Deposit") and (":" in i):
                keys.append(i.split(":")[0])
                vals.append(i.split(":")[1])
            if i.startswith("Resort fee:"):
                keys.append("Resort fee")
                vals.append(i.split(":")[1])
        d = dict(zip(keys, vals))
        d['hotel_id'] = h_id
        return d
    return None


def parse_vcard(h_id, soup):
    property_desc = soup.find("div", attrs={"class": "property-description"})
    if property_desc:
        d = dict()
        d['hotel_id'] = h_id
        if property_desc.find("h1"): 
            d['hotel_name'] = property_desc.find("h1").get_text()
        if property_desc.find("span", attrs={"class": "star-rating-text"}):
            d['rating'] = property_desc.find("span", attrs={"class": "star-rating-text"}).contents[0]
        if property_desc.find("span", attrs={"class": "property-address"}): 
            d['address'] = property_desc.find("span", attrs={"class": "property-address"}).get_text()
        if property_desc.find("div",attrs={"class": "tagline"}):
            d['tagline'] = property_desc.find("div",attrs={"class": "tagline"}).get_text()
        if property_desc.find("span", attrs={"class":"hotel-coordinates"}):
            loc = [i['content'] for i in property_desc.find("span", attrs={"class":"hotel-coordinates"}).descendants]
            d['location'] = loc
        if soup.find("del", {"class": "old-price"}):
            d['old_price'] = soup.find("del", {"class": "old-price"}).get_text()
        if soup.find("span", {"class": "current-price"}):
            d['current_price'] = soup.find("span", {"class": "current-price"}).get_text()
        return d
    else:
        return None


def parse_factsheet(h_id, soup):
    keys = list()
    vals = list()
    for i in soup.find_all("div", {"class": "fact-sheet-table-row"}):
        if i.find("div", {"class": "fact-sheet-table-header"}):
            keys.append(i.find("div", {"class": "fact-sheet-table-header"}).get_text())
        if i.find_all("li"):
            vals.append([j.get_text() for j in i.find_all("li")])
    if len(keys) > 0:
        d = dict(zip(keys, vals))
        d['hotel_id'] = h_id
        return d
    return None


def parse_review_module(h_id, review_module):
    d1 = dict()
    d1['hotel_id'] = h_id
    if review_module.find("span", {"class": "rating"}):
        d1['hotels_com_rating'] = review_module.find("span", {"class": "rating"}).get_text()
    if review_module.find("span", {"class": "rating-count"}):
        d1['hotels_com_reviewer'] = review_module.find("span", {"class": "rating-count"}).get_text()
    if review_module.find("div", {"class": "ta-logo"}):
        d1['tripadvisor_rating'] = review_module.find("div", {"class": "ta-logo"}).get_text()
    if review_module.find("div", {"class": "ta-total-reviews"}):
        d1['tripadvisor_reviewer'] = review_module.find("div", {"class": "ta-total-reviews"}).contents[0]
    d2 = parse_trip_advisor(review_module)
    if d2:
        d1.update(d2)
    return d1


def parse_trip_advisor(review_module):
    keys = list()
    vals = list()
    for i in review_module.find_all("div", {"class": "review"}):
        if i.find("div", {"class": "category-name"}):
            keys.append(i.find("div", {"class": "category-name"}).get_text())
        if i.find("div", {"class": "score"})['style'].replace("width:", "") and i.find("div", {"class": "text"}):
            vals.append((i.find("div", {"class": "score"})['style'].replace("width:", ""), i.find("div", {"class": "text"}).get_text()))
        else:
            vals.append((None, None))
    if len(keys) > 0:
        d = dict(zip(keys, vals))
        return d
    return None


def find_num_room(h_id, soup):
    for i in soup.find_all("div", attrs={"class":"info-box"}):
        h4 = i.find("h4", string="Hotel size")
        if h4:
            num_rooms = h4.next_sibling.get_text()
            if 'rooms' in num_rooms:
                return h_id, num_rooms
    return h_id, None


def parse_hotel(id_, ip_):
    data = dict()
    url = "http://www.hotels.com/{}/".format(id_)
    proxies = {'http': PROXY_INFO} # Hidden from Github 
    header = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0'}
    r = requests.get(url, proxies=proxies, headers=header)
    print("Status Code:{}".format(r.status_code))
    soup = BeautifulSoup(r.content, features="html.parser")
    # extract sections
    man_fees = soup.find("h3", string="Mandatory fees")
    if man_fees:
        mandatory_fees = man_fees.parent
        data['mandatory_fees'] = parse_mandatory_fees(id_, mandatory_fees)
    opt_ext = soup.find("h3", string="Optional extras")
    if opt_ext:
        optional_extras = opt_ext.parent
        data['optional_extras'] = parse_optional_extras(id_, optional_extras)
    in_hotel = soup.find("h2", string="In the hotel")
    if in_hotel:
        in_the_hotel = in_hotel.parent
        data['in_hotel'] = parse_factsheet(id_, in_the_hotel)
    in_room = soup.find("h2", string="In the room")
    if in_room:
        in_the_room = in_room.parent
        data['in_room'] = parse_factsheet(id_, in_the_room)
    review_module = soup.find("div", attrs={"class": "review-module"})
    if review_module:
        data['review_scores'] = parse_review_module(id_, review_module)
    data['description'] = parse_vcard(id_, soup)
    data['num_rooms'] = find_num_room(id_, soup)
    time.sleep(3)
    with open('/NOBACKUP/scratch/ih2344/hotels_com/{}.json'.format(id_), 'w') as fp:
        json.dump(data, fp)
    with open('completed_so_far.txt', 'a') as f:
        f.write(id_ + '\n')
    print("Done with {}".format(id_))


proxy = pd.read_csv('proxylist.csv')
list_of_ips = list(proxy['ip'])

with open('hotel_list.txt', 'r') as f:
    hotel_ids = ['ho' + i.strip() for i in f.readlines()]

already_done = [i.split('/')[-1].replace(".json", "") for i in glob.glob("/NOBACKUP/scratch/ih2344/hotels_com/*")]

for hotel_id in hotel_ids:
    if hotel_id in already_done:
        continue
    else:
        ip = random.choice(list_of_ips)
        parse_hotel(hotel_id, ip)

