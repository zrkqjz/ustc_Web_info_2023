import json

def readMovieData():
    'readMovieData返回爬取并解析后的数据, 具体使用方法见readData.py中的main()'
    with open('data\movieData.json', encoding='utf-8') as file:
        dict = json.load(file)
    return dict

def readBookData():
    'readBookData返回爬取并解析后的数据, 具体使用方法见readData.py中的main()'
    with open('data\\bookData.json', encoding='utf-8') as file:
        dict = json.load(file)
    return dict

def readJSON(filepath):
    with open(filepath, encoding='utf-8') as file:
        dict = json.load(file)
    return dict       

def writeJSON(stuff, path):
    with open(path, "w", encoding='utf-8') as file:
        json.dump(stuff, file, indent=2, ensure_ascii=False)

def main():
    dict = readMovieData()
    print(dict[3]['description'])
if __name__ == '__main__':
    main()
    print(type(readJSON('data\movie_inverted_index.json')))