import gzip
import os
import timeit
import json
from myRead import *


min_entity = 40
max_entity = 20000
min_relation = 50

def delete(path):
    try:
        os.remove(path)
    except:
        pass

def extract_triplet():
    '''
    extract triplet with given movie, build the 1 step KG
    '''

    def add_triplet(new, triplet):
        output.write(' '.join(triplet) + '\n')
        new_entity.add(new)
        nonlocal count
        count += 1
        if count % 5000 == 0:
            print(f'{count} triplet has been found')

    _, movie_entity = readMap()
    
    new_entity = set(movie_entity)
    count = 0
    with gzip.open('data/freebase_douban.gz','rb') as f:
        with open('data/KG_1step.txt', 'a', encoding='utf-8') as output:
            for line in f:
                line = line.strip()
                triplet = line.decode().split('\t')[:3]

                if triplet[0] in movie_entity and triplet[2].startswith('<http://rdf.freebase.com/ns/'):
                    add_triplet(new=triplet[2], triplet=triplet)
                
                elif triplet[2] in movie_entity and triplet[0].startswith('<http://rdf.freebase.com/ns/'):
                    add_triplet(new=triplet[0], triplet=triplet)
                      
    with open('data/entity_1step.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(new_entity))
    print(f'extract_triplet finished, {count} triplets are found')

def get_count_1step():
    '''
    return relation_count and entity_count as dict
    '''

    def add_count(e, count):
        if e not in count.keys():
            count[e] = 1
        else:
            count[e] += 1

    relation_count = {}
    entity_count = {}
    
    #一开始的578个电影不能被过滤掉
    _, given_movie = readMap()
    for movie in given_movie:
        entity_count[movie] = min_entity

    with open('data/KG_1step.txt','r',encoding='utf-8') as file:
        for line in file:
            triplet = line.split(' ')[:3]
            triplet = [x.strip() for x in triplet]
            add_count(triplet[0], entity_count)
            add_count(triplet[1], relation_count)
            add_count(triplet[2], entity_count)
    
    return relation_count, entity_count
            
def filter_1step():
    '''
    filter 1 step KG and extract eligible entity
    '''
    def eligible_entity(e):
        if entity_count[e] > min_entity and entity_count[e] < max_entity:
            return True
        else:
            return False
        
    relation_count, entity_count = get_count_1step()
    new_entity = set()

    delete('data/KG_1step_filtered.txt')
    with open('data/KG_1step.txt','r',encoding='utf-8') as file:
        with open('data/KG_1step_filtered.txt','a', encoding='utf-8') as output:
            while True:
                line = file.readline()
                if not line:
                    break

                triplet = line.split(' ')[:3]
                triplet = [x.strip() for x in triplet] 
                if relation_count[triplet[1]] > min_relation:
                    if eligible_entity(triplet[0]) and eligible_entity(triplet[2]):
                        output.write(' '.join(triplet) + '\n')
                        new_entity.add(triplet[0])
                        new_entity.add(triplet[2])
                        """ if eligible_entity(triplet[2]):
                            new_entity.add(triplet[2]) """
                    """ elif eligible_entity(triplet[2]):
                        output.write(' '.join(triplet) + '\n')
                        new_entity.add(triplet[2]) """
                    
    with open('data/entity_1step.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(new_entity))

def build_2step_KG():
    def add_line(line):
        output.write(line)
        output.write(b'\n')
        nonlocal count
        count += 1
        if count % 50000 == 0:
            print(f'{count} triplet has been found')

    #read extend_entity
    with open('data/entity_1step.txt','r',encoding='utf-8') as file:
        extend_entity = file.readlines()
        extend_entity = [x.strip() for x in extend_entity]
        extend_entity = set(extend_entity)

    delete('data/KG_2step.gz')
    count = 0
    with gzip.open('data/freebase_douban.gz','rb') as f:
        with gzip.open('data/KG_2step.gz', 'ab') as output:
            for line in f:
                line = line.strip()
                triplet = line.decode().split('\t')[:3]
                if triplet[0] in extend_entity and triplet[2].startswith('<http://rdf.freebase.com/ns/'):
                    add_line(line)
                elif triplet[2] in extend_entity and triplet[0].startswith('<http://rdf.freebase.com/ns/'):
                    add_line(line)

    print(f'2 step KG finished, {count} triplet are found') 

def count_2step():

    def add_count(e, count):
        if e not in count.keys():
            count[e] = 1
        else:
            count[e] += 1

    def write_to_file(path, myDict):
        with open(path,'w',encoding='utf-8') as file:
            json.dump(myDict, file)

    relation_count = {}
    entity_count = {} 

    #一开始的578个电影不能被过滤掉
    _, given_movie = readMap()
    for movie in given_movie:
        entity_count[movie] = min_entity

    with gzip.open('data/KG_2step.gz','rb') as f:
        for line in f:
            line = line.strip()
            triplet = line.decode().split('\t')[:3]
            add_count(triplet[0], entity_count)
            add_count(triplet[1], relation_count)
            add_count(triplet[2], entity_count)

    write_to_file('data/2step_relation_count.json', relation_count)
    write_to_file('data/2step_entity_count.json', entity_count)

def filter_2step():

    def eligible_entity(e):
        if entity_count[e] > 20 and entity_count[e] < max_entity:
            return True
        else:
            return False

    with open("data/2step_relation_count.json", "r") as f:
        relation_count = json.load(f)
    with open("data/2step_entity_count.json", "r") as f:
        entity_count = json.load(f)

    delete('data/KG_2step_filtered.txt')
    count = 0
    with gzip.open('data/KG_2step.gz','rb') as f:
        with open('data/KG_2step_filtered.txt','a', encoding='utf-8') as output:
            for line in f:
                line = line.strip()
                triplet = line.decode().split('\t')[:3]
                if relation_count[triplet[1]] > min_relation and eligible_entity(triplet[0]) and eligible_entity(triplet[2]):
                        output.write(' '.join(triplet) + '\n')
                        count += 1
                        if count % 5000 == 0:
                            print(f'{count} triplet has been found')
    print(f'2 step KG has been filtered , get {count} triplet') 


def main():
    extract_triplet()
    filter_1step()

    start = timeit.default_timer()
    build_2step_KG()
    end = timeit.default_timer()
    print('time to build 2 step KG:',end - start, '秒')

    start = timeit.default_timer()
    count_2step()
    end = timeit.default_timer()
    print('time to count 2 step KG:',end - start, '秒')
    
    start = timeit.default_timer()
    filter_2step()
    end = timeit.default_timer()
    print('time to filter 2 step KG:',end - start, '秒')

if __name__ == '__main__':
    start = timeit.default_timer()
    filter_2step()
    end = timeit.default_timer()
    print('time to filter 2 step KG:',end - start, '秒')
    
