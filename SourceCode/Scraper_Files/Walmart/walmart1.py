import pandas as pd
from scrapingbee import ScrapingBeeClient
from http import client
import json
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
import time
import random
import requests
import re
import inspect
import os
import sys
original_sys_path = sys.path.copy()
sys.path = original_sys_path + [os.path.dirname(os.path.dirname(os.path.dirname(__file__)))]
from secret_api_keys import api_keys
sys.path = original_sys_path

scrapingbee_API_key = api_keys.get_scrapingbee_API_key()

CONCURRENCY = 80

def get_products_worker(n,q):
    while True:
        try:
            data = q.get(block=False, timeout=1)
            try:
                print("Getting json...")
                x = get_products(data)
                print("Got json!")

                # put the reviews into the global variable review_result where each thread will have a designated index
                # where it can safely append new revuews
                global product_dictionaries
                for my_dict in x:
                    product_dictionaries[n] += [my_dict]
                print("Great Success")
                q.task_done()
            except Exception as e:
                print(e)
                print("Couldn't get data from", data)
                q.task_done()
        except Exception:
            print("Thread", n, "has joined")
            break

def get_products(url_to_scrape_and_page, retries=0):

    url_to_scrape = url_to_scrape_and_page[0]
    last_page = url_to_scrape_and_page[1]
    
    # printing out the url to see if it works
    print(url_to_scrape)

    MAX_RETRIES = 15
    print("try",retries)
    if retries > MAX_RETRIES:
        return

    try:
        response = requests.get(
            url='https://app.scrapingbee.com/api/v1/',
            params={
                'api_key': scrapingbee_API_key,
                'url': url_to_scrape, 
                'block_resources': 'false',
                'stealth_proxy': 'true',
                'js_scenario': '{"instructions":[{"scroll_y":3500}, {"wait":7000}]}', 
                'country_code':'us'
            },
            timeout=75
        )
    except Exception as e:
        print(e)
        current_line = inspect.currentframe().f_lineno
        print(f"Current line number: {current_line}")
        return get_products(url_to_scrape_and_page, retries+1)
        

    print(response.status_code)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        #print(soup)
        #<div class="mb0 ph0-xl pt0-xl bb b--near-white w-25 pb3-m ph1"><div class="h-100 pb1-xl pr4-xl pv1 ph1" style="contain-intrinsic-size:198px 340px" io-id="4UD5HAIAWYYE"><div role="group" data-item-id="4UD5HAIAWYYE" class="sans-serif mid-gray relative flex flex-column w-100 hide-child-opacity"><a link-identifier="505869109" class="absolute w-100 h-100 z-1 hide-sibling-opacity z-2" target="" href="/ip/Emerson-Quiet-Kool-50-Pint-Smart-Dehumidifier-in-White-with-Built-In-Pump/505869109?filters=%5B%7B%22intent%22%3A%22retailer%22%2C%22values%22%3A%5B%22Walmart%22%5D%7D%5D&amp;athbdg=L1600&amp;from=/search"><span class="w_iUH7">Emerson Quiet Kool 50 Pint Smart Dehumidifier in White with Built-In Pump<!-- --> </span></a><div class="" data-testid="list-view"><div class=""><div class="h2 relative mb2 nowrap"><span class="w_VbBP w_mFV6 w_I_19 w_3oNC w_AAn7 tag-leading-badge absolute" style="background:#E6F1FC;color:#004F9A;font-weight:700;border-radius:4px">Best seller</span></div><div class="relative"><div class="relative overflow-hidden" style="max-width:290px;height:0;padding-bottom:min(392px, 135.17241379310346%);align-self:center;width:min(290px, 100%)"><span><button type="button" class="bg-white pointer pa0 black bn mt1 mr1 pa1 br4 absolute top-0 right-0 z-2" data-automation-id="heart-item" aria-label="Sign in to add to Favorites list, Emerson Quiet Kool 50 Pint Smart Dehumidifier in White with Built-In Pump" style="width: 32px; height: 32px;"><i class="ld ld-Heart  " aria-hidden="true" style="font-size: 1.5rem; vertical-align: -0.25em; padding-top: 1px; width: 1.5rem; height: 1.5rem; box-sizing: content-box;"></i></button></span><img loading="lazy" srcset="https://i5.walmartimages.com/seo/Emerson-Quiet-Kool-50-Pint-Smart-Dehumidifier-in-White-with-Built-In-Pump_7b73fdb8-b42b-48f7-9708-1813e98d9560_1.f7e665a9bf7d3a79ee225b2d88206e10.jpeg?odnHeight=392&amp;odnWidth=290&amp;odnBg=FFFFFF 1x, https://i5.walmartimages.com/seo/Emerson-Quiet-Kool-50-Pint-Smart-Dehumidifier-in-White-with-Built-In-Pump_7b73fdb8-b42b-48f7-9708-1813e98d9560_1.f7e665a9bf7d3a79ee225b2d88206e10.jpeg?odnHeight=784&amp;odnWidth=580&amp;odnBg=FFFFFF 2x" src="https://i5.walmartimages.com/seo/Emerson-Quiet-Kool-50-Pint-Smart-Dehumidifier-in-White-with-Built-In-Pump_7b73fdb8-b42b-48f7-9708-1813e98d9560_1.f7e665a9bf7d3a79ee225b2d88206e10.jpeg?odnHeight=784&amp;odnWidth=580&amp;odnBg=FFFFFF" id="is-0-productImage-9" width="" height="" class="absolute top-0 left-0" data-testid="productTileImage" alt="Emerson Quiet Kool 50 Pint Smart Dehumidifier in White with Built-In Pump"></div><div class="z-2 absolute bottom--1"><div class="relative dib" data-id="4UD5HAIAWYYE"><a class="w_hhLG w_8nsR w_jDfj pointer bn sans-serif b ph2 flex items-center justify-center w-auto shadow-1" href="/ip/Emerson-Quiet-Kool-50-Pint-Smart-Dehumidifier-in-White-with-Built-In-Pump/505869109?filters=%5B%7B%22intent%22%3A%22retailer%22%2C%22values%22%3A%5B%22Walmart%22%5D%7D%5D&amp;athbdg=L1600" data-pcss-hide="true" aria-label="Options - Emerson Quiet Kool 50 Pint Smart Dehumidifier in White with Built-In Pump"><span class="mh2">Options</span></a></div></div></div><div class="mt5 mb0" style="height:24px" data-testid="variant-4UD5HAIAWYYE"><div class="f7 lh-solid tc h1 v-mid"><div aria-hidden="true" aria-labelledby="variants-dynamic-4UD5HAIAWYYE">+11 sizes</div><span class="w_iUH7" id="variants-dynamic-4UD5HAIAWYYE">Available in additional 11 sizes</span></div></div></div><div class=""><div data-automation-id="product-price" class="flex flex-wrap justify-start items-center lh-title mb0"><div class="mr1 mr2-xl b black lh-copy f5 f4-l" aria-hidden="true"><span class="f3 mr1"></span><span class="f6 f5-l" style="vertical-align:0.65ex;margin-right:2px">$</span><span class="f2">300</span><span class="f6 f5-l" style="vertical-align:0.75ex">00</span></div><span class="w_iUH7">current price $300.00</span></div><div class="f7 f6-l black mb2 mb3-l">More options from $259.99</div><span class="w_V_DM" style="-webkit-line-clamp:3;padding-bottom:0em;margin-bottom:-0em"><span data-automation-id="product-title" class="normal dark-gray mb0 mt1 lh-title f6 f5-l lh-copy">Emerson Quiet Kool 50 Pint Smart Dehumidifier in White with Built-In Pump</span></span><div class="flex items-center mt2"><span class="black inline-flex mr1" data-testid="product-ratings" data-value="3.5"><i class="ld ld-StarFill" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i><i class="ld ld-StarFill" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i><i class="ld ld-StarFill" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i><i class="ld ld-StarHalf" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i><i class="ld ld-Star" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i></span><span class="sans-serif gray f7" aria-hidden="true" data-testid="product-reviews" data-value="19">19</span><span class="w_iUH7">3.5 out of 5 Stars. 19 reviews</span></div><div></div><div class="flex items-center mv2"><div class="f7 mr1 blue b lh-copy">Save with</div><img loading="lazy" class="flex" src="//i5.walmartimages.com/dfw/63fd9f59-ac39/29c6759d-7f14-49fa-bd3a-b870eb4fb8fb/v1/wplus-icon-blue.svg" alt="Walmart Plus" height="20" width="auto"></div><div class="mv2" data-automation-id="fulfillment-badge"><div class="f7 flex self-baseline dark-gray"><div>Free shipping, arrives <span class="b">in 3+ days</span></div></div></div></div></div></div></div></div>
        #<div class="mb0 ph0-xl pt0-xl bb b--near-white w-25 pb3-m ph1"><div class="h-100 pb1-xl pr4-xl pv1 ph1" style="contain-intrinsic-size:198px 340px" io-id="58GYR8TI0B8P"><div role="group" data-item-id="58GYR8TI0B8P" class="sans-serif mid-gray relative flex flex-column w-100 hide-child-opacity"><a link-identifier="181683841" class="absolute w-100 h-100 z-1 hide-sibling-opacity z-2" target="" href="/ip/Standard-Ignition-Choke-Thermostat/181683841?filters=%5B%7B%22intent%22%3A%22retailer%22%2C%22values%22%3A%5B%22Walmart%22%5D%7D%5D&amp;from=/search"><span class="w_iUH7">Standard Ignition Choke Thermostat<!-- --> </span></a><div class="" data-testid="list-view"><div class=""><div class="h2 relative mb2 nowrap"></div><div class="relative"><div class="relative overflow-hidden" style="max-width:290px;height:0;padding-bottom:min(392px, 135.17241379310346%);align-self:center;width:min(290px, 100%)"><span><button type="button" class="bg-white pointer pa0 black bn mt1 mr1 pa1 br4 absolute top-0 right-0 z-2" data-automation-id="heart-item" aria-label="Sign in to add to Favorites list, Standard Ignition Choke Thermostat" style="width: 32px; height: 32px;"><i class="ld ld-Heart  " aria-hidden="true" style="font-size: 1.5rem; vertical-align: -0.25em; padding-top: 1px; width: 1.5rem; height: 1.5rem; box-sizing: content-box;"></i></button></span><img loading="eager" src="https://i5.walmartimages.com/asr/eb3c07ad-a040-4402-a023-bfcca8d37969.871683f277bf611bd699b84f9b084904.jpeg?odnHeight=784&amp;odnWidth=580&amp;odnBg=FFFFFF" id="is-0-productImage-3" width="" height="" class="absolute top-0 left-0" data-testid="productTileImage" alt="Standard Ignition Choke Thermostat"></div><div class="z-2 absolute bottom--1"><div class="relative dib" data-id="58GYR8TI0B8P"><button class="w_hhLG w_8nsR w_jDfj pointer bn sans-serif b ph2 flex items-center justify-center w-auto shadow-1" type="button" data-pcss-hide="true" data-automation-id="add-to-cart" aria-label="Add to cart - Standard Ignition Choke Thermostat"><i class="ld ld-Plus" style="font-size:1.5rem;vertical-align:-0.25em;width:1.5rem;height:1.5rem;box-sizing:content-box" title="add to cart"></i><span class="mr2">Add</span></button></div></div></div><div class="mt5 mb0" style="height:24px" data-testid="variant-58GYR8TI0B8P"></div></div><div class=""><div data-automation-id="product-price" class="flex flex-wrap justify-start items-center lh-title mb1"><div class="mr1 mr2-xl b black lh-copy f5 f4-l" aria-hidden="true"><span class="f3 mr1"></span><span class="f6 f5-l" style="vertical-align:0.65ex;margin-right:2px">$</span><span class="f2">12</span><span class="f6 f5-l" style="vertical-align:0.75ex">86</span></div><span class="w_iUH7">current price $12.86</span></div><span class="w_V_DM" style="-webkit-line-clamp:3;padding-bottom:0em;margin-bottom:-0em"><span data-automation-id="product-title" class="normal dark-gray mb0 mt1 lh-title f6 f5-l lh-copy">Standard Ignition Choke Thermostat</span></span><div></div><div class="flex items-center mv2"><div class="f7 mr1 blue b lh-copy">Save with</div><img loading="lazy" class="flex" src="//i5.walmartimages.com/dfw/63fd9f59-ac39/29c6759d-7f14-49fa-bd3a-b870eb4fb8fb/v1/wplus-icon-blue.svg" alt="Walmart Plus" height="20" width="auto"></div><div class="mv2" data-automation-id="fulfillment-badge"><div class="f7 flex self-baseline dark-gray"><div>Shipping, arrives <span class="b">in 3+ days</span></div></div></div></div></div></div></div></div>
        #<div class="mb0 ph0-xl pt0-xl bb b--near-white w-25 pb1-xl pb3-m ph1"><div class="h-100 pb1-xl pr4-xl pv1 ph1" io-id="2NFDDUGHDNS0" style="contain-intrinsic-size: 198px 340px;"><div role="group" data-item-id="2NFDDUGHDNS0" class="sans-serif mid-gray relative flex flex-column w-100 hide-child-opacity"><a link-identifier="546070846" class="absolute w-100 h-100 z-1 hide-sibling-opacity z-2" target="" href="/ip/Genuine-Whirlpool-WPY304475-Cycling-Thermostat/546070846?filters=%5B%7B%22intent%22%3A%22retailer%22%2C%22values%22%3A%5B%22Walmart%22%5D%7D%5D&amp;from=/search"><span class="w_iUH7">Genuine Whirlpool WPY304475 Cycling Thermostat </span></a><div class="" data-testid="list-view"><div class=""><div class="h2 relative mb2 nowrap"></div><div class="relative"><div class="relative overflow-hidden" style="max-width: 290px; height: 0px; padding-bottom: min(392px, 135.172%); align-self: center; width: min(290px, 100%);"><span><button type="button" class="bg-white pointer pa0 black bn mt1 mr1 pa1 br4 absolute top-0 right-0 z-2" data-automation-id="heart-item" aria-label="Sign in to add to Favorites list, Genuine Whirlpool WPY304475 Cycling Thermostat" style="width: 32px; height: 32px;"><i class="ld ld-Heart  " aria-hidden="true" style="font-size: 1.5rem; vertical-align: -0.25em; padding-top: 1px; width: 1.5rem; height: 1.5rem; box-sizing: content-box;"></i></button></span><img loading="lazy" srcset="https://i5.walmartimages.com/asr/8d45a7ed-b621-44f3-8089-bfdd0e3c7f05_1.677e808de14a5f7f3502bd384de2a140.jpeg?odnHeight=392&amp;odnWidth=290&amp;odnBg=FFFFFF 1x, https://i5.walmartimages.com/asr/8d45a7ed-b621-44f3-8089-bfdd0e3c7f05_1.677e808de14a5f7f3502bd384de2a140.jpeg?odnHeight=784&amp;odnWidth=580&amp;odnBg=FFFFFF 2x" src="https://i5.walmartimages.com/asr/8d45a7ed-b621-44f3-8089-bfdd0e3c7f05_1.677e808de14a5f7f3502bd384de2a140.jpeg?odnHeight=784&amp;odnWidth=580&amp;odnBg=FFFFFF" id="is-0-productImage-19" width="" height="" class="absolute top-0 left-0" data-testid="productTileImage" alt="Genuine Whirlpool WPY304475 Cycling Thermostat"></div></div><div class="mt5 mb0" data-testid="variant-2NFDDUGHDNS0" style="height: 24px;"></div></div><div class=""><div data-automation-id="product-price" class="flex flex-wrap justify-start items-center lh-title mb1"><div class="mr1 mr2-xl normal gray lh-copy f5 f4-l" aria-hidden="true"><span class="f3 mr1"></span><span class="f6 f5-l" style="vertical-align: 0.65ex; margin-right: 2px;">$</span><span class="f2">47</span><span class="f6 f5-l" style="vertical-align: 0.75ex;">79</span></div><span class="w_iUH7">current price $47.79</span></div><span class="w_V_DM" style="-webkit-line-clamp: 3; padding-bottom: 0em; margin-bottom: 0em;"><span data-automation-id="product-title" class="normal dark-gray mb0 mt1 lh-title f6 f5-l lh-copy">Genuine Whirlpool WPY304475 Cycling Thermostat</span></span><div></div><div data-automation-id="inventory-status" class="sans-serif gray f7 f6-l  pb2 mt3">Out of stock</div></div></div></div></div></div>
        #<div class="mb0 ph0-xl pt0-xl relative bb b--near-white w-25 pb3-m ph1"><div class="h-100 pr4-xl pb1-xl pv1 ph1" style="contain-intrinsic-size:198px 340px" io-id="4Y4YS0Q3NVS4"><div role="group" data-item-id="4Y4YS0Q3NVS4" class="sans-serif mid-gray relative flex flex-column w-100 hide-child-opacity"><a link-identifier="5033133932" class="w-100 h-100 z-1 hide-sibling-opacity  absolute" target="" href="/ip/Midea-22-Pint-Smart-Access-Dehumidifier-with-App-and-Voice-Control-New-1-500-Sq-ft-Coverage-MAD22S1AWWT/5033133932?filters=%5B%7B%22intent%22%3A%22retailer%22%2C%22values%22%3A%5B%22Walmart%22%5D%7D%5D&amp;classType=REGULAR"><span class="w_iUH7">Midea 22-Pint Smart Access Dehumidifier with App and Voice Control, New, 1,500 Sq. ft. Coverage, MAD22S1AWWT<!-- --> </span></a><div class="" data-testid="list-view"><div class=""><div class=""><div class="h2 relative nowrap mb2"></div><div class="relative"><div class="relative overflow-hidden" style="max-width: 290px; height: 0px; padding-bottom: min(392px, 135.172%); align-self: center; width: min(290px, 100%);"><span><button type="button" class="bg-white pointer pa0 black bn mt1 mr1 pa1 br4 absolute top-0 right-0 z-2" data-automation-id="heart-item" aria-label="Sign in to add to Favorites list, Midea 22-Pint Smart Access Dehumidifier with App and Voice Control, New, 1,500 Sq. ft. Coverage, MAD22S1AWWT" style="width: 32px; height: 32px;"><i class="ld ld-Heart  " aria-hidden="true" style="font-size: 1.5rem; vertical-align: -0.25em; padding-top: 1px; width: 1.5rem; height: 1.5rem; box-sizing: content-box;"></i></button></span><img loading="eager" src="https://i5.walmartimages.com/asr/b24c9359-1536-45a5-a691-3e2956baabe6.688dea740b38051d21235e9e15bb69e5.jpeg?odnHeight=784&amp;odnWidth=580&amp;odnBg=FFFFFF" id="is-0-productImage-0" width="" height="" class="absolute top-0 left-0" data-testid="productTileImage" alt="Midea 22-Pint Smart Access Dehumidifier with App and Voice Control, New, 1,500 Sq. ft. Coverage, MAD22S1AWWT"></div><div class="z-2 absolute bottom--1"><div class="relative dib" data-id="4Y4YS0Q3NVS4"><button class="w_hhLG w_8nsR w_jDfj pointer bn sans-serif b ph2 flex items-center justify-center w-auto shadow-1" type="button" data-pcss-hide="true" data-automation-id="add-to-cart" aria-label="Add to cart - Midea 22-Pint Smart Access Dehumidifier with App and Voice Control, New, 1,500 Sq. ft. Coverage, MAD22S1AWWT"><i class="ld ld-Plus" style="font-size:1.5rem;vertical-align:-0.25em;width:1.5rem;height:1.5rem;box-sizing:content-box" title="add to cart"></i><span class="mr2">Add</span></button></div></div></div><div class="mt5 mb0" data-testid="variant-4Y4YS0Q3NVS4" style="height: 24px;"></div></div><div class=""><div data-automation-id="product-price" class="flex flex-wrap justify-start items-center lh-title mb1"><div class="mr1 mr2-xl b black lh-copy f5 f4-l" aria-hidden="true"><span class="f3"></span><span class="f6 f5-l" style="vertical-align:0.65ex;margin-right:2px">$</span><span class="f2">157</span><span class="f6 f5-l" style="vertical-align:0.75ex">00</span></div><span class="w_iUH7">current price $157.00</span></div><span class="w_V_DM" style="-webkit-line-clamp:3;padding-bottom:0em;margin-bottom:-0em"><span data-automation-id="product-title" class="normal dark-gray mb0 mt1 lh-title f6 f5-l lh-copy">Midea 22-Pint Smart Access Dehumidifier with App and Voice Control, New, 1,500 Sq. ft. Coverage, MAD22S1AWWT</span></span><div class="flex items-center mt2"><span class="black inline-flex mr1" data-testid="product-ratings" data-value="4.5"><i class="ld ld-StarFill" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i><i class="ld ld-StarFill" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i><i class="ld ld-StarFill" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i><i class="ld ld-StarFill" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i><i class="ld ld-StarHalf" style="font-size:12px;vertical-align:-0.175em;width:12px;height:12px;box-sizing:content-box" aria-hidden="true"></i></span><span class="sans-serif gray f7" aria-hidden="true" data-testid="product-reviews" data-value="136">136</span><span class="w_iUH7">4.5 out of 5 Stars. 136 reviews</span></div><div></div><div class="flex items-center mv2"><div class="f7 mr1 blue b lh-copy">Save with</div><img loading="lazy" class="flex" src="//i5.walmartimages.com/dfw/63fd9f59-ac39/29c6759d-7f14-49fa-bd3a-b870eb4fb8fb/v1/wplus-icon-blue.svg" alt="Walmart Plus" height="20" width="auto"></div><div class="mv2" data-automation-id="fulfillment-badge"><div class="f7 flex self-baseline dark-gray"><div>Free shipping, arrives <span class="b">tomorrow</span></div></div></div><div data-automation-id="inventory-status" class="sans-serif gray f7 f6-l  pb2 mt3"></div></div></div></div></div></div></div>
        product_cards = soup.find_all("div", {"class": "mb0 ph0-xl pt0-xl bb b--near-white w-25 pb3-m ph1"}) # changed on 5/13/2024
        product_cards += soup.find_all("div", {"class": "mb0 ph0-xl pt0-xl bb b--near-white w-25 pb1-xl pb3-m ph1"})
        product_cards += soup.find_all("div", {"class": "mb0 ph1 ph0-xl pt0-xl pb3-m bb b--near-white w-25"})
        product_cards += soup.find_all("div", {"class": "mb0 ph1 ph0-xl pt0-xl pb3-m w-50 w-100 bb b--near-white"})
        product_cards += soup.find_all("div", {"class": "mb0 ph0-xl pt0-xl relative bb b--near-white w-25 pb3-m ph1"})
        
        print("-"*200)
        print(product_cards)
        print("bottom"*50)
        #product_cards = soup.find_all("div", {"class": "mb0 ph1 ph0-xl pt0-xl pb3-m bb b--near-white w-25"}) # the class name changes on walmarts website 4/7/23
        #product_cards = soup.find_all("div", {"class": "mb0 ph1 ph0-xl pt0-xl pb3-m w-50 w-100 bb b--near-white"}) # the class name changes on walmarts website 4/7/23

        if product_cards != []:
            if not(last_page):
                print("length", len(product_cards))
                if len(product_cards) >= 40:
                    return soup_parser(soup)
                else:
                    print("by any chance??")
                    return get_products(url_to_scrape_and_page, retries+1)
            else:
                return soup_parser(soup)
        else:
            print("by any chance?????")
            return get_products(url_to_scrape_and_page, retries+1)

            
    
    elif response.status_code == 429:
        print("Too many requests, waiting 5 seconds...")
        time.sleep(5)
        return get_products(url_to_scrape_and_page, retries)

    elif response.status_code != 200:
        print(response.content)
        return get_products(url_to_scrape_and_page, retries+1)
    
    else:
        print("Something went wrong", url_to_scrape_and_page)

def soup_parser(soup):
    
    product_dictionary_list = []
    #mb0 ph1 ph0-xl pt0-xl pb3-m bb b--near-white w-25
    product_cards = []
    product_cards = soup.find_all("div", {"class": "mb0 ph0-xl pt0-xl bb b--near-white w-25 pb3-m ph1"}) # changed on 5/13/2024
    product_cards += soup.find_all("div", {"class": "mb0 ph0-xl pt0-xl bb b--near-white w-25 pb1-xl pb3-m ph1"})
    product_cards += soup.find_all("div", {"class": "mb0 ph1 ph0-xl pt0-xl pb3-m bb b--near-white w-25"})
    product_cards += soup.find_all("div", {"class": "mb0 ph1 ph0-xl pt0-xl pb3-m w-50 w-100 bb b--near-white"})
    product_cards += soup.find_all("div", {"class": "mb0 ph0-xl pt0-xl relative bb b--near-white w-25 pb3-m ph1"})
    product_cards += soup.find_all("div", {"class": "mb0 ph0-xl pt0-xl bb b--near-white w-25 pb3-m ph1"})
    
    
    for product_card in product_cards:
        
        # get model description
        try:
            model_description = product_card.find("span", {"data-automation-id": "product-title"}).text.strip()
            # use re to get rid of non utf-8 characters

        except Exception as e:
            print(e)
            model_description = ""
            #print line number
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")

        
        # get manufacturer
        try:
            manufacturer = model_description.split(" ")[0]
            # use re to get rid of non utf-8 characters

        except Exception as e:
            print(e)
            manufacturer = ""
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
        
        # get price
        try:
            price = product_card.find("div", {"data-automation-id": "product-price"}).find("div").text.strip()
            if "Now" in price:
                price = price.split("Now")[-1]
                
            # put a decimal in the price before the last two digits
            price = price[:-2] + "." + price[-2:]
            
            price = price.replace("$", "")
            
        except Exception as e:
            print(e)
            price = ""
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
        
        # get href
        try:
            href = product_card.find("a")["href"]
            if href[:5] == "https":
                url = href
            else:
                url = "https://www.walmart.com" + href
        except Exception as e:
            print(e)
            url = ""
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
        
        # get product image
        try:
            product_image = product_card.find("img")["src"]
        except Exception as e:
            print(e)
            product_image = ""
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
        
        # get sku
        try:
            sku = url.split("/")[-1]
            if "?" in sku:
                sku = sku.split("?")[0]
            
            if sku == "track":
                sku = url.split("https%")[-1]
                sku = sku.split("%2F")[-1]
                sku = sku.split("%")[0]
                
                
            if sku == "search":
                sku = url.split("/")[-2]
                if "?" in sku:
                    sku = sku.split("?")[0]
        

        except Exception as e:
            print(e)
            sku = ""
            current_line = inspect.currentframe().f_lineno
            print(f"Current line number: {current_line}")
        

        product_dictionary = {
            "Type": appliance_type_global,
            "Store": "Walmart.com",
            "Manufacturer": manufacturer,
            "Model No.": "",
            "Price": price,
            "Model Description": model_description,
            "sku": sku,
            "url": url,
            "product_image": product_image,
            "page_number": 1
        }
        product_dictionary_list += [product_dictionary]
    
    return product_dictionary_list
        

        

product_dictionaries = [[] for i in range(CONCURRENCY)]
start_url_q = Queue(maxsize=0)
appliance_type_global = ""

def main(starting_url, number_of_pages, appliance_type):
    #redeclare global variables
    global product_dictionaries
    product_dictionaries = [[] for i in range(CONCURRENCY)]

    global start_url_q
    start_url_q = Queue(maxsize=0)

    global appliance_type_global
    appliance_type_global = appliance_type

    print("I made it here w1")
    for i in range(number_of_pages):
        last_page = False
        if i + 1 == number_of_pages:
            last_page = True
            
        # the website also seems to like &affinityOverride=default at the end of the url, so were going to 
        # take it out and add it at the end after the page numver
        starting_url = starting_url.replace("&affinityOverride=default", "")

        # added this in so that if it is the first page it will remove the &page= from the url
        # walmart.com doesn't seem to like page=1
        if i == 0:
            start_url_q.put([starting_url.replace("&page=", "") + "&affinityOverride=default", last_page])
        else:
            start_url_q.put([starting_url + str(i+1) + "&affinityOverride=default", last_page])
    
    threads = []
    for i in range(CONCURRENCY):
        threads += [Thread(target=get_products_worker, args=(i, start_url_q))]
    
    for thread in threads:
        thread.start()
        
    print("I made it here w1?")
    
    for thread in threads:
        thread.join()
        
    dataframe_to_export = pd.DataFrame()
    for my_list in product_dictionaries:
        #convery list of dictionaries to pandas dataframe

        filtered_items = filter(lambda x: x is not None, my_list)
        my_list = list(filtered_items)

        dataframe_to_export = dataframe_to_export._append(pd.DataFrame(my_list), ignore_index=True)

    #dataframe_to_export.to_excel("Walmart.com " + appliance_type + " Product List " + str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + ".xlsx")
    
    return dataframe_to_export

if __name__ == "__main__":
    main("https://www.walmart.com/browse/air-conditioners/window-air-conditioners/1072864_133032_1231458_133026_587566?facet=retailer_type%3AWalmart&page=", 4, "WindowAC")



