from lxml import html
import requests
import configparser
from pulp import *


config = configparser.ConfigParser()
config.read('config.INI')

def clean(l):
    return list(filter(None,map(str.strip,l)))

def getValues(s, l):
    # Because I hate you unconditionally
    return [i.replace(s,'') for v in l for i in v if s in i]

###### Scrape data
print('Scraping ' + config['DEFAULT']['url'])
page = requests.get(config['DEFAULT']['url'])
tree = html.fromstring(page.content)

foods = tree.xpath(config['XPATH']['foods'])
prices = tree.xpath(config['XPATH']['prices'])
infos = tree.xpath(config['XPATH']['infos'])

foods=clean(foods)
prices=clean(prices)
infos=clean(infos)

if( len(foods)!=len(infos) and len(foods)!=len(prices)):
    print("The number of input datas do not match!")
    exit(1)

infos=list(map(lambda info: list(map(str.strip,info.split(','))),infos))
kcals=getValues(' kcal', infos)
fats=getValues('g zsír',infos)
carbs=getValues('g szénh.',infos)
prots=getValues('g fehérje',infos)

kcals=[{foods[i]:kcals[i]} for i in range(0,len(foods)) ]
carbs=[{foods[i]:carbs[i]} for i in range(0,len(foods)) ]
prots=[{foods[i]:prots[i]} for i in range(0,len(foods)) ]
fats=[{foods[i]:fats[i]} for i in range(0,len(foods)) ]

print(kcals)
print(fats)
print(carbs)
print(prots)




