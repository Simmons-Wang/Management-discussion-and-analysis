import pandas as pd
import numpy as np
import os
import re
from tqdm import tqdm
import random


# %% 导入基础数据
# casual list 1
data_reason = pd.read_excel('C:\\Users\\Simmons\\PycharmProjects\\sec\\data\\reasoning words.xlsx')
reason_words1 = [ ]
for col in data_reason.columns:
    x = list(data_reason[ col ])
    reason_words1.extend(x)

while np.nan in reason_words1:
    reason_words1.remove(np.nan)

# person list
data_person = pd.read_excel('C:\\Users\\Simmons\\PycharmProjects\\sec\\data\\person pronouns.xlsx')

first_person = list(data_person[ 1 ])[ 0:12 ] + list(data_person[ 2 ])[ 0:15 ]
other_person = list(data_person[ 3 ])

# casual list 2
data_reason2 = pd.read_excel('C:\\Users\\Simmons\\PycharmProjects\\sec\\data\\reasoning words 2.xlsx')

reason_words2 = list(data_reason2[0])

# expense-related words
er_list = [ 'amortization', 'cost', 'depreciation', 'disposition', 'expense', 'research and development', 'R&D',
            'impairment', 'loss', 'write off'
            ]

# income-related word
ir_list = [ 'EBIT', 'EBITDA', 'income', 'sale', 'revenue', 'profit', 'margin', 'benefit',
            'break-even', 'contribution', 'EPS', 'return' ]

# ‘financial performance’ items
ie_list = er_list + ir_list
# %% 定义函数
# 分段

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


def split_par(text):
    lines = text.splitlines()
    lens = [ len(l) for l in lines ]
    paras = [ ]
    para_end = 0
    for n in range(1, len(lines) - 1):
        if (lens[ n ] < lens[ n - 1 ]) and (lens[ n ] < lens[ n + 1 ]) and lines[ n ] != '' and lines[ n ][ -1 ] == '.':
            paras.append(''.join(lines[ para_end: n + 1 ]))
            para_end = n + 1
    return paras


# 找到相关段落
def find_related(text):
    pars = split_par(text)
    related_pars = [ ]
    for p in pars:
        if any(key in p for key in ie_list):
            related_pars.append(p)
        else:
            pass
    related_Par = ''.join(related_pars)
    return related_Par


def dot_replace(s=''):
    s = s.replace('i.e', 'ie')
    s = s.replace('U.S', 'US')
    s = s.replace('No.', 'number')
    s = s.replace('Corp.', 'corporation')
    s = s.replace('et al.', 'et al')
    return s


def my_tokenisation(text):
    for ch in '!"#$&()*+,-./:;<=>?@[\\]^_{|}·~‘’':
        text = text.replace(ch, " ")
    text = text.lower()
    words = text.split()
    return words


def count_words(tokens, words_list):
    num = 0
    for i in words_list:
        add = tokens.count(i)
        num += add

    return num


# 计算相关句子的数量
def count_sen(s='', casual_list=[ ], forward=False, option='all'):
    # if forward:
    #     if s == s and s != 'nan':
    #         year = year_dict[ s ]
    #         words_list.append(str(year))
    #     else:
    #         pass
    # else:
    #     pass
    sen_lists = s.split('.')
    num_out = 0
    for sen in sen_lists:
        if any(reason in sen for reason in casual_list):
            if option == 'first':
                if any(pron in sen for pron in first_person) and any(
                        pron in sen for pron in other_person) is False:
                    num_out += 1
            elif option == 'other':
                if any(pron in sen for pron in other_person):
                    num_out += 1
            # if (option == 'operations') and any(pron in sen for pron in operations):
            #     num_op += 1
            # if (option == 'finance') and any(pron in sen for pron in finance):
            #     num_fin += 1
            # if (option == 'accounting') and any(pron in sen for pron in accounting):
            #     num_acc += 1
            else:
                num_out += 1
        else:
            pass
    return num_out



# %% main
if __name__ == '__main__':
    allpath = [ ]
    allname = [ ]
    path_list, file_name_list = getallfile(r'D:\sec-files_removehtml')

    result_list = []
    for p, file in tqdm(zip(path_list[5208:], file_name_list[5208:])):

        text = dot_replace(open(p, "r", errors='ignore').read())
        related_text = find_related(text)
        tokens = my_tokenisation(text)
        para_tokens = my_tokenisation(related_text)
        total_words_num = len(tokens)
        target_words = count_words(tokens, reason_words1)
        ser = pd.Series({
            'cik': file.replace('.txt', '').split('_')[0],
            'year': file.replace('.txt', '').split('_')[1],
            'reasoning words 1': count_words(tokens, reason_words1),
            'reasoning words 2': count_words(tokens, reason_words2),
            'total_words': len(tokens),
            'para reasoning words 1': count_words(para_tokens, reason_words1),
            'para reasoning words 2': count_words(para_tokens, reason_words2),
            'para total_words': len(para_tokens),
            'total_sentences': len(text.split('.')),
            'para total_sentences': len(related_text.split('.')),
            'para reasoning sentences 1': count_sen(related_text, casual_list=reason_words1, option='all'),
            'para f-reasoning sentences 1': count_sen(related_text, casual_list=reason_words1, option='first'),
            'para o-reasoning sentences 1': count_sen(related_text, casual_list=reason_words1, option='other'),
            'para reasoning sentences 2': count_sen(related_text, casual_list=reason_words2, option='all'),
            'para f-reasoning sentences 2': count_sen(related_text, casual_list=reason_words2, option='first'),
            'para o-reasoning sentences 2': count_sen(related_text, casual_list=reason_words2, option='other'),
            'reasoning sentences 1': count_sen(text, casual_list=reason_words1, option='all'),
            'f-reasoning sentences 1': count_sen(text, casual_list=reason_words1, option='first'),
            'o-reasoning sentences 1': count_sen(text, casual_list=reason_words1, option='other'),
            'reasoning sentences 2': count_sen(text, casual_list=reason_words2, option='all'),
            'f-reasoning sentences 2': count_sen(text, casual_list=reason_words2, option='first'),
            'o-reasoning sentences 2': count_sen(text, casual_list=reason_words2, option='other'),
        })

        ser['para n-reasoning sentences 1'] = ser['para reasoning sentences 1'] - ser['para f-reasoning sentences 1'] - ser['para o-reasoning sentences 1']
        ser['para n-reasoning sentences 2'] = ser['para reasoning sentences 2'] - ser['para f-reasoning sentences 2'] - ser['para o-reasoning sentences 2']
        ser['n-reasoning sentences 1'] = ser['reasoning sentences 1'] - ser['f-reasoning sentences 1'] - ser['o-reasoning sentences 1']
        ser['n-reasoning sentences 2'] = ser['reasoning sentences 2'] - ser['f-reasoning sentences 2'] - ser['o-reasoning sentences 2']

        ser.sort_index(inplace=True)
        result_list.append(ser)


    result_df = pd.concat(result_list, axis=1).T
    result_df['year'] = '20' + result_df['year']
    result_df.columns = [c.replace('-', '').replace(' ', '') for c in result_df.columns]

    past_result = pd.read_csv(r'C:\Users\Simmons\PycharmProjects\sec\mda causal 2020.csv')
    past_result['cik'] = past_result['cik'].apply(lambda x: str(x).zfill(10))
    merged_result = past_result.append(result_df)
    merged_result['cik'] = merged_result['cik'].astype('str')
    merged_result.sort_values(by=['cik', 'year'], inplace=True)
    merged_result.to_csv(r'C:\Users\Simmons\PycharmProjects\sec\mda causal 20211115.csv', index=None)



#
# data_forward = pd.read_excel('C:\\Users\\Simmons\\PycharmProjects\\sec\\data\\forward_looking words.xlsx',
#                              encoding='gbk')
#
# for_looking_words = list(data_forward[ 1 ]) + list(data_forward[ 2 ])
# del for_looking_words[ 43: ]