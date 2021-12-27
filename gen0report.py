#!/usr/bin/env python3

import json
import pandas

HERO_FILE = 'gen_data.txt'
STATS_FILE = 'hero_stats.json'
def load_data(FILE):
  with open(FILE,'r') as f:
    df = pandas.DataFrame(json.loads(f.read()))
  return df
HEROES = load_data(HERO_FILE)
STATS = load_data(STATS_FILE)

def adv_prof_match(c, p):
  if p == 'mining':
    if c == 'knight' or c == 'warrior' or c == 'archer' or c == 'thief' or c == 'paladin' or c == 'darkKnight':
      return 1
  if p == 'gardening':
    if c == 'wizard' or c == 'priest' or c == 'warrior' or c == 'knight' or c == 'summoner' or c == 'ninja':
      return 1
  if p == 'foraging':
    if c == 'archer' or c == 'thief' or c == 'monk' or c == 'pirate':
      return 1
  if p == 'fishing':
    if c == 'monk' or c == 'pirate' or c == 'priest' or c == 'wizard':
      return 1
  return 0.1

def gene_match(attribute):
  rval = 0.75 # * (attribute['D'] == attribute['D'])
  rval += 0.20 * (attribute['D'] == attribute['R1'])
  rval += 0.04 * (attribute['D'] == attribute['R2'])
  rval += 0.01 * (attribute['D'] == attribute['R3'])
  return rval

def genetic_score(id, statGenes):
  from dfk.hero.utils import utils
  # 1. decode statGenes into main/sub/prof D/R1/R2/R3
  raw_genes = utils.__genesToKai(int(statGenes))
  raw_genes = "".join(raw_genes.split(' '))
  genetics = {'mainClass': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
              'subClass': {'D': "", 'R1': "", 'R2': "", 'R3': ""}, \
              'profession': {'D': "", 'R1': "", 'R2': "", 'R3': ""}}
  genetics['mainClass']['D']  = utils.__kai2dec(raw_genes[3])
  genetics['mainClass']['R1']  = utils.__kai2dec(raw_genes[2])
  genetics['mainClass']['R2']  = utils.__kai2dec(raw_genes[1])
  genetics['mainClass']['R3']  = utils.__kai2dec(raw_genes[0])
  genetics['subClass']['D']  = utils.__kai2dec(raw_genes[7])
  genetics['subClass']['R1']  = utils.__kai2dec(raw_genes[6])
  genetics['subClass']['R2']  = utils.__kai2dec(raw_genes[5])
  genetics['subClass']['R3']  = utils.__kai2dec(raw_genes[4])
  genetics['profession']['D']  = utils.__kai2dec(raw_genes[11])
  genetics['profession']['R1']  = utils.__kai2dec(raw_genes[10])
  genetics['profession']['R2']  = utils.__kai2dec(raw_genes[9])
  genetics['profession']['R3']  = utils.__kai2dec(raw_genes[8])

  # 2. compute wysiwyg probability
  P = {}
  P['mainClass'] = gene_match(genetics['mainClass'])
  P['subClass'] = gene_match(genetics['subClass'])
  P['profession'] = gene_match(genetics['profession'])
  P['mutation'] = adv_prof_match(utils.parse_class(genetics['mainClass']['D']), \
                                 utils.parse_profession(genetics['profession']['D']))

  # 3. intersect the probabilities and add weights
  return 4*P['mainClass'] * P['subClass'] * 2*P['profession'] * P['mutation'] / 8

def alignment_score(mainClass, subClass, profession):
  rval = 0
  if profession == "mining":
    rval = 1.00 * ( STATS[mainClass]['strength'] + STATS[mainClass]['endurance'] ) + \
           0.25 * ( STATS[subClass]['strength'] + STATS[subClass]['endurance'] )
  elif profession == "gardening":
    rval = 1.00 * ( STATS[mainClass]['wisdom'] + STATS[mainClass]['vitality'] ) + \
           0.25 * ( STATS[subClass]['wisdom'] + STATS[subClass]['vitality'] )
  elif profession == "foraging":
    rval = 1.00 * ( STATS[mainClass]['dexterity'] + STATS[mainClass]['intelligence'] ) + \
           0.25 * ( STATS[subClass]['dexterity'] + STATS[subClass]['intelligence'] )
  elif profession == "fishing":
    rval = 1.00 * ( STATS[mainClass]['agility'] + STATS[mainClass]['luck'] ) + \
           0.25 * ( STATS[subClass]['agility'] + STATS[subClass]['luck'] )
  else:
    rval = 0
  return rval / 200

def total_score(A, G, R):
  return A * G * R

def main():
  gen0 = HEROES[HEROES['generation']==0]
  # 1. check class / profession leveling alignment
  gen0['alignment_score'] = gen0.apply(lambda x: alignment_score(x.mainClass, x.subClass, x.profession), axis=1)
  # 2. check class / profession genetic alignment
  gen0['genetic_score'] = gen0.apply(lambda x: genetic_score(x.numberId, x.statGenes), axis=1)
  # 3. get a total score and apply a rarity bonus
  gen0['total_score'] = gen0.apply(lambda x: total_score(x.alignment_score, x.genetic_score, x.rarity), axis=1)
  # 4. format rarity a bit better
  from dfk.hero.utils import utils
  gen0['rarity'] = gen0.apply(lambda x: utils.parse_rarity(x.rarity), axis=1)
  gen0write = gen0[['id', 'total_score', 'alignment_score', 'genetic_score', 'mainClass', 'subClass', 'profession', 'rarity']]
  gen0write.to_csv('gen0.csv')

if __name__ == "__main__":
  main()
