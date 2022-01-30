#!/usr/bin/env python3

import json, pandas, argparse, requests

#URL = 'http://graph3.defikingdoms.com/subgraphs/name/defikingdoms/apiv5/'
#URL = 'https://graph3.defikingdoms.com/subgraphs/name/defikingdoms/apiv5/'
#URL = 'http://graph4.defikingdoms.com/subgraphs/name/defikingdoms/apiv5/'
#URL = 'https://graph4.defikingdoms.com/subgraphs/name/defikingdoms/apiv5/'
#URL = 'http://graph3.defikingdoms.com/subgraphs/name/defikingdoms/apiv5'
#URL = 'https://graph3.defikingdoms.com/subgraphs/name/defikingdoms/apiv5'
#URL = 'http://graph4.defikingdoms.com/subgraphs/name/defikingdoms/apiv5'
URL = 'https://graph4.defikingdoms.com/subgraphs/name/defikingdoms/apiv5'

HERO_FILE = 'gen_data.txt'
def load_data(FILE):
  with open(FILE,'r') as f:
    df = pandas.DataFrame(json.loads(f.read()))
  return df
HEROES = load_data(HERO_FILE)
CLASSES = ['warrior', 'knight', 'archer', 'thief', 'pirate', 'monk', 'wizard', 'priest', 'paladin', 'darkKnight', 'ninja', 'summoner']
PROFESSIONS = ['mining', 'gardening', 'foraging', 'fishing']

def gen1_floor(c, p):
  if p == 'mining' and (c == 'warrior' or c == 'knight'):
    return 250
  if p == 'mining' and (c == 'archer' or c == 'thief'):
    return 200
  if p == 'mining' and (c == 'pirate' or c == 'monk'):
    return 150
  if p == 'mining' and (c == 'wizard' or c == 'priest'):
    return 100
  if p == 'gardening' and (c == 'warrior' or c == 'knight'):
    return 150
  if p == 'gardening' and (c == 'archer' or c == 'thief'):
    return 100
  if p == 'gardening' and (c == 'pirate' or c == 'monk'):
    return 100
  if p == 'gardening' and (c == 'wizard' or c == 'priest'):
    return 200
  if p == 'foraging' and (c == 'warrior' or c == 'knight'):
    return 100
  if p == 'foraging' and (c == 'archer' or c == 'thief'):
    return 100
  if p == 'foraging' and (c == 'pirate' or c == 'monk'):
    return 100
  if p == 'foraging' and (c == 'wizard' or c == 'priest'):
    return 100
  if p == 'fishing' and (c == 'warrior' or c == 'knight'):
    return 100
  if p == 'fishing' and (c == 'archer'):
    return 100
  if p == 'fishing' and (c == 'pirate' or c == 'monk' or c == 'thief'):
    return 100
  if p == 'fishing' and (c == 'wizard' or c == 'priest'):
    return 100
  return 200 # conservative floor price for advanced classes

def get_genetics(statGenes):
  from dfk.hero.utils import utils
  # 1. decode statGenes into main/sub/prof D/R1/R2/R3
  raw_genes = utils.__genesToKai(int(statGenes))
  raw_genes = "".join(raw_genes.split(' '))
  genetics = {'mainClass': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
              'subClass': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
              'profession': {'D': "", 'R1': "", 'R2': "", 'R3': ""}}
  genetics['mainClass']['D']  = utils.parse_class(utils.__kai2dec(raw_genes[3]))
  genetics['mainClass']['R1']  = utils.parse_class(utils.__kai2dec(raw_genes[2]))
  genetics['mainClass']['R2']  = utils.parse_class(utils.__kai2dec(raw_genes[1]))
  genetics['mainClass']['R3']  = utils.parse_class(utils.__kai2dec(raw_genes[0]))
  genetics['subClass']['D']  = utils.parse_class(utils.__kai2dec(raw_genes[7]))
  genetics['subClass']['R1']  = utils.parse_class(utils.__kai2dec(raw_genes[6]))
  genetics['subClass']['R2']  = utils.parse_class(utils.__kai2dec(raw_genes[5]))
  genetics['subClass']['R3']  = utils.parse_class(utils.__kai2dec(raw_genes[4]))
  genetics['profession']['D']  = utils.parse_profession(utils.__kai2dec(raw_genes[11]))
  genetics['profession']['R1']  = utils.parse_profession(utils.__kai2dec(raw_genes[10]))
  genetics['profession']['R2']  = utils.parse_profession(utils.__kai2dec(raw_genes[9]))
  genetics['profession']['R3']  = utils.parse_profession(utils.__kai2dec(raw_genes[8]))
  return genetics

def get_stuff(d, r):
  for k in d:
    if k == 'D':
      r[d[k]] += 0.5 * 0.75
    elif k == 'R1':
      r[d[k]] += 0.5 * 0.20
    elif k == 'R2':
      r[d[k]] += 0.5 * 0.04
    elif k == 'R3':
      r[d[k]] += 0.5 * 0.01
  return r

def advanced(class1, class2):
  if sorted([class1, class2]) == sorted(['warrior', 'knight']):
    return 'paladin'
  if sorted([class1, class2]) == sorted(['pirate', 'monk']):
    return 'ninja'
  if sorted([class1, class2]) == sorted(['archer', 'thief']):
    return 'darkKnight'
  if sorted([class1, class2]) == sorted(['priest', 'wizard']):
    return 'summoner'
  if sorted([class1, class2]) == sorted(['paladin', 'darkKnight']):
    return 'dragoon'
  if sorted([class1, class2]) == sorted(['ninja', 'summoner']):
    return 'sage'
  if sorted([class1, class2]) == sorted(['dragoon', 'sage']):
    return 'dreadKnight'
  return None

def get_children(genes1, genes2):
  class_results = {}
  prof_results = {}
  for c in CLASSES:
    class_results[c] = 0
  for p in PROFESSIONS:
    prof_results[p] = 0
  class_results = get_stuff(genes1['mainClass'], class_results)
  class_results = get_stuff(genes2['mainClass'], class_results)
  prof_results = get_stuff(genes1['profession'], prof_results)
  prof_results = get_stuff(genes2['profession'], prof_results)

  for v1 in genes1['mainClass'].values():
    for v2 in genes2['mainClass'].values():
      adv_class = advanced(v1,v2)
      if adv_class and class_results[adv_class] == 0:
        if adv_class == 'dreadKnight':
          class_results[adv_class] += 0.125 * (class_results[v1] + class_results[v2])
          class_results[v1] *= 0.875
          class_results[v2] *= 0.875
        else:
          class_results[adv_class] += 0.25 * (class_results[v1] + class_results[v2])
          class_results[v1] *= 0.75
          class_results[v2] *= 0.75

  results = []
  for c in class_results:
    for p in prof_results:
#      results.append([c, p, gen1_floor(c,p)-60, class_results[c] * prof_results[p]])
      results.append([c, p, class_results[c] * prof_results[p]])

  return results

def query(hero_id):
  QUERY = """query getHeroInfo($ID: ID) {
    hero(id: $ID) {
      id
      generation
      rarity
      statGenes
    }
  }"""
  vars = {'ID': hero_id}
  r = requests.post(URL, json={'query': QUERY, 'variables': vars}).json()['data']['hero']
  return r

def main(hero1_id, hero2_id):
  hero1 = pandas.DataFrame(query(hero1_id))
  hero2 = pandas.DataFrame(query(hero2_id))
  hero1_genes = get_genetics(hero1['statGenes'])
  hero2_genes = get_genetics(hero2['statGenes'])
  data = get_children(hero1_genes, hero2_genes)
#  results = pandas.DataFrame(data, columns = ['mainClass', 'profession', 'value', 'probability'])
  results = pandas.DataFrame(data, columns = ['mainClass', 'profession', 'probability'])
  print(results[results['probability'] != 0].sort_values('probability', ascending=False))
#  print(hero1_id, hero2_id, (results['value'] * results['probability']).sum())

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Matchmaker. Enter hero ID and desired result')
  parser.add_argument('--h1', help='input hero id', required=True)
  parser.add_argument('--h2', help='input hero id', required=True)
  args = vars(parser.parse_args())
  main(args['h1'], args['h2'])
