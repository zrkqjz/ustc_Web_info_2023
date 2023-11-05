import readData
import jieba
import sys

result_count = 0

def print_result(i, readMethod):
    global result_count
    diction = readMethod()
    if result_count >= 3:
        print(diction[i]['title'])
    else:
        print(diction[i]['title'])
        print(diction[i]['description'])
        result_count += 1

def get_arg():
    try:
        arg = sys.argv[1]
    except:
        arg = input('input movie or book:')
    while True:
        if arg == 'movie' or arg == 'm':
            return 'movie'
        elif arg == 'book' or arg == 'b':
            return 'book'
        else:
            print('invalid input')
            arg = input('input movie or book:')

def get_query():
    sep = '-----------------------------------------------------------'
    print(sep)
    print(f' please enter query seperated with space,\n bool operator should be denoted by & | !,\n example input:Titanic | Inception')
    print(sep)
    try:
        string = input('your query:')
        print(sep)
        return string
    except:
        print('invalid query')
        return ' '

def search(readMethod, inverted_index, query_list):    
    def search_one_query(query):
        #对query分词
        seg_list = jieba.cut_for_search(str(query))
        #分出的每个词查询对应文档，然后取交集(查不到的词舍去)
        it = iter(seg_list)
        first = next(it)
        while first not in inverted_index.keys():
            try:
                first = next(it)
            except:
                return set()
        num_list = set(inverted_index[first])
        for seg in seg_list:
            if seg in inverted_index.keys():
                temp = inverted_index[seg]
                if num_list & set(temp) == set():
                    num_list = num_list | set(temp)
                else:
                    num_list = num_list & set(temp)
        return num_list
    
    def bool_operate():
        total = set(range(0, 1200))
        if query == '&':
            temp1 = stack.pop()
            temp2 = stack.pop()
            temp3 = temp1 & temp2
            stack.append(temp3)
        elif query == '|':
            temp1 = stack.pop()
            temp2 = stack.pop()
            temp3 = temp1 | temp2
            stack.append(temp3)
        elif query == '!':
            temp1 = stack.pop()
            temp1 = total - temp1
            stack.append(temp1)

    operator = ['!','&','|']
    stack = []
    for query in query_list:
        if query not in operator:
            temp = search_one_query(query)
            stack.append(temp)
        else:
            bool_operate()
    #打印查询结果
    num_list = stack.pop()
    if len(num_list) == 0:
        print("search failed, no documents matching the query was found")
    for num in num_list:
        print_result(num, readMethod)

def infix_to_postfix(infix):
    precedence = {'!':3, '&':2, '|':1, '(':0}
    stack = []
    postfix = []
    for word in infix:
        if word == '(':
            stack.append(word)
        elif word == ')':
            while stack[-1] != '(':
                postfix += stack.pop()
            stack.pop()
        elif word != '&' and word != '!' and word != '|':
            postfix.append(word)
        else:
            while stack and precedence[word] <= precedence.get(stack[-1], -1):
                postfix += stack.pop()
            stack.append(word)
    while stack:
        postfix += stack.pop()
    return postfix

def search_movie(query):
    readMethod = readData.readMovieData
    inverted_index = readData.readJSON('data\movie_inverted_index.json')
    search(readMethod, inverted_index, query)

def search_book(query):
    readMethod = readData.readBookData
    inverted_index = readData.readJSON('data\\book_inverted_index.json')
    search(readMethod, inverted_index, query)

def main():
    arg = get_arg()
    string = get_query()
    post_fix = infix_to_postfix(string.split(' '))
    if arg == 'movie':
        search_movie(post_fix)
    else:
        search_book(post_fix)

if __name__ == '__main__':
    main()

