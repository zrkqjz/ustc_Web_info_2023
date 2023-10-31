import json

def readMovieData():
    'readMovieData返回整个json文件, 具体使用方法见readData.py中的main()'
    with open('data\movieData.json', encoding='utf-8') as file:
        dict = json.load(file)
    return dict

def readBookData():
    'readBookData返回整个json文件, 具体使用方法见readData.py中的main()'
    with open('data\\bookData.json', encoding='utf-8') as file:
        dict = json.load(file)
    return dict

def main():
    dict = readMovieData()
    print(dict[1]['title'])
if __name__ == '__main__':
    main()