from lxml import html
import requests
import configparser
from pulp import *
import sys
import re

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

###### Scrape data
print('Scraping ' + site['url'])
page = requests.get(site['url'])
tree = html.fromstring(page.content)

data = {}

###### Parse values
foods = tree.xpath(site['food.xpath'])
data['food'] = [f.text.strip() for f in foods if f.text.strip()]

print(data['food'])

for prop in site['properties'].split('|'):
    print(prop)
    xpath = site['{}.xpath'.format(prop)]
    regex = site['{}.regex'.format(prop)]

    print(regex)
    data[prop] = [
        v.group(1) if v else -9999 for v in
        [re.search(regex, info.text) if info.text else '' for info in tree.xpath(xpath)]
    ]

    print(data[prop])

    if(len(data['food']) != len(data[prop])):
        print("The number of {} do not match: {} out of {}".format(
            prop, len(data[prop]), len(data['food'])))
        exit(1)

print(data)


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
