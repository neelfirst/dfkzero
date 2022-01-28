#!/bin/bash -e

for i in 556 419 1923 1018 1414 1127 749 74
do
  for j in 419 1923 1018 1414 1127 749 74
  do
    if [ $i -ne $j ]; then
      python3 summon_ev.py --h1 $i --h2 $j
    fi
  done
done
