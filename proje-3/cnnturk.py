import requests
from bs4 import BeautifulSoup
from get_lenght import save_to_excel

data = []
new_urls = []
m_url = 'https://www.cnnturk.com/api/lazy/loadmore?containerSize=col-8&url=/turizm&orderBy=StartDate%20desc&paths=&subPath=True&tags=turizm&skip=21&top=10000&contentTypes=Article,NewsVideo,PhotoGallery&customTypes=&viewName=load-mixed-by-date&controlIxName='
count = 0


req = requests.get(m_url)
soup = BeautifulSoup(req.content, 'html.parser')

if soup.find_all('a'):
    a = soup.find_all('a')
    for i in a:
        new_urls.append(f"https://www.cnnturk.com{i['href']}")
        count+=1
        #print(f"https://www.cnnturk.com{i['href']}")


for new_url in new_urls:
    response = requests.get(new_url)
    s = BeautifulSoup(response.content, 'html.parser')
    print(new_url)

    if s.find_all('article'):
        article = s.find_all('article')
    else:
        print('not found',new_url)
        print(s.find('article'))
        #print(s)
        continue


    if article[0].find('h1'):
        title = article[0].find('h1').get_text(strip=True)
    else:
        title = 'Null'


    content = ''
    if article[0].find_all('div', class_='detail-middle'):
        divs = article[0].find_all('div', class_='detail-middle')
        for div in divs:
            content = content + div.get_text(strip=True)

        data.append({'Title': title, 'Content': content, 'Url': new_url})
        #print({'Title': title, 'Content': content, 'Url': new_url})


save_to_excel(data, 'cnnturk')

