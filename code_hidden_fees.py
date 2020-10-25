#!/user/user1/ih2344/.conda/envs/angellist/bin/python

import sys
import requests
import random
import json
import glob
import time
from datetime import datetime, timedelta
from collections import Counter
from w3lib.html import replace_tags
from parsel import Selector
import pandas as pd


class Error(Exception):
    pass


class NoAvailabilityError(Error):
    pass


class MinBookingRequiredError(Error):
    pass


def chunkify(lst,n):
    return [lst[i::n] for i in range(n)]


def get_payload_metadata(sel):
    forms = sel.xpath('//div[@id="rooms-and-rates"]//div[@class="rateplans"]//div[contains(@class,"rateplan")]//form')
    payloads = list()
    for form in forms:
        payload = dict()
        for i in form.xpath(".//input"):
            k = i.xpath("./@name").get()
            payload[k] = i.xpath("./@value").get()
        payloads.append(payload)
    return payloads


def get_term_statements(sel):
    terms_statement = sel.xpath('//div[@id="terms-and-cancellation"]//text()').getall()
    if terms_statement:
        return '\n'.join(terms_statement)
    return None


def get_financial_blob(sel):
    financial_html_blob = sel.xpath('//div[@id="financial-details-wrapper"]').get()
    return replace_tags(financial_html_blob, "\n")


def parse_booking_page(sel):
    data = dict()
    data['hotel_name'] = sel.xpath('//div[@id="booking-details"]//div[@id="hotel-info"]//h3/text()').get()
    data['hotel_address'] = sel.xpath(
        '//div[@id="booking-details"]//div[@id="hotel-info"]//span[@id="hotel-address"]/text()').get()
    data['review_text'] = sel.xpath('//div[@id="booking-details-reviews"]//em[@class="wording"]//text()').get()
    data['review_score'] = sel.xpath('//div[@id="booking-details-reviews"]//em[@class="rating-value"]//text()').get()
    data['room_type'] = sel.xpath('//section[@id="financial-details"]//p[@class="room-type-name"]//text()').get()
    data['total_pay_now'] = sel.xpath('//div[@id="financial-details-total-price"]/text()').get()
    data['man_fee_text'] = sel.xpath(
        '//div[@id="financial-details-mandatory-fee"]//div[contains(@class,"col-description")]//text()').get()
    data['man_fee_value'] = sel.xpath(
        '//div[@id="financial-details-mandatory-fee"]//div[contains(@class,"col-value")]//text()').get()
    data['man_fee_statement'] = sel.xpath('//div[@id="mandatory-fee-items"]//text()').get()
    data['tax_fee_text'] = sel.xpath(
        '//div[@id="taxes-and-fees-row"]//div[contains(@class,"col-description")]//text()').get()
    data['tax_fee_value'] = sel.xpath(
        '//div[@id="taxes-and-fees-row"]//div[contains(@class,"col-value")]//text()').get()
    data['booking_total'] = sel.xpath('//div[@id="financial-details-total-booking"]//text()').get()
    data['term_statement'] = get_term_statements(sel)
    data['financial_text_blob'] = get_financial_blob(sel)
    return data


def select_form_data(payloads, hotel_id):
    with open(f'/NOBACKUP/scratch/ih2344/hotels_com_pl_meta/{hotel_id}.json', "w") as f:
        json.dump(payloads, f)
    for payload in payloads:
        if payload['bookingRequest.items[0].ratePlanConfiguration'] == "REGULAR" and payload[
            'bookingRequest.items[0].businessModel'] == 'MERCHANT':
            return payload
    for payload in payloads:
        if payload['bookingRequest.items[0].ratePlanConfiguration'] == "REGULAR":
            return payload
    for payload in payloads:
        if payload['bookingRequest.items[0].businessModel'] == 'MERCHANT':
            return payload
    raise ValueError("No Suitable Payload found from the given list of payloads")


def generate_url(hotel_id, attempt):
    # generating check-in and check-out dates
    if attempt == 1:
        days_from_today = random.randrange(50, 60)
    else:
        days_from_today = random.randrange(7 + 7 * (3 - attempt), 21 + 7 * (3 - attempt))
    check_in_date = datetime.strftime(datetime.today() + timedelta(days=days_from_today), "%Y-%m-%d")
    check_out_date = datetime.strftime(datetime.today() + timedelta(days=days_from_today + 1), "%Y-%m-%d")
    # generating the query url
    url = f"http://www.hotels.com/{hotel_id}/?q-check-out={check_out_date}&FPQ=2&q-check-in={check_in_date}&WOE=5&WOD=4&q-room-0-children=0&pa=1&tab=description&JHR=1&q-room-0-adults=2&YGF=3&MGT=1&ZSX=0&SYE=3"
    # print(f"-- check in: {check_in_date}", end="\r")
    # print(f"-- check out: {check_out_date}", end="\r")
    return url, check_in_date, check_out_date


def is_sold_out(sel):
    return sel.xpath('string(//li[contains(@class,"sold-out")]//h2)').get()


def parse(hotel_id, list_of_ips):
    print(f"[*] Starting Process for: {hotel_id}")
    # sending request
    with requests.session() as s:
        # setting up the proxy
        ip_ = random.choice(list_of_ips)
        proxies = {'http': f'http://mabelabraham:959f18d8@{ip_}:60099'}
        s.proxies = proxies
        # requesting selection page
        payloads = None
        attempt = 3
        while not payloads and attempt > 0:
            print(f"-- remaining attempt: {attempt}", end="\r")
            url, c_in, c_out = generate_url(hotel_id, attempt)
            resp_selection = s.get(url, timeout=30)
            #             print(f"-- status code selection: {resp_selection.status_code}")
            resp_selection.raise_for_status()
            sel_selection = Selector(resp_selection.text)
            payloads = get_payload_metadata(sel_selection)
            attempt -= 1
        if len(payloads) == 0:
            sold_out_text = is_sold_out(sel_selection)
            if "has no availability" in sold_out_text:
                raise NoAvailabilityError("Not Avialable in 03 attempts!")
            if "book a minimum of" in sold_out_text:
                raise MinBookingRequiredError(sold_out_text)
        # getting all form data, to be analysed to understand the api better
        form_data = select_form_data(payloads, hotel_id)
        # header for booking requests
        header = {
            'Host': 'www.hotels.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Referer': url
        }
        # requesting booking data
        time.sleep(5)
        resp_booking = s.post("https://www.hotels.com/bookingInitialise.do", data=form_data, headers=header,
                              timeout=10)  # proxy
        resp_booking.raise_for_status()
        sel_booking = Selector(resp_booking.text)
        data = parse_booking_page(sel_booking)
        data['check_in'] = c_in
        data['check_out'] = c_out
        print(f"-- Hotel Name: {data['hotel_name']}")
        with open(f'/NOBACKUP/scratch/ih2344/hotels_com_booking/{hotel_id}.json', "w") as f:
            json.dump(data, f)


# reading in hotel ids
with open("hotel_id_new.txt", "r") as f:
    hotel_ids = f.readlines()
hotel_ids = [i.strip() for i in hotel_ids]
already_done = set([i.split('\\')[-1].replace(".json", "") for i in glob.glob("/NOBACKUP/scratch/ih2344/hotels_com_booking/*")])
# already_done = set([i.split('\\')[-1].replace(".json", "") for i in glob.glob("hotels_com_booking\\*")])
with open("min_booking.txt", "r") as f:
    min_booking = set([i.split(" - ")[0].strip() for i in f.readlines()])
with open("no_availability.txt", "r") as f:
    no_availablity = set([i.strip() for i in f.readlines()])

to_skip = already_done.union(min_booking, no_availablity)
hotel_ids = list(set(hotel_ids).difference(to_skip))
hotel_ids = chunkify(hotel_ids, 10)[int(sys.argv[1])]


# reading the proxy list
proxy = pd.read_csv('proxylist.csv')
list_of_ips = list(proxy['ip'])
# scrape
for hotel_id in hotel_ids:
    time.sleep(10)
    try:
        parse(hotel_id, list_of_ips)
    except NoAvailabilityError:
        with open("no_availability.txt", "a") as f:
            f.write(hotel_id + "\n")
    except MinBookingRequiredError as e:
        with open("min_booking.txt", "a") as f:
            f.write(hotel_id + " - " + str(e) + "\n")
    except Exception as e:
        print(e)