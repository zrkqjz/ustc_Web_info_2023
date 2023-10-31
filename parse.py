from lxml import etree
import json
import logging

bookData = []
movieData = []
logging.basicConfig(filename='log\\parse_failed.log', level=logging.DEBUG)

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
    return newData

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
    return newData
    
def parse():
    for n in range(0, 1200):
        try:
            with open(f'txt\{n}.txt', encoding='utf-8') as file:
                text = file.read()
            movieData.append(parse_movie(text))
        except:
            print(f'{n} is None')
    with open("data\movieData.json", "w", encoding='utf-8') as file:
        json.dump(movieData, file, indent=2, ensure_ascii=False)

    for n in range(1200, 2400):
        try:
            with open(f'txt\{n}.txt', encoding='utf-8') as file:
                text = file.read()
            bookData.append(parse_book(text))
        except:
            print(f'{n} is None')        
    with open("data\\bookData.json", "w", encoding='utf-8') as file:
        json.dump(bookData, file, indent=2, ensure_ascii=False)

def main():
        parse()
if __name__ == '__main__':
    main()