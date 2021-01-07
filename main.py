import os

from bs4 import BeautifulSoup
import requests
import re
from db import database


clear_db = False


def get_row_fluids(url):
    response = requests.request("GET", url)
    kladr_main = response.text

    soup = BeautifulSoup(kladr_main, 'html.parser')
    return soup.body.find("div", {"class": "container-fluid"}).find_all("div", {"class": "row-fluid"}, recursive=False)


def find_row_fluids(row_fluids, d):
    row_fluids_len = len(row_fluids)
    if row_fluids_len <= 3:
        return
    for i in range(2, row_fluids_len - 1, 2):
        define(row_fluids[i], row_fluids[i + 1], d)


def verify(a):
    return not (a.has_attr('style') and 'line-through' in a['style'])


def regions(a, d):
    global db, clear_db
    if len(a) != len(d):
        raise Exception("Тут кол-во должно совпадать")
    begin = 0 if clear_db else db.get_last_region_id()
    for i in range(begin, len(a)):
        region = a[i]
        badge = d[i]
        if verify(region):
            print(f'REGION - {region.getText()}')
            row_fluids = get_row_fluids(region['href'])
            region_id = db.add_region(region.getText(), badge.getText(), region['href'])
            find_row_fluids(row_fluids, ['NULL', region_id, 1])
            db.save_changes()


def cities(a, d):
    settlements(a, d)


def districts(a, d):
    settlements(a, d)


def settlements(a, d):
    global settlement_types, db
    for settlement in a:
        if verify(settlement):
            settlement_type = re.search('[А-Я][^А-Я]+$', settlement.getText()).group(0)
            if settlement_type not in settlement_types:
                settlementType_id = db.add_settlementType(settlement_type)
                settlement_types[settlement_type] = settlementType_id
            else:
                settlementType_id = settlement_types[settlement_type]
            row_fluids = get_row_fluids(settlement['href'])
            if d[2] == 1:
                print(settlement.getText())
            settlement_id = db.add_settlement(settlement.getText(), d[0], d[1], settlementType_id, d[2], settlement['href'])
            find_row_fluids(row_fluids, [settlement_id, 'NULL', d[2] + 1])


def normalize_streets(a, d):
    normalize_a = []
    if d[0] == 'NULL':
        for page in a:
            streets_row_fluids = get_row_fluids(page['href'])[-1]
            normalize_a += streets_row_fluids.find_all("a")
    else:
        normalize_a += a
    streets(normalize_a, d)


def streets(a, d):
    global db
    for street in a:
        if verify(street):
            db.add_street(street.getText(), d[1], d[0], street['href'])


dict_define = {
    "Регионы РФ": lambda a, d: regions(a, d),
    "Города": lambda a, d: cities(a, d),
    "Районы": lambda a, d: districts(a, d),
    "Населенные пункты": lambda a, d: settlements(a, d),
    "Улицы": lambda a, d: normalize_streets(a, d),
}


def define(row_fluid, row_fluid_content, d):
    global dict_define
    title = row_fluid.find('h4').getText().rstrip(':')
    div_pagination = row_fluid_content.find("div", {"class": "pagination"})
    if div_pagination is not None:
        row_fluid_content = div_pagination
    dict_define[title](row_fluid_content.find_all("a"), d)


if clear_db:
    os.remove(f'./{database.name_db}')
db = database()
settlement_types = dict()
url = "https://kladr-rf.ru/"
row_fluids = get_row_fluids(url)
define(row_fluids[1], row_fluids[2], row_fluids[2].find_all("span"))
