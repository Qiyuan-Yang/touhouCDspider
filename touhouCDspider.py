import requests
from bs4 import BeautifulSoup
import bs4
import re
import time
from multiprocessing import Pool
import sys   

 
def getHtmlText(url, code="utf-8"): 
    #a simple modul to get html text
    try:
        r = requests.get(url,headers = {'user-agent':'Mozilla/5.0'})
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return ''

def getAlbumHtml(url,startAlbum = '"Activity" Case：01 -Graveyard Memory-'): 
    #to get the html text in album pages
    html = getHtmlText(url+startAlbum)
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all('div'):
        if tag.get('class') == ['mw-category-generated']:
            return(tag)

def generateAlbumList(albumList,startAlbum = '"Activity" Case：01 -Graveyard Memory-'):
    #to get album names in album pages
    for title in getAlbumHtml('https://thwiki.cc/index.php?title=分类:同人专辑&pagefrom=',startAlbum).find_all('a'):
        if title.string == '上一页' or title.string == '下一页':
            continue
        else:
            albumList.append(title.string)

def exportAlbumInfo(startAlbum = '"Activity" Case：01 -Graveyard Memory-',mode = 0):
    #actually the main function
    albumList = []
    generateAlbumList(albumList,startAlbum)
    if mode == 1:
        f = open('C:/albumLocalData.txt','w',encoding='utf-8')
    elif mode == 0:
        f = open('C:/albumLocalData.txt','a',encoding='utf-8')
    #an additional modul to make a prograss bar
    count = 0
    scale = 50
    start = time.perf_counter()
    print("执行开始 start processing".center(scale//2, "-"))
    #try to traverse all album pages
    while len(albumList) > 1:
        a = '*' * int(count/1.1)
        b = '.' * (scale - int(count/1.1))
        c = (int(count/1.1)/scale)*100
        dur = time.perf_counter() - start
        print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c,a,b,dur),end='')
        count += 1
        #try to get all vocal/music in each album
        if startAlbum == '"Activity" Case：01 -Graveyard Memory-':
            albumList = albumList
        else:
            del albumList[0]
        if mode == 1:
            for i in range(len(albumList)):
                f.write(albumList[i]+'\n')
        elif mode == 2:
            with Pool() as pool:
                pool.map(getAlbumInfo,albumList)
        startAlbum = albumList[-1]
        albumList = []
        generateAlbumList(albumList,startAlbum)
    if mode == 1:
        f.close()
    #the additional modul of prograss bar to make sure it stop at 100%
    a = '*' * 50
    b = '.' * (scale - 50)
    c = (50/scale)*100
    dur = time.perf_counter() - start
    print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c,a,b,dur),end='')
    print("\n"+"执行结束 end processing".center(scale//2,'-'))


def getAlbumInfo(albumName):
    #actually the most useful function
    #it contain the function to get all vocal/music and the function to make a output
    infoFile = open('C:/musicLocalData.txt','a',encoding='utf-8')
    albumUrl = 'https://thwiki.cc/'
    html = getHtmlText(albumUrl+albumName)
    soup = BeautifulSoup(html, 'html.parser')
    singleInfo = {}
    singleInfo['专辑名'] = albumName
    publisher = []
    for tag in soup.find_all('table'):
        if tag.get('class') == ['wikitable','doujininfo']:
            for tr in tag.find_all('tr'):
                try:
                    for td in tr.find_all('td'):
                        try:
                            for a in td.find_all('a'):
                                if a.get('title') == a.string or a.get('title') == a.string+'（页面不存在）':
                                    publisher.append(a.string)
                        except:
                            continue
                except:
                    continue
        if tag.get('class') == ['wikitable', 'musicTable']:
            for item in tag.find_all('tr'):
                if len(publisher) == 1:
                    singleInfo['制作方'] = publisher[0]
                elif publisher != []:
                    singleInfo['制作方'] = publisher[(len(publisher)-1)//2]
                try:
                    #get the title of each single
                    a = item.b.string
                    if a in '0102030405060708091121314151617181922324252627282933435363738394454647484955657585966768697787988990':
                        if item.a.string == None:
                            for j in item.find_all('td'):
                                pattern = '>(.*?)<span'
                                singleName = re.search(pattern,str(j))
                                if singleName:
                                    singleName = singleName.group(0)[1:-5]
                                    if '\u3000' in singleName:
                                        singleName = singleName.replace('\u3000',' ')
                                    singleInfo['单曲名'] = singleName
                        else:
                            singleName = item.a.string
                            if '\u3000' in singleName:
                                singleName = singleName.replace('\u3000',' ')
                            singleInfo['单曲名'] = singleName
                except AttributeError:
                    for td in item.find_all('td'):
                        if td.string == '编曲':
                            getSingleDetails(singleInfo,item,'编曲')
                        elif td.string == '演唱':
                            getSingleDetails(singleInfo,item,'演唱')
                        elif td.string == '作词':
                            getSingleDetails(singleInfo,item,'作词')
                        elif td.string == '社团':
                            getSingleDetails(singleInfo,item,'社团')
                        elif td.string == '原曲':
                            getSingleDetails(singleInfo,item,'原曲')
                            infoFile.write(str(singleInfo)+'\n')
                            #print(publisher)
                            #print(singleInfo)
                            singleInfo = {}
                            singleInfo['专辑名'] = albumName
                        else:
                            continue
    infoFile.close()



def getSingleDetails(singleInfo,item,type):
    details = []
    for td in item.find_all('td'):
        if td.string == type:
            for label in item.find_all('a'):
                if label.string != None:
                    if '\u3000' in label.string:
                        label.string = label.string.replace('\u3000',' ')
                    details.append(label.string)
                else:
                     continue
    singleInfo[type] = details


def labelMatch(file,label,content,lang = '中文',save = False):
    f = open(file,encoding = 'UTF-8')
    count = 0
    for line in f.readlines():
        try:
            info = eval(line)
            if content in info[label]:
                count += 1
                if lang == '中文':
                    print('第{}个结果'.format(count),end = ':')
                    print('\n{}'.format(info))
                elif lang == 'English':
                    print('The No.{} result'.format(count),end = ':')
                    print('\n{}'.format(info))
                if save == '虾米':
                    f = open('C:/result.txt','a',encoding = 'utf-8')
                    single = info['单曲名']
                    publisher = info['制作方']
                    f.write(str(single)+' '+str(publisher)+'\n')
                    if '演唱' in info: 
                        singers = info['演唱']
                        for singer in singers:
                            f.write(str(single)+' '+str(singer)+'\n')
                    lyrics = info['编曲']
                    for lyric in lyrics:
                        f.write(str(single)+' '+str(lytic)+'\n')
                    if '社团' in info:
                        group = info['社团']
                        f.write(str(single)+' '+str(group)+'\n')
                    f.close()
                elif save == '网易云':
                    f = open('C:/result.txt','a',encoding = 'utf-8')
                    single = info['单曲名']
                    ogmusic = info['专辑名']
                    f.write(str(single)+' '+str(ogmusic)+'\n')
                    f.close()
                elif save:
                    f = open('C:/result.txt','a',encoding = 'utf-8')
                    f.write(str(info)+'\n')
                    f.close()
        except:
            continue



def checkUpdate(file,*lang):
    f = open(file,encoding = 'UTF-8')
    txt = f.read()
    txt = txt.split('\n')
    output = open('C:/updateList.txt','w',encoding = 'UTF-8')
    startAlbum = '"Activity" Case：01 -Graveyard Memory-'
    count = 0
    scale = 50
    start = time.perf_counter()
    print("执行开始 start processing".center(scale//2, "-"))
    albumList = []
    updateList = []
    #start = time.perf_counter()
    generateAlbumList(albumList)
    while len(albumList) > 1:
        for i in range(len(albumList)):
            if i != 0 or startAlbum == '"Activity" Case：01 -Graveyard Memory-':
                if albumList[i] in txt[count:len(txt)]:
                    count += 1
                    bar = int(scale*count/len(txt))
                    a = '*' * bar
                    b = '.' * (scale - bar)
                    c = (count/len(txt))*100
                    dur = time.perf_counter() - start
                    print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c,a,b,dur),end='')
                else:
                    output.write(albumList[i])
                    output.write('\n')
                    updateList.append(albumList[i])
        startAlbum = albumList[-1]
        albumList = []
        generateAlbumList(albumList,startAlbum)
    #the additional modul of prograss bar to make sure it stop at 100%
    a = '*' * 50
    b = '.' * 0
    c = 100
    dur = time.perf_counter() - start
    print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c,a,b,dur),end='')
    print("\n"+"执行结束 end processing".center(scale//2,'-'))
    if updateList == []:
        if lang == '汉语':
            print('无需更新')
        else:
            print('No update')
    else:
        if lang == '汉语':
            print('检查到更新')
        else:
            print('Need update')
    f.close()
    output.close()
    

def getUpdate(file):
    input = open(file,encoding = 'UTF-8')
    txt = input.read()
    txt = txt.split('\n')
    count = 0
    scale = 50
    start = time.perf_counter()
    print("执行开始 start processing".center(scale//2, "-"))
    f = open('C:/musicLocalData.txt','a',encoding='utf-8')
    with Pool() as pool:
        pool.map(getAlbumInfo,txt)
        '''
    for album in txt:
        getAlbumInfo(album)
        count += 1
        bar = int(scale*count/len(txt))
        a = '*' * bar
        b = '.' * (scale - bar)
        c = (count/len(txt))*100
        dur = time.perf_counter() - start
        print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c,a,b,dur),end='')
        '''
    f.close()
    input.close()
    print('更新专辑信息 updating album data')
    exportAlbumInfo(mode = 1)
    print('\n')

def main():
    lang = input('汉语请输入1 for English please key in 2\n')
    if lang == '1':
        ending = '否'
        while ending in '不否':
            module = input('检查更新请输入1 获取更新请输入2 查询信息请输入3 退出请输入0\n')
            if module == '1':
                checkUpdate('C:/albumLocalData.txt','汉语')
            elif module == '2':
                getUpdate('C:/updateList.txt')
            elif module == '3':
                label = input('请输入需要查询的项目（原曲/单曲名/专辑名/演唱/编曲/作词/制作方/社团）\n')
                if label not in '原曲/单曲名/专辑名/演唱/编曲/作词/制作方/社团':
                    print('输入错误\n')
                    break
                content = input('请输入需要查询的内容\n')
                save = input('保存结果\n')
                file = 'C:/musicLocalData.txt'
                labelMatch(file,label,content,'中文',save)
                #searchSingleInfo('C:/musicLocalData.txt',single)
            elif module == 'advance':
                module = input('获取专辑列表请输入1 获取单曲信息请输入2\n')
                if module == '1':
                    exportAlbumInfo(mode = 1)
                elif module == '2':
                    exportAlbumInfo(mode = 2)
            else:
                break
            ending = input('结束？\n')
            if ending == '':
                break
    if lang == '2':
        ending = 'no'
        while ending in 'not':
            module = input("key in '1' for checking update\nkey in '2' for getting update\nkey in '3' for info search\nkey in '0' for exit\n")
            if module == '1':
                checkUpdate('C:/albumLocalData.txt','English')
            elif module == '2':
                getUpdate('C:/updateList.txt')
            elif module == '3':
                label = input('key in the label you want(ogmusic原曲/singleinfo单曲名/albuminfo专辑名/singer演唱/arranger编曲/lyrics作词)\n')
                if label not in '原曲/单曲名/专辑名/演唱/编曲/作词':
                    print('input out of range\n')
                    break
                content = input('key in the content you want to search\n')
                save = input('save result\n')
                file = 'C:/musicLocalData.txt'
                labelMatch(file,label,content,'English',save)
            elif module == 'advance':
                module = input('获取专辑列表请输入1 获取单曲信息请输入2\n')
                if module == '1':
                    exportAlbumInfo(mode = 1)
                elif module == '2':
                    exportAlbumInfo(mode = 2)
            else:
                break
            ending = input('exit?\n')
            if ending == '':
                break




if __name__ == '__main__':
    sys.setrecursionlimit(1000000)
    #exportAlbumInfo('Fragile Sacrifice',2)
    main()
    #albumName = '-Gradation-'
    #getAlbumInfo(albumName)