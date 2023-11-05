import readData

import jieba
import json

def get_stopwords_list(file):
    with open(file, 'r', encoding='utf-8') as f:
        stopword_list = [word.strip('\n') for word in f.readlines()]
    stopword_list.append('\n')
    stopword_list.append(' ')
    stopword_list.append('饰')
    return stopword_list

def clean_stopword(word_list, stopword_list):
    result = []
    for w in word_list:
        if w not in stopword_list:
            result.append(w)
    return result

def myCut(stopword_list = [' ']):
    
    def cut(text):
        seg_list = jieba.cut_for_search(str(text))
        seg_list = clean_stopword(seg_list, stopword_list)
        return seg_list
    
    def cutBook():
        book = readData.readBookData()
        # 提取所有书的关键词
        book_key_words = []
        for n in range(len(book)):
            temp = {
                'num':n,
                'key_words':''
            }
            keys = [key for key in book[n].keys() if key != 'rating'] #rating 不提取关键词
            keyword_set = set()
            for key in keys:
                helper = set(cut(book[n][key]))
                keyword_set = keyword_set.union(helper)
            temp['key_words'] = ','.join(keyword_set)
            book_key_words.append(temp)
        # 输出书关键词表
        with open("data\\book_key_words.json", "w", encoding='utf-8') as file:
            json.dump(book_key_words, file, indent=2, ensure_ascii=False)
    
    def cutMovie():
        movie = readData.readMovieData()
        # 提取所有电影的关键词
        movie_key_words = []
        for n in range(len(movie)):
            temp = {
                'num':n,
                'key_words':''
            }
            keys = [key for key in movie[n].keys() if key != 'rating'] #rating 不提取关键词
            keyword_set = set()
            for key in keys:
                helper = set(cut(movie[n][key]))
                keyword_set = keyword_set.union(helper)
            temp['key_words'] = ','.join(keyword_set)
            movie_key_words.append(temp)
        # 输出电影关键词表
        with open("data\movie_key_words.json", "w", encoding='utf-8') as file:
            json.dump(movie_key_words, file, indent=2, ensure_ascii=False)
    
    cutBook()
    cutMovie()    

    
if __name__ == '__main__':
    stopword_list = get_stopwords_list('stopwords-master/hit_stopwords.txt') + get_stopwords_list('stopwords-master/stopwords-en.txt') + get_stopwords_list('stopwords-master/my_stopwords.txt')
    if 'The' in stopword_list:
        print('ERROR')
    myCut(stopword_list=stopword_list)