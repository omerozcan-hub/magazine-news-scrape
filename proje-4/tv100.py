import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
import openpyxl
import re
import html

Body = []
href = []

for p in range(1, 6):
    url = f'https://www.tv100.com/magazin?sayfa={p}'
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    container = soup.find('main', {'class': 'app-container'})
    ilk3 = soup.find('div', {'class': 'row'})
    ilk = ilk3.find('div', {'class': 'col-12 col-lg mw-0'})
    a = ilk.find('a')
    href.append(a['href'])
    iki = ilk3.find_all('div', {'class': 'col-6 col-lg-12'})
    haberler = container.find_all('div', {'class': 'col-6 col-md-4'})
    haberler1 = container.find_all('div', {'class': 'col-12'})
    for i in iki:
        link = i.find('a')
        href.append(link['href'])
    for h in haberler:
        link = h.find('a')
        href.append(link['href'])
    for j in haberler1:
        link = j.find('a')
        href.append(link['href'])

for link in href:
    req = requests.get(link)
    soup = BeautifulSoup(req.text, 'html.parser')
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        cleaned_script = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', script.string)
        data = json.loads(cleaned_script)
        if 'articleBody' in data:
            article_body = html.unescape(data['articleBody'])
            description = html.unescape(data.get('description', ''))
            body = description + '\n' + article_body
            Body.append({'Body': body})

df = pd.DataFrame(Body)

df.to_excel('tv100.xlsx', index=False, header=False)

