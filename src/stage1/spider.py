import pandas
import requests
import re
import logging
import json
import parse
import fake_useragent

idList = pandas.concat([pandas.read_csv('Movie_id.csv', header=None) , pandas.read_csv('Book_id.csv', header=None)])
curID = -1
headers = {'User-Agent': str(fake_useragent.UserAgent().random)}
BASE_URL = 'https://movie.douban.com'
movieData = []
bookData = []
logging.basicConfig(filename='log\\scrape_failed.log', level=logging.ERROR)

def get_proxy():
    try:
        PROXY_API_URL = "https://h.shanchendaili.com/api.html?action=get_ip&key=HUe820e7971028093030zNPr&time=10" \
                        "&count=1&protocol=http&type=json&only=1 "
        proxy_json = requests.get(PROXY_API_URL).text
        server = re.findall("(?<=\"sever\":\").*?(?=\")",
                            proxy_json)[0]
        port = re.findall("(?<=\"port\":).*?(?=,)",
                          proxy_json)[0]
        host = server + ":" + port
    except:
        return None
    proxy = {
        'http': 'http://' + host,
        'https': 'https://' + host,
    }
    return proxy

proxy = get_proxy()

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
        global proxy
        reTry = 0
        logging.info('scraping %s...', url)
        try:
            response = requests.get(url, headers= headers, timeout=8, proxies=proxy)
            if response.status_code == 200:
                return response.text
            elif reTry < 3:
                while response.status_code != 200 and reTry < 3:
                    proxy = get_proxy()
                    response = requests.get(url, headers= headers, timeout=8, proxies=proxy)
                    reTry += 1
            logging.error('get invalid status code %s while scraping %s \n', response.status_code, url)
        except requests.RequestException:
            logging.error('RequestException while scraping %s \n', url, exc_info=True)

    def get_url(id):
        global curID
        if curID <= 1200 :
            url = f'{BASE_URL}/subject/{id}'
        else :
            url = f'https://book.douban.com/subject/{id}'
        return url
    
    index_url = get_url(id)
    return scrape_page(index_url)

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
            movieData.append(parse.parse_movie(text))
        else:
            print(f'{curID} is None')
            with open(f'log\exception.txt', 'a', encoding='utf-8') as file:
                file.write(f'{curID} is None\n') 
    with open("data\movieData.json", "w", encoding='utf-8') as file:
        json.dump(movieData, file, indent=2, ensure_ascii=False)

    for n in range(1200, 2400):
        text = scrape_ID(next_ID())
        if text != None :
            bookData.append(parse.parse_book(text))
        else:
            print(f'{curID} is None')
            with open(f'log\exception.txt', 'a', encoding='utf-8') as file:
                file.write(f'{curID} is None\n')      
    with open("data\\bookData.json", "w", encoding='utf-8') as file:
        json.dump(bookData, file, indent=2, ensure_ascii=False) 

def main():
    scrape()
if __name__ == '__main__':
    main()