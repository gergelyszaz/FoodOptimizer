from lxml import html
import requests
import configparser


config = configparser.ConfigParser()
config.read('config.INI')

######
print('Scraping ' + config['DEFAULT']['url'])
page = requests.get(config['DEFAULT']['url'])
tree = html.fromstring(page.content)