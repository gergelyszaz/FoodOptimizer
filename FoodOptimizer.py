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
    return [int(i.replace(s,'')) for v in l for i in v if s in i]

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
prices=[int(p.replace(' FT','')) for p in prices]

foods = [foods[i][:16]+str(i) for i in range(0,len(foods))]

kcals=dict((foods[i],kcals[i]) for i in range(0,len(foods))) 
carbs=dict((foods[i],carbs[i]) for i in range(0,len(foods)))
prots=dict((foods[i],prots[i]) for i in range(0,len(foods)))
fats=dict((foods[i],fats[i]) for i in range(0,len(foods)))
prices=dict((foods[i],prices[i]) for i in range(0,len(foods)))

# Solve problem
prob = LpProblem("E-Food problem", LpMaximize)

Lp_vars = LpVariable.dicts("Food",foods,cat='Binary')

prob += lpSum([prots[i]*Lp_vars[i] for i in foods]), "CHEAP AF"

prob += lpSum([kcals[i]*Lp_vars[i] for i in foods]) <= int(config['MAX']['calorie']),"MaxCalorie"
prob += lpSum([carbs[i]*Lp_vars[i] for i in foods]) <= int(config['MAX']['carbs']),"MaxCarbs"
prob += lpSum([prots[i]*Lp_vars[i] for i in foods]) <= int(config['MAX']['protein']),"MaxProtein"
prob += lpSum([fats[i]*Lp_vars[i] for i in foods]) <= int(config['MAX']['fat']),"MaxFat"

prob += lpSum([carbs[i]*Lp_vars[i] for i in foods]) >= int(config['MIN']['carbs']),"MinCarbs"
prob += lpSum([kcals[i]*Lp_vars[i] for i in foods]) >= int(config['MIN']['calorie']),"MinCalorie"
prob += lpSum([prots[i]*Lp_vars[i] for i in foods]) >= int(config['MIN']['protein']),"MinProtein"
prob += lpSum([fats[i]*Lp_vars[i] for i in foods]) >= int(config['MIN']['fat']),"MinFat"



prob.writeLP("EFoodModel.lp")
prob.solve()

print("Status:", LpStatus[prob.status])
print([v.name for v in prob.variables() if  v.varValue>0])

