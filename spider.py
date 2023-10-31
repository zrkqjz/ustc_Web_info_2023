import pandas
import requests
import logging
import json
from lxml import etree

idList = pandas.concat([pandas.read_csv('Movie_id.csv', header=None) , pandas.read_csv('Book_id.csv', header=None)])
curID = -1
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36'}
BASE_URL = 'https://movie.douban.com'
movieData = []
bookData = []
logging.basicConfig(filename='data\\scrape_failed.log', level=logging.DEBUG)

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
            logging.error('get invalid status code %s while scraping %s \n', response.status_code, url)
        except requests.RequestException:
            logging.error('RequestException while scraping %s \n', url, exc_info=True)

    def get_url():
        if curID <= 1200 :
            url = f'{BASE_URL}/subject/{id}/?from=showing'
        else :
            url = f'https://book.douban.com/subject/{id}'
        return url
    
    index_url = get_url()
    return scrape_page(index_url)

def parse_movie(text):
    def parse_title():
        title = html.xpath('//*[@id="content"]/h1/span/text()')
        return title
    
    def parse_rating():
        rating = html.xpath('//div[@class="rating_self clearfix"]//strong/text()')
        if rating != None:
            return rating
        else:
            logging.error("get invalid rating while parse %s", parse_title())
    
    def parse_info():
        info = html.xpath('//*[@id="info"]/span/text() | //*[@id="info"]/span//a/text() | //*[@id="info"]/text() | //*[@id="info"]/span/span/text()')
        if info != None:
            info = ' '.join(info)
            return info
        else:
            logging.error("get invalid info while parse %s", parse_title())
    
    def parse_desc():
        desc = html.xpath('//span[@property="v:summary"]/text()')
        if desc != None:
            desc = ' '.join(desc)
            return desc
        else:
            logging.error("get invalid description while parse %s", parse_title())
    
    def parse_staff():
        staff = html.xpath('//li[@class="celebrity"]//span/text() | //li[@class="celebrity"]//span//a/text()')
        if staff != None:
            staff = ' '.join(staff)
            return staff
        else:
            logging.error("get invalid staff while parse %s", parse_title())
    
    html = etree.HTML(text)
    newData = {
        "title" : parse_title(),
        "rating" : parse_rating(),
        "info" : parse_info(),
        "description" : parse_desc(),
        "staff" : parse_staff()
    }
    movieData.append(newData)

def parse_book(text):
    def parse_title():
        title = html.xpath('//*[@id="wrapper"]/h1/span/text()')
        return title
    
    def parse_rating():
        rating = html.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()')
        if rating != None:
            return rating
        else:
            logging.error("get invalid rating while parse %s", parse_title())
    
    def parse_info():
        info = html.xpath('//*[@id="info"]//*/text() | //*[@id="info"]/text()')
        if info != None:
            info = ' '.join(info)
            return info
        else:
            logging.error("get invalid info while parse %s", parse_title())
    
    def parse_desc():
        desc = html.xpath('//*[@id="link-report"]//span[@class="all hidden"]//p/text()')
        if desc != None:
            desc = ' '.join(desc)
            return desc
        else:
            logging.error("get invalid description while parse %s", parse_title())
    
    def parse_staff():
        staff = html.xpath('//div[@class="intro"]/p/text()')
        if staff != None:
            staff = ' '.join(staff)
            return staff
        else:
            logging.error("get invalid staff while parse %s", parse_title())
    
    html = etree.HTML(text)
    newData = {
        "title" : parse_title(),
        "rating" : parse_rating(),
        "info" : parse_info(),
        "description" : parse_desc(),
        "staff" : parse_staff()
    }
    bookData.append(newData)

def scrape_to_txt():
    for n in range(0, len(idList)):
        text = scrape_ID(next_ID())
        if text != None :
            with open(f'txt\{curID}.txt', 'w', encoding='utf-8') as file:
                file.write(text)
                print(f'{curID}/2400 done\n')
        else:
            print(f'{curID} is None\n')
            with open(f'data\exception.txt', 'a', encoding='utf-8') as file:
                file.write(f'{curID} is None\n')
    
def scrape():
    for n in range(0, 1200):
        text = scrape_ID(next_ID())
        if text != None :
            parse_movie(text)
        else:
            print(f'{curID} is None')
            with open(f'data\exception.txt', 'a', encoding='utf-8') as file:
                file.write(f'{curID} is None\n') 
    with open("data\movieData.json", "w", encoding='utf-8') as file:
        json.dump(movieData, file, indent=2, ensure_ascii=False)

    for n in range(1200, 2400):
        text = scrape_ID(next_ID())
        if text != None :
            parse_book(text)
        else:
            print(f'{curID} is None')
            with open(f'data\exception.txt', 'a', encoding='utf-8') as file:
                file.write(f'{curID} is None\n')      
    with open("data\\bookData.json", "w", encoding='utf-8') as file:
        json.dump(bookData, file, indent=2, ensure_ascii=False) 

def main():
    scrape()
if __name__ == '__main__':
    main()