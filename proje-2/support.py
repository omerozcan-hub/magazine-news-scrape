from random import choice

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import psycopg2
import validators
import json

# import config infos
file = open('config.json', 'r')
config = json.load(file)
file.close()


# support functions

def start_scrape(year, month, part):
    urls_of_webarchive_days = scrape_webarchive_scan_days_for_half_month(year, month, part)

    print(len(urls_of_webarchive_days), ' gün bağlantısı mevcut.   ---1/4--- start scrape')

    return urls_of_webarchive_days


def collect_all_urls_of_news(urls_of_days):
    urls = []
    count = 0
    if urls_of_days:
        for url in urls_of_days:
            print(url)
            links = scrape_webarchive_new_links_on_a_day(url)
            if links:
                urls.extend(links)
            count += 1
    print(len(urls), ' adet haber bağlantısı mevcut.   ---2/4--- collect all urls of news')

    return urls


def scrape_new(links):
    all_news_data = []
    news_count = 0

    for link in links:
        if not validators.url(link):
            print(f"{link} geçersiz bir URL. Atlanıyor.")
            continue
        try:
            req1 = requests.get(link)
            req1.raise_for_status()  # HTTP hatalarını tespit etmek için eklenmiştir.
        except requests.exceptions.RequestException as e:
            print(f"{link} yüklenemedi: {e}")
            continue
        soup1 = BeautifulSoup(req1.text, 'html.parser')

        title = None
        content = None

        if soup1.find('h1', class_='rhd-article-title') and soup1.find('div',
                                                                       class_='gallery-main-container news-detail__body'):
            title = soup1.find('h1', class_='rhd-article-title').get_text(strip=True)

            news_texts = ""
            for div in soup1.find_all('div', class_='text-container'):
                news_texts = news_texts + div.get_text(strip=True) + ' '
            content = news_texts

        elif soup1.find('h1', class_='nd-article__title news-detail__info__title') and soup1.find('div',
                                                                                                  class_='nd-article__content news-detail__body'):
            title = soup1.find('h1', class_='nd-article__title news-detail__info__title').get_text(strip=True)
            content = soup1.find('div', class_='nd-article__content news-detail__body').get_text(strip=True)

        if title is None or content is None:
            print(f"{link} için başlık veya içerik bulunamadı.")
            continue

        all_news_data.append({'Title': title, 'Content': content, 'Url': link})
        news_count += 1
        print(news_count)

    print(len(all_news_data), ' adet haber içeriği mevcut. 3/4- scrape new')
    return all_news_data


def save_to_excel(data):
    if data:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Geçerli tarih ve saat bilgisini al
        filename = f"posta_{timestamp}.xlsx"  # Dosya ismini oluştur
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        print(f"Magazin haberleri başarıyla '{filename}' dosyasına kaydedildi.")
        print(len(data), ' adet haber içeriği kaydedildi. 4/4- save to excel')
    else:
        print("Hiçbir haber bulunamadı.")


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
                    "INSERT INTO news (title, content, url) VALUES (%s, %s, %s)",
                    (title, content, url)
                )

            connection.commit()
            print("Magazin haberleri başarıyla PostgreSQL veritabanına kaydedildi.")
            print(len(data), ' adet haber içeriği kaydedildi. 4/4- save to db')
        except (Exception, psycopg2.Error) as error:
            print("Veritabanına kaydetme hatası:", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Veritabanı bağlantısı kapandı.")
    else:
        print("Hiçbir haber bulunamadı.")


# ----    other   ------

def scrape_webarchive_new_links_on_a_day(url):
    links = []

    req = requests.get(url, timeout=(360))
    soup = BeautifulSoup(req.text, 'html.parser')

    if soup.find_all("div", class_="newsbox"):
        # 2019, 2020, 2021
        boxs = soup.find_all("div", class_="newsbox")

        for box in boxs:
            url = box.find('div', class_='newsbox__text').find('a')['href']
            links.append(url)

    elif soup.find_all("div", class_="main-card"):
        # 2022, 2023, 2024
        cards = soup.find_all('div', class_='main-card')

        for card in cards:
            link = card.find('a')['href']
            links.append(link)

    elif soup.find_all('div', class_='box small'):
        # 2017, 2018
        # normal cars
        boxes = soup.find_all('div', class_='box small')

        for box in boxes:
            url = box.find('a')['href']
            links.append(url)

        if soup.find('div', class_='item'):
            slider_items = soup.find_all('div', class_='item')
            for item in slider_items:
                url = item.find('a')['href']
                links.append(url)

    elif soup.find_all('div', class_="listNewsContainerDiv"):
        # 2010, 2011, 2012, 2013, 2014, 2015, 2016
        if soup.find('div', class_='list3'):
            list1 = soup.find('div', class_='list3')
            list_tags = list1.find_all('a')

            for tag in list_tags:
                url = tag['href']
                links.append(url)

        if soup.find('div', class_='list2'):
            divs = soup.find_all('div', class_='listNewsContainerDiv')
            for div in divs:
                url = div.find('a')['href']
                links.append(url)

        if soup.find('div', class_='mList'):
            main_div = soup.find('div', class_='mList')
            lis = main_div.find_all('li')
            for li in lis:
                url = li.find('a')['href']
                links.append(url)

        if soup.find('div', class_='sManset'):
            main_div = soup.find('div', class_='sManset')
            lis = main_div.find_all('li')
            for li in lis:
                url = li.find('a')['href']
                links.append(url)
    else:
        print("haber card/box'lari bulunamadi")
        return None

    links = fix_url(links)
    return links


def fix_url(links):
    urls = []

    if not links:
        print("Bağlantı listesi boş.")
        return urls

    if validators.url(fix_url_v1(links[1])):
        for link in links:
            urls.append(fix_url_v1(link))
    elif validators.url(fix_url_v2(links[1])):
        for link in links:
            urls.append(fix_url_v2(link))
    elif validators.url(fix_url_v3(links[1])):
        for link in links:
            urls.append(fix_url_v3(link))
    else:
        print("fix url methodları yetersiz kaldı.")

    return urls


def fix_url_v1(url):
    splitted_url = url.split('www.posta.com')[-1]
    url = 'https://www.posta.com' + splitted_url

    return url


def fix_url_v2(url):
    splitted_url = url.split('www.posta.com')[-1]
    url = 'www.posta.com' + splitted_url

    return url


def fix_url_v3(url):
    splitted_url = url.split('http://www.posta.com')[-1]
    url = 'https://www.posta.com' + splitted_url

    return url


def scrape_webarchive_scan_days_for_a_year(year):
    urls = []
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        formatted_date = current_date.strftime('%Y%m%d')

        url = f'https://web.archive.org/web/{formatted_date}/https://www.posta.com.tr/magazin/'

        urls.append(url)

        current_date += timedelta(days=1)

    return urls


def scrape_webarchive_scan_days_for_a_month(year, month):
    urls = []
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    # Tarih aralığında döngü
    current_date = start_date
    while current_date <= end_date:
        # Tarih biçimini ayarla
        formatted_date = current_date.strftime('%Y%m%d')

        # URL oluştur
        url = f'https://web.archive.org/web/{formatted_date}/https://www.posta.com.tr/magazin/'
        urls.append(url)

        current_date += timedelta(days=1)
    return urls


def scrape_webarchive_scan_days_for_half_month(year, month, part):
    urls = []

    start_date = datetime(year, month, 1)

    if part == 1:
        end_date = datetime(year, month, 15)
    elif part == 2:
        start_date = datetime(year, month, 16)
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)

    current_date = start_date
    while current_date <= end_date:
        formatted_date = current_date.strftime('%Y%m%d')
        url = f'https://web.archive.org/web/{formatted_date}/https://www.posta.com.tr/magazin/'
        urls.append(url)
        current_date += timedelta(days=1)

    return urls


def remove_duplicates():
    try:
        connection = psycopg2.connect(
            user=config['database']['username'],
            password=config['database']['password'],
            host=config['database']['host'],
            port=config['database']['port'],
            database=config['database']['database']
        )
        cursor = connection.cursor()

        cursor.execute("CREATE TABLE new_table AS SELECT DISTINCT * FROM news;")
        cursor.execute("DROP TABLE news;")
        cursor.execute("ALTER TABLE new_table RENAME TO news;")

    except (Exception, psycopg2.Error) as error:
        print("Veritabanı hatası:", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Veritabanı bağlantısı kapandı.")
