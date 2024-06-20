import requests
from bs4 import BeautifulSoup
from get_lenght import save_to_excel


data = []

for i in range(1, 95):
    new_urls = []
    url = f"https://www.trthaber.com/ajax/getTagNews/{i}/95/"

    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    divs = soup.find_all('div', class_='title')
    for div in divs:
        a = div.find('a')
        new_urls.append(a['href'])

    for new_url in new_urls:
        req2 = requests.get(new_url)
        soup2 = BeautifulSoup(req2.text, 'html.parser')

        if soup2.find('h1'):
            title = soup2.find('h1').get_text(strip=True)
        else:
            title = 'Null'

        if soup2.find('div', class_='news-content').get_text(strip=True):
            content = soup2.find('div', class_='news-content').get_text(strip=True)
        else:
            content = 'Null'

        if content !='Null':
            data.append({'Title': title, 'Content': content, 'Url': new_url})
            print({'Title': title, 'Content': content, 'Url': new_url})


save_to_excel(data, 'trthaber')