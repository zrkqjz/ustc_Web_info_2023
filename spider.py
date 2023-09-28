import pandas
import requests
import logging
import re
import json
from lxml import etree

idList = pandas.concat([pandas.read_csv('Movie_id.csv', header=None) , pandas.read_csv('Book_id.csv', header=None)])
curID = -1
movie_list_size = 1200
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36'}
BASE_URL = 'https://movie.douban.com'
data = []

def next_ID():
    '''
    return the next ID to be used
    '''
    global curID
    curID += 1
    return idList.iloc[curID, 0]

def scrape_ID(id):
    '''
    scrape a page with given id
    '''
    def scrape_page(url):
        '''
        scrape a page with given url, return the text 
        '''
        logging.info('scraping %s...', url)
        try:
            response = requests.get(url, headers= headers)
            if response.status_code == 200:
                return response.text
            logging.error('get invalid status code %s while scraping %s', response.status_code, url)
        except requests.RequestException:
            logging.error('RequestException while scraping %s', url, exc_info=True)

    def get_url():
        if curID <= movie_list_size :
            url = f'{BASE_URL}/subject/{id}/?from=showing'
        else :
            url = f'https://book.douban.com/subject/{id}'
        return url
    
    index_url = f'https://book.douban.com/subject/{id}'
    return scrape_page(index_url)

def parse_movie(text):
    global data

    def parse_title():
        title = html.xpath('//*[@id="content"]/h1/span/text()')
        return title
    
    def parse_rating():
        rating = html.xpath('//div[@class="rating_self clearfix"]//strong/text()')
        return rating
    
    def parse_info():
        temp = html.xpath('//*[@id="info"]/span/text() | //*[@id="info"]/span//a/text() | //*[@id="info"]/text() | //*[@id="info"]/span/span/text()')
        info = ''
        for str in temp:
            if str[0] == '\n':
                info += '\n'
            else:
                info += str            
        return info
    
    def parse_desc():
        temp = html.xpath('//span[@property="v:summary"]/text()')
        desc = [s.strip() for s in temp]
        return desc
    
    def parse_staff():
        temp = html.xpath('//li[@class="celebrity"]//span/text() | //li[@class="celebrity"]//span//a/text()')
        staff = []
        for i in range(0, len(temp), 2): 
            if i + 1 < len(temp) :
                staff.append(temp[i] + ' ' + temp[i+1])
            else :
                staff.append(temp[i])
        return staff
    
    html = etree.HTML(text)
    newData = {
        "title" : parse_title(),
        "rating" : parse_rating(),
        "info" : parse_info(),
        "description" : parse_desc(),
        "staff" : parse_staff()
    }
    data.append(newData)
    with open("data\data.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def scrape():
    for n in range(0, len(idList)):
        text = scrape_ID(next_ID())
        with open(f'txt\{n}.txt', 'w', encoding='utf-8') as file:
            file.write(text)
        if n % 10 == 0 :
            print(f'{n} done \n')

    '''
        parse_movie(text)
    with open("data\data.json", "w", encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    '''
    


def main():
    text = scrape_ID(1084336)
    print(text)
    with open(f'1084336.txt', 'w', encoding='utf-8') as file:
        file.write(text)

if __name__ == '__main__':
    main()