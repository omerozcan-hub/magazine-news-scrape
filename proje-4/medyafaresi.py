import requests
from bs4 import BeautifulSoup
import psycopg2
import json

# import config infos
file = open('config.json', 'r')
config = json.load(file)
file.close()


def scrape_medyafaresi():
    for count in range(5, 3715):  # 3715 sayfa
        data = []
        url = f"https://www.medyafaresi.com/magazin/{count}"

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        if soup.find('div', class_='col-12 col-lg minw-0'):
            div = soup.find('div', class_='col-12 col-lg minw-0')
            tags = div.find_all('div', class_='post-list-item')
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

    content_element = soup2.find('div', class_='post-content')
    if content_element:
        content = content_element.get_text(strip=True)
        content = fix_special_characters(content)
    else:
        print(f"İçerik bulunamadı: {url}")
        return None

    return {'Title': title, 'Content': content, 'Url': url}


# -------------------------------------------
# -------------------------------------------
# -------------------------------------------
def fix_special_characters(text):
    # Özel karakterleri düzelt
    text = text.replace("\\", "").replace("\xa0", " ").replace("\'", "'")
    return text


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
                    "INSERT INTO medyafaresi (title, content, url) VALUES (%s, %s, %s)",
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


scrape_medyafaresi()
