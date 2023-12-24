# Stage1

## 爬虫

使用request库爬取网页，lxml库利用xpath解析。爬虫代码在`spider.py`中，解析代码在`parse.py`中，书和电影爬取结果分别在`bookData.json`和 `movieData.json`中。

### 反爬策略

不带headers爬会直接报错，因此用fake_useragent库每次生成不同的headers：
```
headers = {'User-Agent': str(fake_useragent.UserAgent().random)}
```

同一ip爬太多可能被封ip，因此写了一个更换代理的方法：
```
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
```
但是实际上，我们做实验的时候并没有一次全爬完，因此没有遇到被封ip的情况。ip来自[ 闪臣代理 (shanchendaili.com)](https://scsg.shanchendaili.com/)，有免费试用，可以通过api获取ip。但因为没有遇到封ip的情况，所以也没去激活，这段api是网上其他人分享的（估计也过期了）。

### 爬虫
```
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
```
给定url爬取时，调用requests库的get方法，传入前文生成的headers和proxy。爬取成功返回结果，爬取失败时会更换ip尝试两次，仍然失败会放弃并写入日志。

但是如前所述，我们做实验的时候并没有一次全爬完，爬取了一部分后才学会写日志，所以日志没有记录到所有失败url。

查看最终结果的长度，应该有大概二十个爬取失败的结果
```
>>> import readData
>>> book = readData.readBookData()
>>> print(len(book))
1190
>>> import readData
>>> movie = readData.readMovieData()
>>> print(len(movie))   
1184
```

### 解析
以下面的页面为例：

![](assert/Screenshot%202023-11-05%20150411.png)

解析了标题、评分、剧情简介、演职员表部分，分别存为title、rating、description、staff。此外还解析了海报旁边的导演、编剧、主演等信息，存入info部分。

具体代码在`parse.py`中，此处以提取剧情简介代码为例：
```
    def parse_desc():
        desc = html.xpath('//span[@class="all hidden"]/text()')
        if desc == []:
            desc = html.xpath('//span[@property="v:summary"]/text()')
        #desc = html.xpath('//span[@property="v:summary"]/text() | //span[@class="all hidden"]/text()')
        if desc != []:
            for string in desc:
                string = string.strip()
            desc = ' '.join(desc)
            return desc
        else:
            logging.error("get invalid description while parse %s", parse_title())
```
利用lxml库的xpath方法，依据xpath提取简介信息，处理为一个字符串后返回。

## 检索

### 分词
使用[结巴中文分词 (github.com)](https://github.com/fxsjy/jieba)工具。

[hanlp和jieba等六大中文分工具的测试对比 - 知乎 (zhihu.com)](https://zhuanlan.zhihu.com/p/57731823)这篇文章对比了六种分词器，选择结巴分词主要是因为安装方便、使用广泛、容易找教程，并且分词效果对于实验已经够用了。

`draft.py`中的方法 `split_compare()`对比了结巴分词不同模式的效果：
```
>>> import draft
>>> draft.split_compare()
Building prefix dict from the default dictionary ...
Loading model from cache C:\Users\zzzrk\AppData\Local\Temp\jieba.cache
Loading model cost 0.493 seconds.
Prefix dict has been built successfully.
麻省理工学院的数学教授蓝波在席上公布了一道困难的数学题，却被年轻的清洁工威尔（马特·戴蒙 饰）解了出来。
cut for search without HMM:麻省,理工,工学,学院,理工学,工学院,麻省理工学院,的,数学,教授,蓝波,在,席,上,公布,了,一道,困难,的,数学,数学题,，,却,被,年轻,的,清洁,清洁工,威尔,（,马,特,·,戴,蒙, ,饰,）,解,了,出来,。
cut for search with HMM:麻省,理工,工学,学院,理工学,工学院,麻省理工学院,的,数学,教授,蓝波,在席,上,公布,了,一道,困难,的,数学,数学题,，,却,被,年轻,的,清洁,清洁工,威尔,（,马特,·,戴蒙
, ,饰,）,解了,出来,。
cut all:麻省,麻省理工,麻省理工学院,理工,理工学,理工学院,工学,工学院,学院,的,数学,教授,蓝波,在,席,上,公布,了,一道,困难,的,数学,数学题,，,却,被,年轻,的,清洁,清洁工,威尔,（,马,特,·,戴,蒙,, ,,饰,）,解,了,出来,。
```
输入是《心灵捕手》剧情简介第一句，观察输出：
1. ’麻省理工‘只有cut all模式分了出来
2. 演员马特·戴蒙的名字在启用HMM（隐马尔可夫）模型时分了出来，但在其他模式下都被切分成了单个字
3. ’在席上‘在HMM模式被奇怪的切成了’在席‘和’上‘，不知道怎么回事

结巴分词的官方文档说 `jieba.cut_for_search` 方法适合用于搜索引擎构建倒排索引的分词，粒度比较细。考虑上面的输出结果，不使用HMM模型时的`jieba.cut_for_search`方法虽然分不出人名，但检索时可以对单字取交集得到准确结果，分的更细可以避免遗漏，因此实验里采用此方法。

电影的分词代码如下，图书类似，具体代码在 `textRep.py`中 ：
```
    def cut(text):
        seg_list = jieba.cut_for_search(str(text))
        seg_list = clean_stopword(seg_list, stopword_list)
        return seg_list

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

```
读取爬虫爬到的每部电影信息，调用 `cut` 方法分词，将所有信息的分词结果取并集后，输出到 `movie_key_words.json` 文件。

### 去除停用词
在[goto456/stopwords: 中文常用停用词表（哈工大停用词表、百度停用词表等） (github.com)](https://github.com/goto456/stopwords)下载了哈工大停用词表，在[stopwords-iso/stopwords-en: English stopwords collection (github.com)](https://github.com/stopwords-iso/stopwords-en)下载了英文停用词表，存在`src\stopwords-master`文件夹下。此外还有一个自己添加的停用词表，因为每部电影爬取的基本信息里都有导演、编剧、主演等词，因此把这些词添加进停用词表。

去除停用词的代码如下：
```
def clean_stopword(word_list, stopword_list):
    result = []
    for w in word_list:
        if w not in stopword_list:
            result.append(w)
    return result
```

### 倒排表构建
倒排表采用了python中的字典型，没有构建跳表，具体理由后面有分析。

具体代码在 `invert.py` 中，读取到每部电影的关键词表后，运行下面的方法构建倒排表：
```
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
```

### bool查询

对输入的bool表达式首先转换为后缀表达式，随后按照后缀表达式检索每个关键词的相关文档，遇到运算符则取交/并/补集。

考虑查询“中科大泰坦尼克号”的情况，分词大概会分出“中科大”、“泰坦”、“尼克”等词。“中科大”不会查询到任何结果，“泰坦”和“尼克”作为常见词会查询到多个结果。预期的结果应该忽略掉干扰项“中科大"，同时返回尽可能准确的结果，而不是把每一部有人叫”尼克“的电影都返回。因此，对于查询条件的不同词，应该取交集，除非他查不到任何结果。

检索每个关键词的代码如下：
```
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
```

查询到结果后，按照文档编号读取信息，打印标题和简介。结果多于5个时后面的结果只打印标题：
```
def print_result(i, readMethod):
    global result_count
    diction = readMethod()
    if result_count >= 3:
        print(diction[i]['title'])
    else:
        print(diction[i]['title'])
        print(diction[i]['description'])
        result_count += 1
```


运行 `search.py` ，查询豆瓣top250中排04的《泰坦尼克号》和排84的《心灵捕手》：

![](assert/Screenshot%202023-11-05%20160305.png)

![](assert/Screenshot%202023-11-05%20160423.png)

用布尔表达式检索：
![](assert/Screenshot%202023-11-05%20165033.png)

搜索排行第04的图书《哈利·波特》，结果较多，后面的结果只打印标题：
![](assert/Screenshot%202023-11-05%20165422.png)

排行第84的图书叫《文学回忆录》，[文学回忆录 (豆瓣) (douban.com)](https://book.douban.com/subject/20440644/)，好像没在给定的数据集里，没有展示。
### 索引压缩与跳表

这两部分分析过后都觉得不如不做，因此没有实际使用，只实现了对象。

#### 索引压缩

如前所述，倒排表用python的字典型存储，探索下字典型的内存分配：
```
>>> d = {'key':123}
>>> sys.getsizeof(d)
184
>>> sys.getsizeof('key')
52
>>> sys.getsizeof(123)
28
>>> sys.getsizeof({})
64
```
可以看到内存由key、value和字典结构本身的所占的内存构成，字典本身的内存无法压缩，考虑key和value的压缩：

key在倒排表中是关键词，但是python已经选择了用字符串型存储key，本身就是变长的，按块存储意义不大。此外，实验中的关键词基本都是中文，前端编码也意义不大。

value是一个list型的列表，存储了文档编号。如果文档编号较大，可以考虑存储间距、变长编码等方法。但是本次实验文档只有2400个，分成电影和图书后最大是1200，没有超过python存储int型的范围，也没有压缩的必要：
```
>>> import sys
>>> a = 1
>>> sys.getsizeof(a)
28
>>> a = 2400
>>> sys.getsizeof(a)
28
```


综合考虑，最后没有使用什么压缩方法，只在 `draft.py` 文件的 `zip_compare` 方法中写了按间距存储的对象zipList，带有insert和search方法。

运行`zip_compare`方法，对比存储`[0,112,210,434,508,593,688]` （关键词”救赎“对应的文档列表）时的存储空间，输出如下：
```
result for search 112: 112
size of my List: 196
size of python list: 120
```
发现python的链表反而还小很多，比 $28 \times 7$ 还要小。~~试图用自己的灵光一闪挑战编译器~~

#### 跳表

去除停用词后，大多数词项对应的文档其实很少。`draft.py` 中的 `draw_graph` 方法输出词项的列表长度平均值，并绘制统计图：
```
average length of movie:  4.066069057104913
average length of book:  5.051262778111846
```
![](assert/Screenshot%202023-11-05%20192002.png)

长度大于30的词项很少，图里没有统计。可以看出，对应文档少于5的词项占据了绝大部分，因此建立跳表不是很有必要。

此外，python的set类型支持通过'&'运算符取交集，因此自己实现的跳表很可能不如set型。`draft.py` 中的 `skipList_compare` 方法实现了一个最多四层的跳表SkipList，并且对比了大小和时间的差异。

SkipList的每个节点都存储了它的值以及在更低层的后继节点。插入新节点时先插入到最低层，然后有1/2的概率上升（因此有1/8概率插入到最高层）。查找时从最高层开始，查找不到时下降一层，直到最低层也找不到为止。

运行`skipList_compare` 方法，针对关键词”尼克“对应的文档建立跳表，并对比跳表和set型的大小和查找速率，输出如下：

![](assert/Screenshot%202023-11-05%20191241.png)

大小显然是python set类型更小，而且查找时间也是set型更快，几乎快一个数量级。对本次实验来说，这个跳表的数据已经很多了，大多数词项的查找时间应该差距更大。因此最终没有使用跳表。~~再次试图用自己的灵光一闪挑战编译器~~

总之尝试了一下，觉得自己写的数据结构确实不如python的各种数据类型，因此只在 `draft.py` 中留了一些尝试的记录，最终没有使用压缩算法和跳表。

