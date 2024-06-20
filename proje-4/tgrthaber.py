import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
import json

# çekildi
# 342

# import config infos
file = open('config.json', 'r')
config = json.load(file)
file.close()


def scrape_tgrthaber():

    for count in range(33, 477):  # 477
        data = []
        url = f"https://www.tgrthaber.com.tr/magazin?p={count}"

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        if soup.find('div', class_='news-list__content js-elements color-fff mb-3'):

            divs = soup.find('div', class_='news-list__content js-elements color-fff mb-3')
            tags = divs.find_all('a')
            for tag in tags:
                if tag is not None:  # None dönenler atlanıyor
                    url = tag['href']
                    content_data = scrape(url)
                    if content_data:
                        data.append(content_data)
        else:
            print('kartlar bulunamadı!!!!')

        print(f'{count}. gün tarandı.')
        save_to_database(data)


def scrape(url):
    full_url = 'https://www.tgrthaber.com.tr' + url

    req2 = requests.get(full_url)
    soup2 = BeautifulSoup(req2.text, 'html.parser')

    title_element = soup2.find('h1', class_='news-detail__title news-detail__title--main mb-2')
    if title_element:
        title = title_element.get_text(strip=True)
    else:
        print(f"İçerik bulunamadı: {url}")
        return None

    content_element = soup2.find('div', class_='news-detail__content')
    if content_element:
        content = content_element.get_text(strip=True)
    else:
        print(f"İçerik bulunamadı: {url}")
        return None

    return {'Title': title, 'Content': content, 'Url': full_url}


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
                    "INSERT INTO tgrthaber (title, content, url) VALUES (%s, %s, %s)",
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




scrape_tgrthaber()
