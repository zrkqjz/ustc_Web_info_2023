from buildTriplet import *

def threshold_for_1step():
    min_entity = 40
    max_entity = 20000
    min_relation = 100
    r, e = get_count_1step()
    c = {k for k,v in r.items() if v > min_relation}
    t = {k for k,v in e.items() if v > min_entity and v < max_entity}
    print('len of relation:',len(r))
    print('len of eligible relation with threshold',min_relation,':',len(c))
    print('len of entity:',len(e))
    print('len of eligible entity with threshold',min_entity,',',max_entity,':',len(t))

def given_movie_ensurance_1_step():
    _, given_movie = readMap()
    with open('data/entity_1step.txt','r',encoding='utf-8') as file:
        extend_entity = file.readlines()
        extend_entity = [x.strip() for x in extend_entity]
        extend_entity = set(extend_entity)
    
    for i in given_movie:
        if i not in extend_entity:
            print(i,'not found')

def threshold_for_2step():
    min_entity = 20
    max_entity = 20000
    min_relation = 50
    r = set()
    e = set()
    _, given_movie = readMap()
    count = 0
    with open("data/2step_relation_count.json", "r") as f:
        for line in f:
            data = json.loads(line)
            for k, v in data.items():
                if v > min_relation:
                    r.add(k)
    with open("data/2step_entity_count.json", "r") as f:
        for line in f:
            data = json.loads(line)
            for k, v in data.items():
                count += 1
                if k in given_movie or ( v > min_entity and v < max_entity ):
                    e.add(k)
    print('len of eligible relation with threshold',min_relation,':',len(r))
    print('len of eligible entity with threshold',min_entity,',',max_entity,':',len(e))


if __name__ == '__main__':
    threshold_for_2step()