import requests
from bs4 import BeautifulSoup
import psycopg2
import json

# import config infos
file = open('config.json', 'r')
config = json.load(file)
file.close()


def scrape_magazinkolik():
    for count in range(577, 880):  # 880 sayfa
        data = []
        url = f"https://www.magazinkolik.com/magazin-haberleri-2hk-p{count}.htm"

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        if soup.find('section', class_='news-category box-02'):
            section = soup.find('section', class_='news-category box-02')
            tags = section.find_all('div', class_='col-sm-12 col-md-6 col-lg-4 mb-sauto')
            for div in tags:
                div_url = div.find('a')['href']
                if div_url is not None:  # None dönenler atlanıyor
                    content_data = scrape(div_url)
                    if content_data:
                        data.append(content_data)
        else:
            print('kartlar bulunamadı!!!!')

        print(f'{count}. gün tarandı.')
        save_to_database(data)


def scrape(url):
    real_url = 'https://www.magazinkolik.com' + url
    req2 = requests.get(real_url)
    soup2 = BeautifulSoup(req2.text, 'html.parser')

    title_elem = soup2.find('h1', class_='content-title')
    title = title_elem.text.strip() if title_elem else None

    content_element = soup2.find('div', class_='text-content')
    if content_element:
        content = content_element.get_text(strip=True)
    else:
        print(f"İçerik bulunamadı: {url}")
        return None

    return {'Title': title, 'Content': content, 'Url': real_url}


# -------------------------------------------
# -------------------------------------------
# -------------------------------------------

def save_to_database(data):
    if data:
        try:
            connection = psycopg2.connect(
                user=config['database']['username'],
                password=config['database']['password'],
                host=config['database']['host'],
                port=config['database']['port'],
                database=config['database']['database']
            )
            cursor = connection.cursor()

            for item in data:
                title = item['Title']
                content = item['Content']
                url = item['Url']

                cursor.execute(
                    "INSERT INTO magazinkolik (title, content, url) VALUES (%s, %s, %s)",
                    (title, content, url)
                )

            connection.commit()
            print("Magazin haberleri başarıyla PostgreSQL veritabanına kaydedildi.")
            print(len(data), ' adet haber içeriği kaydedildi.')
        except (Exception, psycopg2.Error) as error:
            print("Veritabanına kaydetme hatası:", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Veritabanı bağlantısı kapandı.")
    else:
        print("Hiçbir haber bulunamadı.")


scrape_magazinkolik()
