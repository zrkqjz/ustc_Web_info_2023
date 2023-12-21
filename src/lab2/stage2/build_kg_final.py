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

    given_movie_mapping = {x: i for i, x in enumerate(given_movie)}
    other_movie_mapping = {x: i for i, x in enumerate(other_movie)}
    relation_mapping = {x: i for i, x in enumerate(relation_set)}

    return given_movie_mapping, other_movie_mapping, relation_mapping

def build():
    def entity_map(movie):
        try:
            return given_movie_mapping[movie]
        except:
            return other_entity_mapping[movie]
        
    given_movie_mapping, other_entity_mapping, relation_mapping = entity_to_index()
    text = [0 for i in range(3)]
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
    pass

if __name__ == '__main__':
    build()