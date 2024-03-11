from support import *
import time

#scraping posta.com/magazin archive news

def main():
    scan_six_month(2023, 1, 6)


def scan_half_month(year, month, half_part):
    urls_of_webarchive_days = start_scrape(year, month, half_part)

    urls_of_news = collect_all_urls_of_news(urls_of_webarchive_days)

    data = scrape_new(urls_of_news)

    save_to_database(data)

    print('yarım aylık veri çekildi!!!!!')

def scan_a_month(year, month):

    for i in range(2):
        urls_of_webarchive_days = start_scrape(year, month, i+1)

        urls_of_news = collect_all_urls_of_news(urls_of_webarchive_days)

        data = scrape_new(urls_of_news)

        save_to_database(data)
        time.sleep(40)

    print('1 aylık veri çekildi!!!!!')

def scan_six_month(year, start_month, finish_month):
    month = start_month
    for count in range(6):
        if month <= finish_month:
            for i in range(2):
                urls_of_webarchive_days = start_scrape(year, month, i+1)

                urls_of_news = collect_all_urls_of_news(urls_of_webarchive_days)

                data = scrape_new(urls_of_news)

                save_to_database(data)
                time.sleep(120)
        month += 1

    print('6 aylık veri çekildi!!!!!')

if __name__ == "__main__":
    main()
