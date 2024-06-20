import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_slides(url):
    links = []

    # URL'den sayfa içeriğini çekme
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # slide içeriklerini çekme
        slides = soup.find_all('a', class_='slide')

        for slide in slides:
            news_title = slide['title']
            news_url = 'https://www.haberler.com' + slide['href']
            links.append({'Title': news_title, 'URL': news_url})

        return links
    else:
        print("Sayfa içeriği alınamadı.")
        return None

def scrape_generals(url):
    links = []

    # URL'den sayfa içeriğini çekme
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # slide içeriklerini çekme
        news = soup.find_all('a', class_='boxStyle color-magazine hbBoxMainText')


        for new in news:
            news_title = new['title']
            news_url = 'https://www.haberler.com' + new['href']
            links.append({'Title': news_title, 'URL': news_url})

        return links
    else:
        print("Sayfa içeriği alınamadı.")
        return None

def scrape_magazine_news(url):
    # URL'den sayfa içeriğini çekme
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Haber metninin bulunduğu etiketi bulma
        toContent = soup.find('main', class_='haber_metni')
        contents = toContent.find_all('p')

        new_text = ' '.join(content.get_text(strip=True) for content in contents)

        return new_text
    else:
        print("Sayfa içeriği alınamadı.")
        return None



def main():
    # İstediğiniz magazin sitelerinin URL'lerini buraya ekleyin
    news_data = []
    url = 'https://www.haberler.com/magazin/'

    news_links = scrape_slides(url)
    news_links.extend(scrape_generals(url))

    print(news_links)

    for link in news_links:
        new_content = scrape_magazine_news(link['URL'])
        if new_content:
            news_data.append({'Title':link['Title'], 'Content':new_content})

    # Verileri Excel dosyasına kaydetme
    if news_data:
        df = pd.DataFrame(news_data)
        df.to_excel('magazine_news.xlsx', index=False)
        print("Magazin haberleri başarıyla Excel dosyasına kaydedildi.")
    else:
        print("Hiçbir haber bulunamadı.")


if __name__ == "__main__":
    main()
