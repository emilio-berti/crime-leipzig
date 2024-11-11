#!/bin/bash
cd ~/crime-leipzig/data
cp crimes.csv old-crimes.csv
wget -q -O crimes.csv "https://docs.google.com/spreadsheets/d/1xU5NEc3wLm4QCF1vj_UiSGd39oF33ht0jUVRK6kSN9U/export?format=csv"
cd ..
python leipzig-map.py
cp figures/points.html ~/emilio-berti.github.io/crime-leipzig/points.html
cp figures/districts.html ~/emilio-berti.github.io/crime-leipzig/districts.html
cd ~/emilio-berti.github.io/
git add crime-leipzig/districts.html
git add crime-leipzig/points.html
git commit -m 'update leipzig crime map'
git push
cd -
