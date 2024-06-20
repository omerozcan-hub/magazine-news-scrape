import requests
from bs4 import BeautifulSoup
from get_lenght import save_to_excel

data = []
count = 0
new_urls = []

for i in range(1,332):
    m_url = f"https://search.ensonhaber.com/arama/turizm&page={i}"

    response = requests.get(m_url)
    json_data = response.json()

    hits = json_data.get('hits', [])

    for hit in hits:
        # Her bir haberin detaylarına erişiyoruz
        document = hit.get('document', {})
        title = document.get('title', '')
        new_url = document.get('url', '')

        if new_url.startswith('/'):
            new_url = 'https://www.ensonhaber.com' + new_url
            new_urls.append(new_url)
            count+=1
            print(count)

    for u in new_urls:
        req = requests.get(new_url)
        soup = BeautifulSoup(req.text, 'html.parser')

        if soup.find('div', class_='article-body'):
            content = soup.find('div', class_='article-body').get_text(strip=True)
            data.append({'Title': title, 'Content': content, 'Url': new_url})
            #print({'Title': title, 'Content': content, 'Url': new_url})

save_to_excel(data, 'ensonhaber')