import gzip
import pandas

def readZip():
    with gzip.open('data/freebase_douban.gz','rb') as f:
        for line in f:
            line = line.strip()
            triplet = line.decode().split('\t')[:3]
            print(triplet)
            break

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

def readCSV(path):
    return pandas.read_csv(path, header=None).iloc

if __name__ == '__main__':
    #print(readCSV('data/Movie_id.csv')[1,0])
    print(readMap()['1291544'])
    readZip()