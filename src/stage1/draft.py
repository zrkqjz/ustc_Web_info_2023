import jieba
import readData

def split_compare():
    string = '麻省理工学院的数学教授蓝波在席上公布了一道困难的数学题，却被年轻的清洁工威尔（马特·戴蒙 饰）解了出来。'
    seg_list = jieba.cut_for_search(string, HMM=False)
    seg_list = ','.join(seg_list)
    print(string)
    print('cut for search without HMM:'+seg_list)
    
    seg_list = jieba.cut_for_search(string, HMM=True)
    seg_list = ','.join(seg_list)
    print('cut for search with HMM:'+seg_list)

    seg_list = jieba.cut(string, cut_all=True)
    seg_list = ','.join(seg_list)
    print('cut all:'+seg_list) 

def draw_graph():
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    from matplotlib.font_manager import FontProperties   #显示中文，并指定字体
    myfont=FontProperties(fname=r'C:/Windows/Fonts/simhei.ttf',size=14)
    sns.set(font=myfont.get_name())
    plt.rcParams['axes.unicode_minus']=False      #显示负号

    x = np.array([])
    inverted_index = readData.readJSON('data\movie_inverted_index.json')
    count = 0
    for entry in inverted_index:
        l = len(inverted_index[entry])
        x = np.append(x,l)
        count += l
    x = x[x < 30]
    print('average length of movie: ',count/len(inverted_index))

    y = np.array([])
    inverted_index = readData.readJSON('data\\book_inverted_index.json')
    count = 0
    for entry in inverted_index:
        l = len(inverted_index[entry])
        y = np.append(y,l)
        count += l
    y = y[y < 30]    
    print('average length of book: ', count/len(inverted_index))

    plt.rcParams['figure.figsize'] = (13, 5)    #设定图片大小
    f = plt.figure()                            #确定画布

    f.add_subplot(1,2,1)
    sns.histplot(x, stat='percent')                 #绘制频数直方图
    plt.ylabel("百分比", fontsize=16)
    plt.xticks(fontsize=16)                    #设置x轴刻度值的字体大小
    plt.yticks(fontsize=16)                   #设置y轴刻度值的字体大小
    plt.title("(movie)", fontsize=20)             #设置子图标题

    f.add_subplot(1,2,2)
    sns.histplot(y, stat='percent')                
    plt.ylabel("百分比", fontsize=16)
    plt.xticks(fontsize=16)                  #设置x轴刻度值的字体大小
    plt.yticks(fontsize=16)                  #设置y轴刻度值的字体大小
    plt.title("(book)", fontsize=20)            #设置子图标题
    
    plt.subplots_adjust(wspace=0.3)         #调整两幅子图的间距
    plt.show()

def longest_keyword():
    maxLen = 0
    maxKw = ''
    inverted_index = readData.readJSON('data\movie_inverted_index.json')
    for entry in inverted_index:
        l = len(entry)
        if l > maxLen:
            maxLen = l
            maxKw = entry
    print(maxLen)
    print(maxKw)

def skipList_compare():
    import random
    import timeit
    import sys
    class ListNode:
        def __init__(self, data = None):
            self._data = data
            self._forwards = []   # 存放类似指针/引用的数组，占用空间很小
    class SkipList:
        _MAX_LEVEL = 4 

        def __init__(self):
            self._level_count = 1
            self._head = ListNode()
            self._head._forwards = [None] * self._MAX_LEVEL

        def _random_level(self, p = 0.5):
                level = 1
                while random.random() < p and level < self._MAX_LEVEL:
                    level += 1
                return level
        
        def insert(self, value):
            '''
            插入一个结点，成功返回 True 失败返回 False
            '''
            level = self._random_level()
            if self._level_count < level: self._level_count = level
            new_node = ListNode(value)
            new_node._forwards = [None] * level
            update = [self._head] * level     # update 保存插入结节的左边的节点

            p = self._head
            for i in range(level - 1, -1, -1):
                while p._forwards[i] and p._forwards[i]._data < value:
                    p = p._forwards[i]
                if p._forwards[i] and p._forwards[i]._data == value:
                    #说明已经存储该节点，不需要再插入
                    return False 
                update[i] = p     # 找到插入的位置

            for i in range(level):
                new_node._forwards[i] = update[i]._forwards[i]   # new_node.next = prev.next
                update[i]._forwards[i] = new_node     # prev.next = new_node
            return True

        def delete(self, value):
            update = [None] * self._level_count
            p = self._head
            for i in range(self._level_count - 1, -1, -1):
                while p._forwards[i] and p._forwards[i]._data < value:
                    p = p._forwards[i]
                update[i] = p

            if p._forwards[0] and p._forwards[0]._data == value:
                for i in range(self._level_count - 1, -1, -1):
                    if update[i]._forwards[i] and update[i]._forwards[i]._data == value:
                        update[i]._forwards[i] = update[i]._forwards[i]._forwards[i]     # Similar to prev.next = prev.next.next
                return True
            else:
                return False
            
        def find(self, value):
            '''
            查找一个元素，返回一个 ListNode 对象
            '''
            p = self._head
            for i in range(self._level_count - 1, -1, -1):   # Move down a level
                while p._forwards[i] and p._forwards[i]._data < value:
                    p = p._forwards[i]   # Move along level
                if p._forwards[i] and p._forwards[i]._data == value:
                    return p._forwards[i]
            #到这一步，说明没有找到
            return None
        
        def pprint(self):
            '''
            打印跳表
            '''
            skiplist_str = ''
            i = self._level_count -1 
            while i >= 0:
                p = self._head
                skiplist_str = f'head {i}: '
                while p:
                    if p._data:
                        skiplist_str += '->' + str(p._data)
                    p = p._forwards[i]
                print(skiplist_str)
                i -= 1
        def size(self):
            result = 0
            i = self._level_count -1 
            while i >= 0:
                p = self._head
                while p:
                    result += sys.getsizeof(p)
                    p = p._forwards[i]
                i -= 1
            return result

    def merge_with_skipList(left, right):
        result = []
        left_level_count = left._level_count
        right_level_count = right._level_count
        left = left._head
        right = right._head
        while left and right:
            if left._data == right._data:
                result.append(left._data)
                left = left._forwards[0]
                right = right._forwards[0]
            elif left._data < right._data:
                for i in range(left_level_count - 1, -1, -1):
                    while left._forwards[i] and left._forwads[i]._data < right._data:
                        left = left._forwards[i]
                    if left._forwards[i] and left._forwards[i]._data == right._data:
                        result.append(left._data)
                        left = left._forwards[0]
                        right = right._forwards[0]
                        break
            else:
                for i in range(right_level_count - 1, -1, -1):
                    while right._forwards[i] and right._forwads[i]._data < left._data:
                        right = right._forwards[i]
                    if right._forwards[i] and right._forwards[i]._data == left._data:
                        result.append(left._data)
                        left = left._forwards[0]
                        right = right._forwards[0]
                        break                
                
    set1 = SkipList()
    inverted_index = readData.readJSON('data\movie_inverted_index.json')
    for k in inverted_index['尼克']:
        set1.insert(k)
    set1.pprint()
    
    start = timeit.default_timer()
    temp = set1.find(219)
    end = timeit.default_timer()
    print('size of skipList:', set1.size())
    print('time to find with skipList:',end - start)

    set2 = set(inverted_index['尼克'])
    start = timeit.default_timer()
    if 219 in set2:
        temp = 219
    end = timeit.default_timer()

    print('size of set:', sys.getsizeof(set2))
    print('time to find with set:',end - start)

def zip_compare():
    import sys

    class zipList:
        def __init__(self):
            self.data = []
        
        def insert(self, value):
            if self.data == []:
                self.data.append(value)
            else:
                value = value - self.data[-1]
                self.data.append(value)
        
        def search(self, value):
            temp = 0
            for i in range(len(self.data)):
                if temp == value:
                    return temp
                else:
                    temp += self.data[i]
            return False
        
        def size(self):
            result = 0
            for i in self.data:
                result += sys.getsizeof(i)
            return result
        
    myList = zipList()
    inputList = [0,112,210,434,508,593,688] #‘救赎’对应的文档表
    for i in inputList:
        myList.insert(i)

    print('result for search 112:',myList.search(112))
    print('size of my List:',myList.size())
    print('size of python list:',sys.getsizeof(inputList))
                

if __name__ == '__main__':
    draw_graph()

