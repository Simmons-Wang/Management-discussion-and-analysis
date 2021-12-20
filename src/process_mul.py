import html2text
import os
from multiprocessing import Pool
from tqdm import tqdm


def getallfile(path):
    allfilelist=os.listdir(path)
    # 遍历该文件夹下的所有目录或者文件
    for file in allfilelist:
        filepath=os.path.join(path,file)
        # 如果是文件夹，递归调用函数
        if os.path.isdir(filepath):
            getallfile(filepath)
        # 如果不是文件夹，保存文件路径及文件名
        elif os.path.isfile(filepath):
            allpath.append(filepath)
            allname.append(file)
    return allpath, allname


def gettext(path):
    txt = open(path, "r", errors='ignore').read()
    new_t = html2text.html2text(txt)
    lines = new_t.split('\n')
    return lines


def long_time_task(i, path_list):
    print('Run task %s (%s)...' % (i, os.getpid()))
    paths = path_list[i: i+1000]
    for p in tqdm(paths, desc=str(i)):
        p = p.replace('\\', '/')
        new_name = p.split('/')[2] + "_" + p.split('/')[4].split('-')[1]
        try:
            text = gettext(p)
        except :
            print(p)
            continue
        index_start = find_start(text)
        index_end = find_end(text)
        if index_end != index_end:
            index_end = index_start + 5000
        result_text = text[index_start: index_end]
        with open('./sec-files_removehtml/{}.txt'.format(new_name), 'w', encoding='utf-8') as f:
            for l in result_text:
                if len(l) <= 10:
                    continue
                else:
                    f.write(l + '\n')

    print(str(i) + ' is ok')


def my_tokenisation(text):
    for ch in '!"#$&()*+,-./:;<=>?@[\\]^_{|}·~‘’':
        text = text.replace(ch, " ")
    text = text.lower()
    words = text.split()
    return words


def terms_position(q, terms):
    length = len(q)
    if q[0] in terms:
        pos_1 = terms.index(q[0])
        my_judge = list(filter(lambda x: terms.index(q[x]) == pos_1 + x if q[x] in terms else False, list(range(length))))
        if len(my_judge) != length:
            return None
        else:
            return pos_1
    else:
        return None


def find_start(lines):
    result = 0
    for n, l in enumerate(lines):
        if len(l) < 10:
            continue
        tokens = my_tokenisation(l)
        signals = [i in tokens for i in ['item', '7', "management's", 'discussion', 'analysis']]
        if signals.count(True) > 3:
            if ('management' in tokens) and (tokens.index('management') == 0):
                if n > result:
                    result = n
            elif ('item' in tokens) and (tokens.index('item') == 0):
                if n > result:
                    result = n
    return result


def find_end(lines):
    result = 0
    for n, l in enumerate(lines):
        tokens = my_tokenisation(l)
        if (terms_position(['item', '7a'], tokens) == 0) and (len(tokens) > 3):
            if n > result:
                result = n
        elif (terms_position(['item', '8'], tokens) == 0) and (len(tokens) > 3):
            if n > result:
                result = n
    return result


if __name__ == '__main__':
    print('Parent process %s.' % os.getpid())
    os.chdir(r'D:')

    allpath = []
    allname = []
    path_list, file_name_list = getallfile('./sec-edgar-filings')
    print(len(path_list))
    p = Pool(6)

    for i in range(6):
        p.apply_async(long_time_task, args=(int(i * 1000), path_list,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')



