import json

def readData():
    with open('data\data.json', encoding='utf-8') as file:
        dict = json.load(file)
    return dict


def main():
    print(readTxt())

if __name__ == '__main__':
    main()