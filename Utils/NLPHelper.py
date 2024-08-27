import requests
import logging
import json
import re
import pandas as pd
import numpy as np

import config

# Dependency Parsing
def phonlp_annotate(text):
    err = True;
    cnt = 0;
    def unpack_dep_parsing(response):
        if (
            np.any(pd.isnull(response['word'])) or
            np.any(pd.isnull(response['pos_tag'])) or
            np.any(pd.isnull(response['dep_tag'])) or
            not isinstance(response['word'], list) or
            not isinstance(response['pos_tag'], list) or
            not isinstance(response['dep_tag'], list)
        ): return {
            'word': [],
            'pos_tag': [],
            'index': [],
            'label': []
        }



        word = []
        label = []
        index = []
        pos_tag = []
        for w in response['word']:
            if w == '':
                continue
            word.append(w)
        for p in response['pos_tag']:
            pos_tag.append(p[0])
        for l in response['dep_tag']:
            index.append(l[0])
            label.append(l[1])

        return {
            'word': word,
            'pos_tag': pos_tag,
            'index': index,
            'label': label
        }  
            

    while err:
        try:
            response = requests.post(
                url = f"{config.NLP_API_ENDPOINT}/phonlp_annotate",
                json = {
                    'input': text,
                    'is_tokenized': True,
                },
                verify=False
            ).json()['data']
            if cnt > 0: logging.warning(f"Phân tích văn bản thành công sau {cnt} lần thử thất bại");
            err = False
        except Exception as e:
            cnt += 1
            if cnt == 5: 
                logging.error(f"Không thể phân tích văn bản sau {cnt} lần thử thất bại");
                return {
                    'word': [],
                    'pos_tag': [],
                    'index': [],
                    'label': []
                }

    
    
    if isinstance(text, str): 
        response = unpack_dep_parsing(response)
        return response['word'], response['pos_tag'], response['index'], response['label']
    else:
        response = pd.DataFrame.from_dict(response)

        logging.info(f"Chuyển dữ liệu phân tích câu...");
        print() # Print để dòng log tiếp theo không bị cùng dòng với TQDM Progress Bar
        return_value = list(response.progress_apply(unpack_dep_parsing, axis=1))
        print() # Print để dòng log tiếp theo không bị cùng dòng với TQDM Progress Bar
        return return_value



# Segmentize
def segmentize(sentence):
    err = True;
    cnt = 0;

    while err:
        try:
            response = (requests.post(
                url = f"{config.NLP_API_ENDPOINT}/segmentize",
                json = {'input': sentence},
                verify=False
            ).json()['data'])
            if cnt > 0: logging.warning(f"Tokenize văn bản thành công sau {cnt} lần thử thất bại");

            if isinstance(sentence, str): return ' '.join(response)
            else: return pd.Series(response).apply(lambda sentence_pack: ' '.join(sentence_pack))
        except:
            cnt += 1
            # pass



# Strip heading
def deindex(text):
    pattern_phan    = '^((phần(\ )*[IVXABCD0-9]+(\.|\:|\-)*(\ )+)' + '|' + '(phần\ [1|.]+(\ )+))'
    pattern_chuong  = '^((chương|(mẫu\ (số)?))(\ )*[IVXABCD0-9]+(\.|\:|\-)*(\ )*)'
    pattern_muc     = '^(mục(\ )*[I0-9]+(\.|\:|\-)*(\ )*)'
    pattern_dieu    = '^(điều [0-9]+(\.|\,)*(\ )*)'
    pattern_khoan   = '^([0-9]+(\.[0-9]+)*(\.|\ |\-)*)'
    pattern_diem    = '^([a-zđ]+(\ )*(\))?(\.|\:|\-)*(\ )*)'
    

    # phan = re.findall(pattern_phan, text, flags=re.IGNORECASE)
    chuong = re.findall(pattern_chuong, text, flags=re.IGNORECASE)
    muc = re.findall(pattern_muc, text, flags=re.IGNORECASE)
    dieu = re.findall(pattern_dieu, text, flags=re.IGNORECASE)
    khoan = re.findall(pattern_khoan, text, flags=re.IGNORECASE)
    diem = re.findall(pattern_diem, text, flags=re.IGNORECASE)


    if len(chuong) > 0:
        index = chuong[0][0]
        text = re.sub(pattern_chuong, '', text, flags=re.IGNORECASE, count = 1).strip().lower()
        return index, text
    elif len(muc) > 0:
        index = muc[0][0]
        text = re.sub(pattern_muc, '', text, flags=re.IGNORECASE, count = 1).strip().lower()
        return index, text
    elif len(dieu) > 0:
        index = dieu[0][0]
        text = re.sub(pattern_dieu, '', text, flags=re.IGNORECASE, count = 1).strip().lower()
        return index, text
    elif len(khoan) > 0:
        index = khoan[0]
        text = re.sub(pattern_khoan, '', text, flags=re.IGNORECASE, count = 1).strip().lower()
        return index, text
    elif len(diem) > 0:
        index = diem[0]
        text = re.sub(pattern_diem, '', text, flags=re.IGNORECASE, count = 1).strip().lower()
        return index, text
    else: 
        index = ''
    return index, text