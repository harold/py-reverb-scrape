import requests
import urllib.request
import time
import json
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import pprint
import re
import os

def proc_item(item_div):
    price_str = item_div.select(".price-with-shipping__price__amount")[0].text
    shipping_str = item_div.select(".price-with-shipping__shipping")[0].text
    shipping_num = re.findall(r"[\d\.]+", shipping_str)
    shipping = 0
    price = float(re.findall(r"[\d\.]+", price_str)[0])
    if shipping_num:
        shipping = float(shipping_num[0])
    total_price = price + shipping
    return {"url": item_div.a.get("href"),
            "title": item_div.select(".listing-row-card__title")[0].text,
            "condition": item_div.select(".condition-indicator__label")[0].text,
            "price": price,
            "shipping": shipping,
            "total_price": total_price}

def page_items(url):
    print(f"Scraping: {url}", flush=True)
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    item_divs = soup.select(".listing-row-card")
    next = soup.select(".pagination__page--next")
    next_url = None
    if next:
        next_url = next[0].a["href"]
    return [[proc_item(i) for i in item_divs], next_url]

base_url = "https://reverb.com"

def slug_dataset(slug):
    path = f"/data/{slug}"
    os.makedirs(path, exist_ok=True)
    [items, next_url] = page_items(base_url + f"/p/{slug}/used")
    while next_url:
        [new_items, next_url] = page_items(base_url + next_url)
        items = items + new_items
    data = pd.DataFrame(items)
    t = time.strftime("%Y-%m-%dT%H_%M_%S")
    data.to_csv(f"/data/{slug}/{t}.tsv", sep="\t", index=False)

slug_dataset("boss-dd-500-digital-delay")
slug_dataset("soundcraft-notepad-12fx-small-format-12-input-mixing-console")
slug_dataset("elektron-digitone")
slug_dataset("roland-boutique-series-sh-01a")

# data2 = pd.read_csv("/data/data.tsv", sep="\t")
# pprint.pprint(data2.sort_values("total_price").to_dict("records"))

################################################################################
## Other thoughts...

# x =  "{ "name":"John", "age":30, "city":"New York"}"
# y = json.loads(x)
# print(y["age"])

# data = pd.DataFrame(columns=["a", "b"])
# data = data.append({"a": 1, "b": "first"}, ignore_index=True)
# print(data)
# print(data.dtypes)
# data.to_csv("/data/data.tsv", sep="\t")

# data2 =  pd.read_csv("/data/data.tsv", sep="\t", index_col=0)
# print(data2)
# print(data2.dtypes)
# print(data2.index)
# print(data2.columns)
# print(data2.describe())
# data3 = data2.append({"v": 2, "n": "c"}, ignore_index=True)
# data3.to_csv("/data/data.tsv", sep="\t")

# url = "https://somedomain.com"
# body = {"name": "Maryja"}
# headers = {"content-type": "application/json"}

# r = requests.post(url, data=json.dumps(body), headers=headers)
