from datetime import datetime
import multiprocessing as mp
from multiprocessing import Pool
import requests
import numpy as np
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import time
import random


def extraction_reuters(folder,year,nb_days, days_list):

    """
    Scrapping of reuters data
    :param folder: output folder for storing the articles
    :param year: year for which we want to collect reuters articles
    :param nb_days: maximum number of days we want to collect

    :param days_list: list of days for which we want the articles
    :return:
    """

    # list of agent to fake a browser connection
    user_agent_list = [\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",\
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",\
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",\
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",\
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",\
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",\
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",\
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",\
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36"
       ]

	# file path to store the urls of articles we failed to scrap
    failed_urls = folder + 'failed_urls.txt'

    year_str = str(year)

    start_time = time.time()
    
    day_count = 0
    total = 0

    journal = 'reuters/'

	# the urls of links giving access to every articles of a year have a specific pattern
    year_pattern = '/resources/archive/us/' + year_str
    title = "http://www.reuters.com"

	# the urls of article links have a specific pattern
    article_pattern = 'http://www.reuters.com/article'

    for link_d in days_list:

        if day_count<nb_days:
            # We first get the date from the url and make some transformation to make it easier to read
            date = link_d[22:30]
            date = datetime.strptime(date, '%Y%m%d')
            date = str(date)[:10]
            elapsed_time = time.time() - start_time

            print("-" * 25)
            print('\n scrapping REUTERS for date ; {}\n'.format(date))
            print('total articles scrapped : {} \n'.format(total))
            print('elapsed_time : {}'.format(elapsed_time))

            # Let's create a folder for each scraped day
            
            date_dir = date + '/'


            # We create a new folder for each day only if this folder does not not exist yet
            day_path = os.path.join(folder, date_dir)
            if not os.path.exists(day_path):
                os.makedirs(day_path)

            # In case we would scrap other journals than reuters, inside the day folder we create a new folder for each journal only if this folder does not not exist yet
            journal_dir = os.path.join(day_path, journal)
            if not os.path.exists(journal_dir):
                os.makedirs(journal_dir)

			# full_url is an url that leads to all the articles of a specific day
            full_url = title + link_d

			# We open it and then read the html code with BeautifulSoup
            html_d = urlopen(full_url)
            bs2 = BeautifulSoup(html_d.read())

            day_count += 1
            
			# We get all the links ("a") from the html
            l2 = [x.get('href') for x in bs2.find_all("a") if x.get('href') is not None]
			# We then get only the links leading to a real article. We do not want advertisement or any undesired content in our data.
            article_list = [x for x in l2 if x[:len(article_pattern)] == article_pattern]
 

# !! Most important part of the script !! 
           
			# We loop over all the articles found
            for link_a in article_list:
                
				# We change our headers

                headers = {'User-Agent': random.choice(user_agent_list)}
				
				# Try to make a get requests with the headers. If it fails we had the failed url to the failed_urls file
                try:
                    html_a = requests.get(link_a, timeout=10, headers=headers).text
                except Exception:
                    print('failed url  : {}  date : {}'.format(link_a, date))
                    f = open(failed_urls, 'a')
                    f.write(date + " " + link_a + '\n')
                    f.close()
                    pass
                
				# We make a BS object from the html text ( in html_a ). We will then be able to parse the text
                bsa = BeautifulSoup(html_a)

				# Get the title of the article using the h1 tag. Sometimes there is no h1 tag so we just take the first 80 characters as a title
                try:
                    article_title = bsa('h1')[0].text.replace("/", " ") + ' '
                except Exception:
                    article_title = bsa('p')[0].text[:80]
				
				# We get the text of the article using 'p' tags. 
                article = bsa('p')
				
				# Simple trick to avoid filter out useless text
                article = [tex.text for tex in article if len(tex.text) > 80]

                text = ''.join([x for x in article])
                filename = article_title[:50] + '.txt'
                article_text = article_title + text

                file_path = os.path.join(journal_dir, filename)
                if not os.path.exists(file_path):
                    f = open(file_path, 'w')
                    f.write(article_text)
                    f.close()

                total += 1
            
            elapsed_time = time.time() - start_time

            print("-" * 25)
            print('\n scrapping REUTERS for date ; {}\n'.format(date))
            print('total articles scrapped : {} \n'.format(total))
            print('elapsed_time : {}'.format(elapsed_time))
        else:
            break
     
      
    print('Total articles scrapped : {}'.format(total))
    return('Total articles scrapped : {}'.format(total))


def get_url(date, page=1):
    #url="https://finance.naver.com/news/news_list.nhn?mode=RANK&date=20210519&page=4"
    url = "https://finance.naver.com/news/news_list.nhn?mode=RANK&"
    url_date="date=" + date
    url_page="page="+str(page)
    url = "https://finance.naver.com/news/news_list.nhn?mode=RANK&"+url_date+"&"+url_page
    return url

def get_article(article_url):
    article_url = urlopen(article_url)
    bs = BeautifulSoup(article_url.read(), "html.parser")

    article_date = bs.find("span", class_="article_date")
    print(article_date.get_text())

    article_title = bs.find("div", class_="article_info")
    article_title = article_title.find_next()
    article_title = article_title.get_text().strip()
    print(article_title)

    article_content = bs.find("div", class_="articleCont")
    #print(article_content.get_text())

def main():
    # date > page > article_list > crawling_page
    page_url = urlopen(get_url("20190519"))
    bs = BeautifulSoup(page_url.read(), "html.parser")
    bs_newsList = bs.find("ul", class_="newsList")
    l = [x.get('href') for x in bs_newsList.find_all("a")]

    bs_newsList = bs.find("td", class_="pgRR")
    last_page = bs_newsList.find("a").get("href").split("page=")[-1]
    print(last_page)

    for x in l:
        get_article("https://finance.naver.com/" + x)


""""
    folder = '/home/zeninvest/text_data/'
    failed_urls = folder + 'failed_urls'
    nb_days = 1000

    year_list = [2017, 2016, 2015, 2014]
	

    for year in year_list:
        year_str = str(year)
        journal = 'reuters/'
        html_year = urlopen("https://www.reuters.com/news/archive/us/" + year_str + ".html") # Insert your URL to extract
        # http://www.reuters.com/resources/archive/us/
        # BS object to parse the html code

        bs1 = BeautifulSoup(html_year.read())
        year_pattern = '/news/archive/us/' + year_str
        title = "http://www.reuters.com"
        article_pattern = 'http://www.reuters.com/article'

        # We get only the link tags
        l = [x.get('href') for x in bs1.find_all("a")]
		
		# We keep only those corresponding to a year
        days_list = [x for x in l if x[:len(year_pattern)] == year_pattern]
        

        day_repartition = list(np.array_split(days_list, os.cpu_count()))
        day_repartition = [list(x) for x in day_repartition]
        
        arg_list = [[folder, year, nb_days, x] for x in day_repartition]
        

        folder = "test"
        year=2020
        nb_days=0520
        day_repqrtition=0505
        arg_list = [[folder, year, nb_days, x] for x in day_repartition]
        # Parallel computing using Process class. Refer to Multiprocessing library doc 
        process_list = [mp.Process(target=extraction_naver_finance, args=arg) for arg in arg_list]
        

        
        for p in process_list:
          p.start()

        for p in process_list :
          p.join()
"""

if __name__ == '__main__':
    main()

