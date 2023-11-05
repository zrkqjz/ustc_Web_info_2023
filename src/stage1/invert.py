import readData

def invert_table(dict):
    inverted_index = {}
    for i in range(len(dict)):
        w_list = dict[i]['key_words'].split(',')
        for word in w_list:
            if word not in inverted_index:
                inverted_index[word] = [dict[i]['num']]
            else:
                inverted_index[word].append(dict[i]['num'])
    return inverted_index

if __name__ == '__main__':
    path_movie_key_words = 'data\movie_key_words.json'
    path_book_key_words = 'data\\book_key_words.json'
    # 电影倒排表生成
    movie_keywords = readData.readJSON(path_movie_key_words)
    readData.writeJSON(invert_table(movie_keywords), 'data\movie_inverted_index.json')
    # 书倒排表生成
    book_keywords = readData.readJSON(path_book_key_words)
    readData.writeJSON(invert_table(book_keywords), 'data\\book_inverted_index.json')