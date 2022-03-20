#!/usr/bin/env python3

import json, pandas, argparse, requests

URL = 'https://graph4.defikingdoms.com/subgraphs/name/defikingdoms/apiv5'

HERO_FILE = 'gen_data.txt'
def load_data(FILE):
  with open(FILE,'r') as f:
    df = pandas.DataFrame(json.loads(f.read()))
  return df
HEROES = load_data(HERO_FILE)
CLASSES = ['warrior', 'knight', 'archer', 'thief', 'pirate', 'monk', 'wizard', 'priest', 'paladin', 'darkKnight', 'ninja', 'summoner', 'dragoon', 'sage', 'dreadKnight']
PROFESSIONS = ['mining', 'gardening', 'foraging', 'fishing']

def parse_class(x):
  if x == 0:
    return "Basic1"
  if x == 1:
    return "Basic2"
  if x == 2:
    return "Basic3"
  if x == 3:
    return "Basic4"
  if x == 4:
    return "Basic5"
  if x == 5:
    return "Basic6"
  if x == 6:
    return "Basic7"
  if x == 7:
    return "Basic8"
  if x == 16:
    return "Advanced1"
  if x == 17:
    return "Advanced2"
  if x == 18:
    return "Advanced3"
  if x == 19:
    return "Advanced4"
  if x == 24:
    return "Elite1"
  if x == 25:
    return "Elite2"
  if x == 28:
    return "Transcendent1"
  return None

def get_genetics(statGenes):
  from dfk.hero.utils import utils
  # 1. decode statGenes into main/sub/prof D/R1/R2/R3
  raw_genes = utils.__genesToKai(int(statGenes))
  raw_genes = "".join(raw_genes.split(' '))
  genetics = {'mainClass': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
              'subClass': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
              'passive1': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
              'passive2': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
              'active1': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
              'active2': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
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
# active1, active2, passive1, passive2
  genetics['passive1']['D']  = parse_class(utils.__kai2dec(raw_genes[15]))
  genetics['passive1']['R1']  = parse_class(utils.__kai2dec(raw_genes[14]))
  genetics['passive1']['R2']  = parse_class(utils.__kai2dec(raw_genes[13]))
  genetics['passive1']['R3']  = parse_class(utils.__kai2dec(raw_genes[12]))
  genetics['passive2']['D']  = parse_class(utils.__kai2dec(raw_genes[19]))
  genetics['passive2']['R1']  = parse_class(utils.__kai2dec(raw_genes[18]))
  genetics['passive2']['R2']  = parse_class(utils.__kai2dec(raw_genes[17]))
  genetics['passive2']['R3']  = parse_class(utils.__kai2dec(raw_genes[16]))
  genetics['active1']['D']  = parse_class(utils.__kai2dec(raw_genes[23]))
  genetics['active1']['R1']  = parse_class(utils.__kai2dec(raw_genes[22]))
  genetics['active1']['R2']  = parse_class(utils.__kai2dec(raw_genes[21]))
  genetics['active1']['R3']  = parse_class(utils.__kai2dec(raw_genes[20]))
  genetics['active2']['D']  = parse_class(utils.__kai2dec(raw_genes[27]))
  genetics['active2']['R1']  = parse_class(utils.__kai2dec(raw_genes[26]))
  genetics['active2']['R2']  = parse_class(utils.__kai2dec(raw_genes[25]))
  genetics['active2']['R3']  = parse_class(utils.__kai2dec(raw_genes[24]))
  return genetics

def get_stuff(d, r):
  for k in d:
    if k == 'D':
      r[d[k]] += 0.5 * 0.75
    elif k == 'R1':
      r[d[k]] += 0.5 * 0.1875
    elif k == 'R2':
      r[d[k]] += 0.5 * 0.046875
    elif k == 'R3':
      r[d[k]] += 0.5 * 0.015625
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

def adv_skill(skill1, skill2):
  if sorted([skill1, skill2]) == sorted(['Basic1', 'Basic2']):
    return 'Advanced1'
  if sorted([skill1, skill2]) == sorted(['Basic3', 'Basic4']):
    return 'Advanced2'
  if sorted([skill1, skill2]) == sorted(['Basic5', 'Basic6']):
    return 'Advanced3'
  if sorted([skill1, skill2]) == sorted(['Basic7', 'Basic8']):
    return 'Advanced4'
  return None

def get_match_score(genes1, genes2):
  score = 0
  if advanced(genes1['mainClass']['D'], genes2['mainClass']['D']):
    score += 0.75
  if advanced(genes1['mainClass']['R1'], genes2['mainClass']['R1']):
    score += 0.1875
  if advanced(genes1['mainClass']['R2'], genes2['mainClass']['R2']):
    score += 0.046875
  if advanced(genes1['mainClass']['R3'], genes2['mainClass']['R3']):
    score += 0.015625
  score *= 1

  if advanced(genes1['subClass']['D'], genes2['subClass']['D']):
    score += 0.75
  if advanced(genes1['subClass']['R1'], genes2['subClass']['R1']):
    score += 0.1875
  if advanced(genes1['subClass']['R2'], genes2['subClass']['R2']):
    score += 0.046875
  if advanced(genes1['subClass']['R3'], genes2['subClass']['R3']):
    score += 0.015625

  for gene in ['active1', 'active2', 'passive1', 'passive2']:
    if adv_skill(genes1[gene]['D'], genes2[gene]['D']):
      score += 0.75
    if adv_skill(genes1[gene]['R1'], genes2[gene]['R1']):
      score += 0.1875
    if adv_skill(genes1[gene]['R2'], genes2[gene]['R2']):
      score += 0.046875
    if adv_skill(genes1[gene]['R3'], genes2[gene]['R3']):
      score += 0.015625

  return score

'''
def get_match_score(genes1, genes2):
  score = 0
  for v1 in genes1['mainClass'].values():
    for v2 in genes2['mainClass'].values():
      if advanced(v1,v2):
        score += 1

  for gene in ['active1', 'active2', 'passive1', 'passive2']:
    for v1 in genes1[gene].values():
      for v2 in genes2[gene].values():
        if adv_skill(v1,v2):
          score += 1

  return score
'''

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

def main(hero1_id):
  hero1 = pandas.Series(query(hero1_id))
  hero1_genes = get_genetics(hero1['statGenes'])
  data = []
  for i in range(0,len(HEROES)):
    hero2 = HEROES.iloc[i]
    if hero2['generation'] == 0:
      hero2_genes = get_genetics(hero2['statGenes'])
      data.append([hero2['id'], hero2['mainClass'], hero2['profession'], get_match_score(hero1_genes, hero2_genes)])
  results = pandas.DataFrame(data, columns = ['match_id', 'mainClass', 'prof', 'match_score'])
  print(results[results['match_score'] >= 2.5].sort_values('match_id', ascending=True).to_string())

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Matchmaker. Enter hero ID and desired result')
  parser.add_argument('--h1', help='input hero id', required=True)
  args = vars(parser.parse_args())
  main(args['h1'])
