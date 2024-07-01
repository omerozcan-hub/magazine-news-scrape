My goal in this project was to create a Turkish textual data for the natural language processing project I will work on. According to the topic distribution in my team, I took on magazine and tourism news. 

I performed a web scraping process aimed at collecting historical news headlines and content from many local and national news pages. For sites that offer limited historical data, I used and recommend https://wayback-api.archive.org/. If the media organization you target has enough records here, you can pull a good amount of data.

I performed these web scraping operations using python. I used libraries these are Request, BeautifulSoup, psycopg2, Validators. I created a scraper for each web page according to its own html structure. 

I extracted a total of 265 thousand data. You can find tips for your web scraping processes by using these resources. Thanks.
