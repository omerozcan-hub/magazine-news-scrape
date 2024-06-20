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


def scrape_haberglobal():

    for count in range(170, 2199):  # 2199
        data = []
        url = f"https://haberglobal.com.tr/magazin/{count}"

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        if soup.find('div', class_='row mb-20'):
            div = soup.find('div', class_='row mb-20')
            tags = div.find_all('div', class_='col-12')
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
    req2 = requests.get(url)
    soup2 = BeautifulSoup(req2.text, 'html.parser')

    title_element = soup2.find('h1')
    title = title_element.get_text(strip=True)

    content_element = soup2.find('div', class_='content-text')
    if content_element:
        content = content_element.get_text(strip=True)
    else:
        print(f"İçerik bulunamadı: {url}")
        return None

    return {'Title': title, 'Content': content, 'Url': url}


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
                    "INSERT INTO haberglobal (title, content, url) VALUES (%s, %s, %s)",
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


def save_to_excel(data):
    if data:
        filename = "ucackus.xlsx"  # Dosya ismini oluştur
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        print(f"Magazin haberleri başarıyla '{filename}' dosyasına kaydedildi.")
        print(len(data), ' adet haber içeriği kaydedildi. 4/4- save to excel')
    else:
        print("Hiçbir haber bulunamadı.")



scrape_haberglobal()
