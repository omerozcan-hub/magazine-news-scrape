from get_lenght import get_main_urls, save_to_excel

import requests
from bs4 import BeautifulSoup

main_urls = []
new_urls = []
data = []

def Scrape(href):
    main_urls = get_main_urls(href)

    for main_url in main_urls:
        new_urls.extend(get_new_urls(main_url))

    for new_url in new_urls:
        x = scrape_url(new_url)
        if x['Content'] != 'Null':
            data.append(x)
            #print(x)

    save_to_excel(data, 'antalyakorfez')

def get_new_urls(href):
    urls = []
    req = requests.get(href)

    if req.status_code == 200:
        soup = BeautifulSoup(req.content, "html.parser")

        boxes = soup.find_all("div", class_="card border-0 h-100")

        for box in boxes:
            link = box.find("a")

            if link and "href" in link.attrs:
                page_url = link["href"]
                urls.append(page_url)

        return urls
    else:
        print("Error:", req.status_code)

def scrape_url(href):
    req = requests.get(href)
    soup = BeautifulSoup(req.text, 'html.parser')

    if soup.find('h1'):
        title = soup.find('h1').get_text(strip=True)
    else:
        title = 'Null'

    if soup.find('div', class_='article-text container-padding'):
        content = soup.find('div', class_='article-text container-padding').get_text(strip=True)
    else:
        content = 'Null'

    return {'Title': title, 'Content': content, 'Url': href}


# Main Part
Scrape('https://www.antalyakorfez.com/arsiv/turizm')
