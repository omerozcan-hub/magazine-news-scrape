from random import choice

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import psycopg2
# support functions

def start_scrape(year, month, part):

    urls_of_webarchive_days = scrape_webarchive_scan_days_for_half_month(year, month, part)

    print(len(urls_of_webarchive_days),' gün bağlantısı mevcut.   ---1/4--- start scrape')

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
        req1 = requests.get(link)
        if req1.status_code != 200:
            print(f"{link} yüklenemedi.")
            continue
        soup1 = BeautifulSoup(req1.text, 'html.parser')

        title = None
        content = None

        if scrape_type_1_check(soup1):
            title = soup1.find('h1', class_='rhd-article-title').get_text(strip=True)

            news_texts = []
            for div in soup1.find_all('div', class_='text-container'):
                news_text = div.get_text(strip=True) + ' '
                news_texts.append(news_text)

            content = news_texts

            #content = soup1.find('div', class_='text-container ').get_text(strip=True)

        elif scrape_type_2_check(soup1):
            title = soup1.find('h1', class_='nd-article__title news-detail__info__title').get_text(strip=True)
            content = soup1.find('div', class_='nd-article__content news-detail__body').get_text(strip=True)

        elif soup1.find('h1', class_='nd-article__title news-detail__info__title'):
            title = soup1.find('h1', class_='nd-article__title news-detail__info__title')
            content = soup1.find('div', class_=' nd-content-column')

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
    else:
        print("Hiçbir haber bulunamadı.")

def save_to_database(data):
    if data:
        try:
            connection = psycopg2.connect(
                user="postgres",
                password="admin",
                host="localhost",
                port="5432",
                database="NaturelLanguageProcessing"
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
        except (Exception, psycopg2.Error) as error:
            print("Veritabanına kaydetme hatası:", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("Veritabanı bağlantısı kapandı.")
    else:
        print("Hiçbir haber bulunamadı.")


#----    other   ------

def scrape_webarchive_new_links_on_a_day(url):
    links = []

    req = requests.get(url, timeout=(30))
    soup = BeautifulSoup(req.text, 'html.parser')


    if soup.find_all("div", class_="newsbox"):
        boxs = soup.find_all("div", class_="newsbox")

        for box in boxs:

            box_url = box.find('div', class_='newsbox__text').find('a')['href']
            url = fix_url(box_url)
            links.append(url)

    elif soup.find_all("div", class_="main-card"):
        cards = soup.find_all('div', class_='main-card')

        for card in cards:
            link = card.find('a')['href']
            link = fix_url(link)
            links.append(link)

    else:
        print("haber car/box'lari bulunamadi")
        return None

    return links

def fix_url(url):
    splitted_url = url.split('https://')[-1]
    url = 'https://' + splitted_url

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

def scrape_type_1_check(soup1):
    if soup1.find('h1', class_='rhd-article-title') and soup1.find('div', class_='gallery-main-container news-detail__body'):
        return True
    else:
        return False

def scrape_type_2_check(soup1):
    if soup1.find('h1', class_='nd-article__title news-detail__info__title') and soup1.find('div', class_='nd-article__content news-detail__body'):
        return True
    else:
        return False

