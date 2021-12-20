from sec_edgar_downloader import Downloader
import os
import pandas as pd
from tqdm import tqdm
import time
from multiprocessing import Pool


def long_time_task(i, data_need, dl):
    print('Run task %s (%s)...' % (i, os.getpid()))
    df = data_need.iloc[i: i+300]
    for i in tqdm(list(df.index), desc=str(i)):
        cik = df.loc[i,  'cik']
        # if cik in os.listdir('./ouput/sec-edgar-filings'):
        #     continue
        start = '2016-06-30'
        end = '2021-06-30'
        try:
            num = dl.get("10-K", cik, after=start, before=end, download_details=False)
        except :
            print(cik)

        time.sleep(0.1)
    print(str(i) + ' is ok')


if __name__ == '__main__':
    print('Parent process %s.' % os.getpid())
    os.chdir(r'C:\Users\Simmons\PycharmProjects\sec')

    data_need = pd.read_excel('./data/need.xlsx')

    # data_need['start'] = ['2021-06-30'] * len(data_need)
    # data_need['end'] = ['2021-06-30'] * len(data_need)
    data_need['cik'] = data_need['cik'].apply(lambda x: str(x).zfill(10))
    dl = Downloader(r'D:')

    p = Pool(7)

    for i in range(7):
        p.apply_async(long_time_task, args=(int(i * 300), data_need, dl,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
