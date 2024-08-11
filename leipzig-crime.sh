#!/bin/bash
cd ~/crime-leipzig/data
cp crimes.csv old-crimes.csv
wget -O crimes.csv "https://docs.google.com/spreadsheets/d/1xU5NEc3wLm4QCF1vj_UiSGd39oF33ht0jUVRK6kSN9U/export?format=csv"
cd ..
source activate crime
python leipzig-map.py
cp figures/map.html ~/emilio-berti.github.io/crime-leipzig/map.html
cd ~/emilio-berti.github.io/
git add crime-leipzig/map.html
git commit -m 'update leipzig crime map'
git push
cd -

