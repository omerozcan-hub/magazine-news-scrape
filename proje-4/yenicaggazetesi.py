import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
import json

# 342

# import config infos
file = open('../proje-3/config.json', 'r')
config = json.load(file)
file.close()


def main():
    scrape_yenicaggazetesi()


def scrape_yenicaggazetesi():
    data = []
    for count in range(300, 343): #342
        url = f"https://www.yenicaggazetesi.com.tr/magazin-96hk.htm?page={count}"

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        if soup.find('article', class_='swiper-slide'):
            articles = soup.find_all('article', class_='swiper-slide')
            for article in articles:
                article_url = 'https://www.yenicaggazetesi.com.tr'+article.find('a')['href']
                scraped_data = scrape(article_url)
                if scraped_data is not None:  # None dönenler atlanıyor
                    data.append(scraped_data)
        else:
            print('slider bulunamadı!!!!')

        if soup.find('div', class_='post-item'):
            cards = soup.find_all('div', class_='post-item')
            for card in cards:
                card_url = 'https://www.yenicaggazetesi.com.tr' + card.find('a')['href']
                scraped_data = scrape(card_url)
                if scraped_data is not None:  # None dönenler atlanıyor
                    data.append(scraped_data)
        else:
            print('post-items bulunamadı!!!!')

        print(f'{count}. gün tarandı.')
        save_to_database(data)

def scrape(url):
    req2 = requests.get(url)
    soup2 = BeautifulSoup(req2.text, 'html.parser')

    title_elem = soup2.find('h1', class_='content-title')
    title = title_elem.get_text(strip=True)

    content_elem = soup2.find('div', class_='text-content')
    if content_elem:
        content = content_elem.get_text(strip=True)
    else:
        print(f"İçerik bulunamadı: {url}")
        return None

    return {'Title': title, 'Content': content, 'Url': url}


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
                    "INSERT INTO yenicaggazetesi (title, content, url) VALUES (%s, %s, %s)",
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


if __name__ == '__main__':
    main()
