import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_next_page_url(current_url):
    # Mevcut sayfayı al
    response = requests.get(current_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Sonraki sayfa bağlantısını bul
    next_page_link = soup.find('a', {'rel': 'next'})
    if next_page_link:
        next_page_url = next_page_link.get('href')
        return next_page_url
    else:
        return None


def get_length(href):
    count = 0

    # İlk sayfanın URL'si
    current_url = href

    while current_url:
        # Sonraki sayfanın URL'sini al
        next_page_url = get_next_page_url(current_url)
        if next_page_url:
            print("Next page URL:", next_page_url)
            # Bir sonraki sayfaya geç
            current_url = next_page_url
            # İsteğe bağlı olarak biraz bekleyebiliriz
            count += 1
            # time.sleep(2)  # 2 saniye bekleme
        else:
            print("No more pages found.")
            break

        print('Count :  ', count)


def get_main_urls(href):
    urls = []
    count = 0

    current_url = href

    while current_url:
        # Sonraki sayfanın URL'sini al
        next_page_url = get_next_page_url(current_url)
        if next_page_url:
            # print("Next page URL:", next_page_url)
            urls.append(current_url)
            current_url = next_page_url
            count += 1

        else:
            print("No more pages found.")
            break

    print("-----------------------------------------")
    print("Anasayfa url toplama işlemi tamamlandı.")
    print("Bulunan Anasayfa sayısı", count)
    print("-----------------------------------------")
    return urls


def save_to_excel(data, doc_name):
    if data:
        df = pd.DataFrame(data)
        df.to_excel(doc_name+".xlsx", engine='xlsxwriter', index=False)
        print(f"Turizm haberleri başarıyla '{doc_name}' dosyasına kaydedildi.")
        print(len(data), ' adet haber içeriği kaydedildi. - save to excel')
    else:
        print("Hiçbir haber bulunamadı.")
