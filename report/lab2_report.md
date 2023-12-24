
# Stage1
## 匹配豆瓣ID与FreeBase实体
读取给定的 `douban2fb.txt` 文件，获得豆瓣ID对应的mid，并添加前缀使之与给定的 `freebase_douban.gz` 中实体格式一致，返回dict型的映射表与set型的给定电影实体：

```python
def readMap():
    '''
    return Map (dict,{id:fb}) and movie_entity list
    '''
    with open('data/douban2fb.txt', 'r') as file:
        data = file.readlines()

    Map = {}
    movie_entity = []
    for line in data:
        temp = line.split()
        Map[temp[0]] = '<'+'http://rdf.freebase.com/ns/' + temp[1] +'>'
        movie_entity.append('<'+'http://rdf.freebase.com/ns/' + temp[1] +'>')
    return Map, set(movie_entity)
```

## 第一步筛选
用上面的 `readMap` 方法得到给定的电影实体表，遍历给定的知识图谱，遇到头实体或尾实体是给定电影时，将其写入 `KG_1step.txt` 中。

遍历结束后，统计实体和关系出现数量，挑选高频实体，存入 `entity_1step.txt` 中。给定实体的频数初始值为筛选的最低标准，保证给定实体不被筛走：

```python
    _, given_movie = readMap()
    for movie in given_movie:
        entity_count[movie] = min_entity
```

这些txt文件，以及下文提到的一些txt文件都没有提交，但运行 lab2/stage1/buildTriplet.py 文件时会生成提到的所有txt。

## 第二步筛选
读取第一步 `entity_1step.txt` 中的拓展实体表，遍历知识图谱，找到所有头实体或尾实体是拓展实体的三元组，写入 `KG_2step.gz` 中，最终得到的 `KG_2step.gz` 约1.4G。统计其中实体和关系的出现次数。

在 `KG_2step.gz` 中，挑选头实体、尾实体、关系均为高频的三元组，写入 `KG_2step_filtered.txt` 中，最终得到的图谱大约有 50w 个三元组:

```python
    def eligible_entity(e):
        if entity_count[e] > 20 and entity_count[e] < max_entity:
            return True
        else:
            return False

    triplet = line.decode().split('\t')[:3]
    if relation_count[triplet[1]] > min_relation 
        and eligible_entity(triplet[0]) 
        and eligible_entity(triplet[2]):
            output.write(' '.join(triplet) + '\n')
```

## 筛选标准的确定
最终得到的知识图谱显然已经超过了群里说的 5w 个三元组，因此统计了一下不同要求下，符合条件的实体和关系数量，这部分代码在 `draft.py` 中。

![](assert2/Screenshot%202023-12-24%20220645.png)

上图可以看到出现超过 50 次的关系有 403 条，出现超过 40 次的实体有 21911 个，以此为标准筛选出的图谱大约有 30w 个三元组，已经有些多了。而且实际运行后，发现以 40 为标准会将两个给定电影筛掉：

![](assert2/QQ图片20231224221026.png)

两部电影分别是 [情书](https://movie.douban.com/subject/1292220) 和 [你丫闭嘴！](https://movie.douban.com/subject/1303815)，这两部电影自身的出现次数都有好几百次，但是没有链接到其他高频实体上去，因此最终的知识图谱中没有他们。

将实体的频数要求降低到 20 以上，符合要求的实体和关系数如下：

![](assert2/Screenshot%202023-12-24%20221555.png)

符合要求的实体多了很多，过滤后的知识图谱规模也达到了 50w 个三元组，即使如此《你丫闭嘴！》链接到的实体依然很少，《情书》则多一些：

![](assert2/Screenshot%202023-12-24%20221748.png)

![](assert2/Screenshot%202023-12-24%20221840.png)

![](assert2/Screenshot%202023-12-24%20221958.png)

![](assert2/Screenshot%202023-12-24%20222025.png)

![](assert2/Screenshot%202023-12-24%20222107.png)

最终选择了 50w 个三元组的规模，遍历一次需要不到 1 秒，包含了给定的全部实体，但可能依然不足以支撑实际的推荐任务。

# Stage2
## 实体与关系到ID的映射
读取给定的 `movie_id_map.txt` 中豆瓣ID到实验ID的映射，结合Stage1中得到的豆瓣ID到Freebase实体的映射，得到Freebase实体到实验ID的映射：

```python
    with open('data/movie_id_map.txt', 'r') as file:
        data = file.readlines()

    fb_to_id = {}
    for line in data:
        # temp[0] = db, temp[1] = id
        temp = line.split()
        fb = db_to_fb[temp[0]]
        fb_to_id[fb] = temp[1]
```

给定电影映射完毕后，遍历Stage1得到的 `KG_2step_filtered.txt`，得到其中所有的关系和实体集合，将不在给定电影中的实体从578开始编号，并将关系映射到[0, 𝑛𝑢𝑚 𝑜𝑓 𝑟𝑒𝑙𝑎𝑡𝑖𝑜𝑛𝑠)范围。

