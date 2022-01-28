import logging
import sys
import pandas
import dfk.auctions.sale.sale_auctions as sales
from summon_ev import get_genetics

def get_it(step=1000, n=7000):
  rpc_server = 'https://api.harmony.one'
  graphql = 'http://graph3.defikingdoms.com/subgraphs/name/defikingdoms/apiv5'

  df = pandas.DataFrame()
#  df = pandas.DataFrame(columns=['id','seller','tokenId','startingPrice','endingPrice','startedAt','duration','winner','open'])
  for i in range(0,n,step):
    auctions = sales.get_open_auctions(graphql, i, step)
    if df.empty:
      df = pandas.DataFrame(auctions)
    else:
      df = df.append(pandas.DataFrame(auctions))
  return df

def main():
  df = get_it()
  tokens = df['tokenId']
  heroes = tokens[tokens['generation']==1]
  for h in heroes:
    genes = get_genetics(h['statGenes'])
    if genes['mainClass']['D'] == genes['mainClass']['R1']:


if __name__ == "__main__":
  main()
