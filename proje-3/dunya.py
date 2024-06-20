import requests
from bs4 import BeautifulSoup
from get_lenght import save_to_excel

data = []

for i in range(1,165):#165
    m_url = f"https://www.dunya.com/sektorler/turizm/{i}"
    new_urls = []

    req = requests.get(m_url)
    soup = BeautifulSoup(req.content, 'html.parser')

    if soup.find_all('div', class_='row'):
        rows = soup.find_all('div', class_='row')
        gundem = rows[0].find_all('a')
        for p in gundem:
            new_urls.append(p['href'])
            #print(p['href'])

        #print("----------------------------------------")

        if rows[2].find('div', class_='col-12 col-lg mw0'):
            a = rows[2].find('div', class_='col-12 col-lg mw0')

            nav_section = a.find('nav')
            if nav_section:
                nav_section.extract()  # Nav etiketini kaldır

            tags = a.find_all('a')

            for tag in tags:
                new_urls.append(tag['href'])
                #print(tag['href'])
        #print("///////////////////////////////")

    for new_url in new_urls:
        response = requests.get(new_url)
        s = BeautifulSoup(response.content, 'html.parser')

        if s.find('h1'):
            title = s.find('h1').get_text(strip=True)
        else:
            title = 'Null'

        if s.find('div', class_='content-text'):
            content = s.find('div', class_='content-text').get_text(strip=True)
            data.append({'Title': title, 'Content': content, 'Url': new_url})
            #print({'Title': title, 'Content': content, 'Url': new_url})

save_to_excel(data, 'dunya')


