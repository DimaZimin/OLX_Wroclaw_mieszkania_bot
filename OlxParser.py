from bs4 import BeautifulSoup
import requests
import json


class Parser:
    """
    This class is OLX URL parser that accesses the specified url at https://www.olx.pl/
    :arg
    category # sets the searching category: https://www.olx.pl/nieruchomosci/
    subcategory # sets the  searching subcategory: https://www.olx.pl/nieruchomosci/mieszkania/
    city # sets the city of searching ads https://www.olx.pl/nieruchomosci/mieszkania/wynajem/wroclaw/
    rooms='one' # quantity of rooms in a flat ('one' to 'four']
    price_from # price filter
    page:
    """

    _rooms_index = {
        "one": 0, "two": 1, "three": 2, "four": 3
    }

    def __init__(self, file, category='nieruchomosci', subcategory='mieszkania', city='wroclaw',
                 rooms='one', price_from=1, price_to=9999, page='1'):
        self.file = file
        self.page = page
        self.url = 'https://www.olx.pl/'
        self.rooms = f'search[filter_enum_rooms][0]={rooms}'
        self.price_from = f'search[filter_float_price%3Afrom]={price_from}'
        self.price_to = f'search[filter_float_price%3Ato]={price_to}'
        self.url = self.url + f'{category}/' + f'{subcategory}/' + f'wynajem/' + f'{city}/' + f'?' + \
                              f'{self.price_to}' + f'&{self.rooms}' + f'&page={self.page}'

    @staticmethod
    def write_json(data, file):
        """
        writes data to json file
        """
        with open(file, "w") as json_file:
            json.dump(data, json_file, indent=4)

    @staticmethod
    def filter_price(string):
        """
        parses price from html string
        """
        return ''.join(filter(str.isdigit, string))

    def make_ad_list(self):
        """
        scrapes the data from OLX search engine
        :return: list that includes link to an ad (0), its price(1) and id of an ad(2)
        """
        source = requests.get(self.url).text
        soup = BeautifulSoup(source, 'lxml')
        adverts_table = soup.find(id='offers_table')
        adverts = adverts_table.find_all('div', class_='offer-wrapper')
        ads_list = [(ad.a['href'], self.filter_price(ad.find('p', class_='price').text),
                     ad.table['data-id']) for ad in adverts]
        return ads_list

    def ad_bill(self, link):
        """
        Enters each ad link and retrieves amount of a bill(czynsz)
        :param link: link to an ad
        :return: bill amount
        """
        advert_source = requests.get(link).text
        advert_soup = BeautifulSoup(advert_source, 'html5lib')
        advert_detail = advert_soup.find_all('strong', class_='offer-details__value')
        lst = [detail.text for detail in advert_detail]
        try:
            return self.filter_price(lst[-1])
        except IndexError:
            return self.filter_price(lst[0])

    @staticmethod
    def is_olx_link(link):
        if link.split('/')[2] == 'www.olx.pl':
            return True

    def ad_generator(self):
        for advert in ((link[0], (int(link[1]) + int(self.ad_bill(link[0]))), link[2])
                       for link in self.make_ad_list() if self.is_olx_link(link[0])):
            yield advert

    def update_id(self, nrooms: str):
        """
        updates ad IDs in json file. When executing, this compares the actual IDs with a previously recorded IDs in json
        and in case if there are differences, new IDs will be recorded.
        :param nrooms: number of rooms (str)
        """
        last_ad_ids = [ad[2] for ad in self.make_ad_list()]
        with open(self.file, "r+") as json_db:
            data = json.load(json_db)
            rooms = data['rooms']
            old_ads = rooms[self._rooms_index[nrooms]][nrooms][0]['old']
            new_ads = [ID for ID in last_ad_ids if ID not in old_ads]
            rooms[self._rooms_index[nrooms]][nrooms][0]['new'] = new_ads
            old_ads.extend(new_ads)
            self.write_json(data, self.file)

    def get_last_ads(self, nrooms: str):
        with open(self.file, "r+") as json_db:
            data = json.load(json_db)
            rooms = data['rooms']
            new_ads = rooms[self._rooms_index[nrooms]][nrooms][0]['new']
            self.write_json(data, self.file)
            return new_ads

    def clear_oldest_ads(self, nrooms):
        with open(self.file, "r+") as json_db:
            data = json.load(json_db)
            rooms = data['rooms']
            old_ads = rooms[self._rooms_index[nrooms]][nrooms][0]['old']
            if len(old_ads) > 100:
                del old_ads[0:10]
            self.write_json(data, self.file)
