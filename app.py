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

def slugs():
    return sorted(os.listdir("/data"))

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

file_time_format = "%Y-%m-%dT%H_%M_%S.tsv"

def scrape_slug(slug):
    base_path = f"/data/{slug}"
    os.makedirs(base_path, exist_ok=True)
    if os.listdir(base_path):
        latest_file = sorted(os.listdir(base_path))[-1]
        latest_file_time = time.strptime(latest_file, file_time_format)
        time_diff = time.mktime(time.gmtime()) - time.mktime(latest_file_time)
        if time_diff < (60 * 60):
            return pd.read_csv(f"/data/{slug}/{latest_file}", sep="\t")

    [items, next_url] = page_items(base_url + f"/p/{slug}/used")
    while next_url:
        [new_items, next_url] = page_items(base_url + next_url)
        items = items + new_items
    data = pd.DataFrame(items)
    t = time.strftime(file_time_format)
    data.to_csv(f"/data/{slug}/{t}", sep="\t", index=False)
    return data

def slug_offers(slug):
    path = f"/data/{slug}"
    dfs = [pd.read_csv(path + "/" + fname, sep="\t") for fname in os.listdir(path)]
    return pd.concat(dfs).drop_duplicates(["url", "total_price"])

def slug_best_deals_by_condition(old_offers, new_offers):
    offers = pd.concat([old_offers, new_offers]).drop_duplicates(["url", "total_price"], keep="last")
    groups = offers.groupby("condition")
    col = "total_price"
    for condition, group_df in groups:
        df = group_df.copy()
        df["total_price_z_score"] = (df[col] - df[col].mean())/df[col].std(ddof=0)
        deal_records = df[df["for_sale"] == True].sort_values("total_price_z_score").to_dict("records")
        if deal_records:
            print(condition)
            pprint.pprint(deal_records[0])
        print("")

for slug in slugs():
    print("========================================", flush=True)
    print(slug)
    print("========================================")
    old_offers = slug_offers(slug)
    new_offers = scrape_slug(slug)
    old_offers["for_sale"] = False
    new_offers["for_sale"] = True
    if not new_offers.empty:
        slug_best_deals_by_condition(old_offers, new_offers)

################################################################################
## Other thoughts...

# pprint.pprint(data.sort_values("total_price").to_dict("records"))

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
