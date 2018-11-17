from lxml import html
import requests
import configparser


config = configparser.ConfigParser()
config.read('config.INI')

######
print('Scraping ' + config['DEFAULT']['url'])
page = requests.get(config['DEFAULT']['url'])
tree = html.fromstring(page.content)

foods = tree.xpath(config['XPATH']['foods'])
prices = tree.xpath(config['XPATH']['prices'])
infos = tree.xpath(config['XPATH']['infos'])

map(str.strip,foods)
map(str.strip,prices)
map(str.strip,infos)

print(foods)
print(prices)
print(infos)