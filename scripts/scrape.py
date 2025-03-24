from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import pandas as pd
import time

service = Service("/snap/bin/firefox.geckodriver")
driver = webdriver.Firefox(service = service)
driver.get('https://www.polizei.sachsen.de/de/medieninformationen_pdl.htm')
null = input("Click on a month and press Enter to start scraping")

url = driver.current_url
presse = driver.find_element(By.ID, 'presse')
links = presse.find_elements(By.XPATH, './/*[@href]')
for i in range(len(links)):
  # time.sleep(1)
  driver.get(url)
  presse = driver.find_element(By.ID, 'presse')
  links = presse.find_elements(By.XPATH, './/*[@href]')
  link_url = links[i].get_attribute('href')
  driver.get(link_url)
  content = driver.find_element(By.ID, 'content')
  crime = content.find_elements(By.CSS_SELECTOR, 'h3')
  d = [None for _ in range(len(crime))]
  for ind, elem in enumerate(crime, start = 1):
    try:
      info = elem.find_element(By.XPATH, 'following-sibling::p[1]')
      info = info.text.split('\n')
      if 'Ort' in info[0]:
        ort = info[0].replace('Ort: ', '')
        ort = ort.split(', ')
        district = ort[0]
        street = ort[1] if len(ort) == 2 else None
        zeit = info[1].replace('Zeit: ', '')
        date = zeit.split(', ')[0]
        d[ind - 1] = {'date': date, 'district': district, 'street': street, 'crime': elem.text}
    except Exception as e:
      print(f"Error {ind}: {e}")

  d = [x for x in d if x is not None]
  d = pd.DataFrame(d).drop_duplicates()

  target = driver.current_url.split('/')[-1].replace('htm', 'csv')
  d.to_csv(f'data/polizei/{target}', index = False)

driver.quit()
