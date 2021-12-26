#!/usr/bin/env python3

import json, requests
from time import sleep

# batch query of 100 heroes, statGenes only
BATCH_QUERY = """query getHeroInfo($I: Int) {
  heros(skip: $I, orderBy: numberId) {
    id
    numberId
    generation
    rarity
    mainClass
    subClass
    profession
    statGenes
  }
}"""

FILE = 'gen_data.txt'

URL = 'https://graph2.defikingdoms.com/subgraphs/name/defikingdoms/apiv5'
N_HEROES = 80000 # would be lovely to retrieve this value from the api

# use this function sparingly. this blasts the DFK API, sleep(1) is a keepalive
# load json text, get count, update with new query, save
def main():
  with open(FILE,'r') as f:
    results = json.loads(f.read())
  with open(FILE,'w') as f:
    for i in range(41700, N_HEROES, 100): # we're limited to 100 heroes at a time
      try:
        print(i)
        vars = {'I': i}
        r = requests.post(URL, json={'query': BATCH_QUERY, 'variables': vars}).json()['data']['heros']
        results.extend(r)
        sleep(1)
      except:
        break
    f.write(json.dumps(results))

if __name__ == "__main__":
  main()

