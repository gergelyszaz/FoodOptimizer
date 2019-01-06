from lxml import html, etree
import requests
import configparser
from pulp import *
import sys
import re
import json

###### Get configuration

if(len(sys.argv) != 2):
    print('Missing parameter: name of the site to process!')
    exit(1)

config = configparser.ConfigParser()
config.read('config.INI', 'UTF-8')


if(not config.has_section(sys.argv[1])):
    print('No section found for "{}" in config!'.format(sys.argv[1]))
    exit(1)

site = config[sys.argv[1]]

# returns nil if url is not available
def getFoodData(url):
    data = {}
    page = requests.get(url)
    print(page.status_code)
    print(page.text)

    if page.status_code != 200 or not page.text:
        return nil
    tree = html.fromstring(page.text)

    ###### Parse values

    data['full'] = page.content
    data['name'] = tree.xpath(site['food.xpath'])[0]
    print(data['name'])
    data['category'] = data['name'].split(' ', 1)[0]
    print(data['category'])

    # Parse properties
    for prop in site['properties'].split('|'):
        print(prop)
        xpath = site['{}.xpath'.format(prop)]
        regex = site['{}.regex'.format(prop)]
        #print(xpath)
        #print(regex)
        
        data[prop] = [
            v.group(1) if v else -9999 for v in
            [re.search(regex, info.text) if info.text else '' for info in tree.xpath(xpath)]
        ][0]

        print(data[prop])
    
    return tree


def populateDataSet():

    ###### Scrape data
    print('Scraping ' + site['url'])
    #page = requests.get(site['url'])
    #tree = html.fromstring(page.content)
    for date in site['date'].split('|'):
        print(date)
        for category in site['category'].split('|'):
            print(category)
            url = site['food.url'].replace('[category]', category).replace('[date]',date)
            print(url)
            data = getFoodData(url)
            print(data)
        
        
        
    data = {}

    return data

data = populateDataSet()

print(data)
exit(0)

foods = [foods[i][:16]+str(i) for i in range(0, len(foods))]

kcals = dict((foods[i], kcals[i]) for i in range(0, len(foods)))
carbs = dict((foods[i], carbs[i]) for i in range(0, len(foods)))
prots = dict((foods[i], prots[i]) for i in range(0, len(foods)))
fats = dict((foods[i], fats[i]) for i in range(0, len(foods)))
prices = dict((foods[i], prices[i]) for i in range(0, len(foods)))

# Solve problem
prob = LpProblem("E-Food problem", LpMaximize)

Lp_vars = LpVariable.dicts("Food", foods, cat='Binary')

prob += lpSum([prots[i]*Lp_vars[i] for i in foods]), "CHEAP AF"

prob += lpSum([kcals[i]*Lp_vars[i] for i in foods]
              ) <= int(config['MAX']['calorie']), "MaxCalorie"
prob += lpSum([carbs[i]*Lp_vars[i] for i in foods]
              ) <= int(config['MAX']['carbs']), "MaxCarbs"
prob += lpSum([prots[i]*Lp_vars[i] for i in foods]
              ) <= int(config['MAX']['protein']), "MaxProtein"
prob += lpSum([fats[i]*Lp_vars[i] for i in foods]
              ) <= int(config['MAX']['fat']), "MaxFat"

prob += lpSum([carbs[i]*Lp_vars[i] for i in foods]
              ) >= int(config['MIN']['carbs']), "MinCarbs"
prob += lpSum([kcals[i]*Lp_vars[i] for i in foods]
              ) >= int(config['MIN']['calorie']), "MinCalorie"
prob += lpSum([prots[i]*Lp_vars[i] for i in foods]
              ) >= int(config['MIN']['protein']), "MinProtein"
prob += lpSum([fats[i]*Lp_vars[i] for i in foods]
              ) >= int(config['MIN']['fat']), "MinFat"


prob.writeLP("EFoodModel.lp")
prob.solve()

print("Status:", LpStatus[prob.status])
print([v.name for v in prob.variables() if v.varValue > 0])
