import os

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

def given_movie_map():
    db_to_fb, _ = readMap()

    with open('data/movie_id_map.txt', 'r') as file:
        data = file.readlines()

    fb_to_id = {}
    for line in data:
        # temp[0] = db, temp[1] = id
        temp = line.split()
        fb = db_to_fb[temp[0]]
        fb_to_id[fb] = temp[1]

    return fb_to_id

def entity_to_index():

    def add(movie):
        if movie not in given_movie:
            other_movie.add(movie)

    _, given_movie = readMap()
    other_movie = set()
    relation_set = set()
    with open('../stage1/data/KG_2step_filtered.txt','r',encoding='utf-8') as file:
        for line in file:
            triplet = line.split(' ')[:3]
            triplet = [x.strip() for x in triplet]
            add(triplet[0])
            relation_set.add(triplet[1])
            add(triplet[2])

    
    given_movie_mapping = given_movie_map()

    other_movie = list(other_movie)
    other_movie.sort()
    n = len(given_movie)
    other_movie_mapping = {other_movie[i]: i + n for i in range(len(other_movie))}

    relation_set = list(relation_set)
    relation_set.sort()
    relation_mapping = {relation_set[i]: i for i in range(len(relation_set))}

    return given_movie_mapping, other_movie_mapping, relation_mapping

def build():
    def entity_map(movie):
        if movie in given_movie_mapping.keys():
            v = given_movie_mapping[movie]
            c.add(movie)
            return v
            # return given_movie_mapping[movie]
        else:
            return other_entity_mapping[movie]
        
    given_movie_mapping, other_entity_mapping, relation_mapping = entity_to_index()
    text = [0 for i in range(3)]
    c = set()
    try:
        os.remove('data/Douban/kg_final.txt')
    except:
        pass
    with open('../stage1/data/KG_2step_filtered.txt','r',encoding='utf-8') as file:
        with open('data/Douban/kg_final.txt','a', encoding='utf-8') as output:
            for line in file:
                triplet = line.split(' ')[:3]
                triplet = [x.strip() for x in triplet]
                text[0] = str(entity_map(triplet[0]))
                text[1] = str(relation_mapping[triplet[1]])
                text[2] = str(entity_map(triplet[2]))
                output.write(' '.join(text) + '\n')
    for i in given_movie_mapping.keys():
        if i not in c:
            print(i,'not found, id:',given_movie_mapping[i])

if __name__ == '__main__':
    build()