import requests
from bs4 import BeautifulSoup
from get_lenght import save_to_excel

data = []

for i in range(1, 253):
    m_url = f"https://www.turizminsesi.com/haberler/gundem-1-p{i}.htm"
    new_urls = []

    req = requests.get(m_url)
    soup = BeautifulSoup(req.content, 'html.parser')

    if soup.find('div', class_='news_block_view'):
        div = soup.find('div', class_='news_block_view')
        gundem = div.find_all('a', class_='image')
        for p in gundem:
            new_urls.append(p['href'])
            #print(p['href'])

    if soup.find('div', class_='news_box_view'):
        div = soup.find('div', class_='news_box_view')
        news = div.find_all('a', class_='image')
        for new in news:
            new_urls.append(new['href'])
            #print(new['href'])

    for new_url in new_urls:
        response = requests.get(new_url)
        s = BeautifulSoup(response.content, 'html.parser')

        if s.find('h1'):
            title = s.find('h1').get_text(strip=True)
        else:
            title = 'Null'

        if s.find('div', class_='news_detail'):
            content = s.find('div', class_='news_detail').get_text(strip=True)
            data.append({'Title': title, 'Content': content, 'Url': new_url})
            print({'Title': title, 'Content': content, 'Url': new_url})


save_to_excel(data, 'turizminsesi')