from lxml import html
import requests
import configparser


config = configparser.ConfigParser()
config.read('config.INI')

def clean(l):
    return list(filter(None,map(str.strip,l)))

######
print('Scraping ' + config['DEFAULT']['url'])
page = requests.get(config['DEFAULT']['url'])
tree = html.fromstring(page.content)

foods = tree.xpath(config['XPATH']['foods'])
prices = tree.xpath(config['XPATH']['prices'])
infos = tree.xpath(config['XPATH']['infos'])

print(clean(foods))
print(clean(prices))
print(clean(infos))