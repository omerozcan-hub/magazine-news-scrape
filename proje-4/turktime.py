
import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
import json



# import config infos
file = open('config.json', 'r')
config = json.load(file)
file.close()


def scrape_turktime():

    for count in range(2, 701):  # 701
        data = []
        url = f"https://www.turktime.com/kategoridevam/magazin/26/{count}"

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        if soup.find_all('a', class_='katdetaybaslik'):
            tags = soup.find_all('a', class_='katdetaybaslik')
            for div in tags:
                div_url = div['href']
                if div_url is not None:  # None dönenler atlanıyor
                    content_data = scrape(div_url)
                    if content_data:
                        data.append(content_data)
        else:
            print('kartlar bulunamadı!!!!')

        print(f'{count}. gün tarandı.')
        save_to_database(data)


def scrape(url):

    if url.startswith("http"):
        return None

    full_url = 'https://www.turktime.com' + url.strip()  # Doğru bir şekilde URL'leri birleştirin
    req2 = requests.get(full_url)

    if req2.status_code == 200:
        soup = BeautifulSoup(req2.content, 'html.parser')

        title_element = soup.find('h1')
        title = title_element.get_text(strip=True)

        content_element = soup.find('span', id='contextual')
        if content_element:
            content = content_element.get_text(strip=True)
        else:
            print(f"İçerik bulunamadı: {full_url}")
            return None

        return {'Title': title, 'Content': content, 'Url': full_url}
    else:
        print(f"Geçersiz URL: {full_url}")
        return None



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
                    "INSERT INTO turktime (title, content, url) VALUES (%s, %s, %s)",
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



scrape_turktime()
