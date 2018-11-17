from lxml import html
import requests
import configparser


config = configparser.ConfigParser()
config.read('config.INI')

def clean(l):
    return list(filter(None,map(str.strip,l)))

def getValues(s, l):
    return list(
        map(
            lambda info: 
                list(
                    map(
                        lambda v: v.replace(s,''),
                        filter(
                            lambda value: s in value,
                            info
                        )
                    )
                ),
            l
        )
    )

######
print('Scraping ' + config['DEFAULT']['url'])
page = requests.get(config['DEFAULT']['url'])
tree = html.fromstring(page.content)

foods = tree.xpath(config['XPATH']['foods'])
prices = tree.xpath(config['XPATH']['prices'])
infos = tree.xpath(config['XPATH']['infos'])

foods=clean(foods)
prices=clean(prices)
infos=clean(infos)

infos=list(map(lambda info: list(map(str.strip,info.split(','))),infos))
kcals=getValues(' kcal', infos)
fats=getValues('g zsír',infos)
carbs=getValues('g szénh.',infos)
prots=getValues('g fehérje',infos)

print(len(foods))
print(len(infos))
print(len(prices))
print(foods)
print(prices)
print (fats)
print(kcals)
print(prots)