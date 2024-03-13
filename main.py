from support import *
import time

#scraping posta.com/magazin archive news

def main():
    #scan_quantity_month(2023, 3, 10)
    scan_half_month(2016, 7, 1)

def scan_half_month(year, month, half_part):
    urls_of_webarchive_days = start_scrape(year, month, half_part)

    urls_of_news = collect_all_urls_of_news(urls_of_webarchive_days)

    data = scrape_new(urls_of_news)

    #save_to_database(data)

    print('yarım aylık veri çekildi!!!!!')

def scan_a_month(year, month):

    for i in range(2):
        urls_of_webarchive_days = start_scrape(year, month, i+1)

        urls_of_news = collect_all_urls_of_news(urls_of_webarchive_days)

        data = scrape_new(urls_of_news)

        save_to_database(data)

    print('1 aylık veri çekildi!!!!!')

def scan_quantity_month(year, start_month, quantity):
    month = start_month
    finish_month = quantity + start_month - 1
    for count in range(quantity):
        if month <= finish_month:
            for i in range(2):
                urls_of_webarchive_days = start_scrape(year, month, i+1)

                urls_of_news = collect_all_urls_of_news(urls_of_webarchive_days)

                data = scrape_new(urls_of_news)

                save_to_database(data)
        month += 1

    print(quantity, ' aylık veri çekildi!!!!!')

if __name__ == "__main__":
    main()
