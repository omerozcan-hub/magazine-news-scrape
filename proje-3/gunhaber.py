import requests
from bs4 import BeautifulSoup
from get_lenght import save_to_excel

data = []

for i in range(1, 96):
    m_url = f"https://www.gunhaber.com.tr/kategoridevam/Turizm/209/{i}"
    new_urls = []

    req = requests.get(m_url)
    soup = BeautifulSoup(req.content, 'html.parser')

    if soup.find('table', id='AutoNumber17'):
        table = soup.find('table', id='AutoNumber17')

        tagsA = table.find_all('a', class_='link14rb')
        tagsB = table.find_all('a', class_='link12bn')

        for tag in tagsA:
            new_urls.append('https://www.gunhaber.com.tr'+tag['href'])

        for tag in tagsB:
            new_urls.append('https://www.gunhaber.com.tr'+tag['href'])

    for new_url in new_urls:
        response = requests.get(new_url)
        s = BeautifulSoup(response.content, 'html.parser')

        if s.find('h1'):
            title = s.find('h1').get_text(strip=True)
        else:
            title = 'Null'

        if s.find('span', id='contextual'):
            content = s.find('span', id='contextual').get_text(strip=True)
            data.append({'Title': title, 'Content': content, 'Url': new_url})
            print({'Title': title, 'Content': content, 'Url': new_url})


save_to_excel(data,'gunhaber')