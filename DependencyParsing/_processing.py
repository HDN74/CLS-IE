# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Bùi Tiến Thành, Đặng Nhật Huy
# Title: _processing.py
# Date: 2024/01/31 11:35:06
# Description: File chứa các hàm liên quan xử lý chính cho Dependency Parsing
# 
# (c) 2023-2024 CMC ATI. All rights reserved.
# -----------------------------------------------------------------------------------------------


import numpy as np
import pandas as pd
import logging
import Utils.NLPHelper

    
def make_DP(self, sentence, dp_data):

    # Phần này xử lý cả trường hợp dữ liệu về DP đã có sẵn hoặc chưa có
    if dp_data is None:
        logging.warning(f"Sử dụng NLP để phân tích câu: {sentence}")
        word, pos_tag, index, label = Utils.NLPHelper.phonlp_annotate(sentence)
    else:
        word, pos_tag, index, label = dp_data['word'], dp_data['pos_tag'], dp_data['index'], dp_data['label']

    # logging.error(word)
    # logging.error(pos_tag)
    # logging.error(index)
    # logging.error(label)

    dp_set = []
    for i in range(len(word)):
        if label[i] == 'root':
            dp_set.append([i, word[i], pos_tag[i], "", "",label[i]])
        else:
            dp_set.append([i, word[i], pos_tag[i], int(index[i])-1, word[int(index[i])-1], label[i]])
    dataframe = pd.DataFrame(dp_set, columns = ['Index', 'Word', 'Pos_Tag', 'Head_Index', 'Head', 'Label'])
    return dataframe


    
def update_DP(self):
    self.DP_SupportWords = self.find_support_words()
    self.DP_PhanCap = self.phan_cap_DP(self.DP_SupportWords)
    self.DP_InformationWords = self.give_information_for_words(self.DP_SupportWords, self.DP_PhanCap)
    self.DP_Category = self.determine_category(self.special_verb_set)
    self.DP_Level = self.determine_level(self.DP_PhanCap)
    DP = self.DP


    DP['SupportWords'] = ''
    DP['InformationWords'] = ''
    DP['Category'] = ''
    DP['Level'] = '' 
    
    max_allowed_length = DP.shape[0]
    try:
        for i in self.DP_SupportWords.keys():
            if i >= max_allowed_length: continue
            DP['SupportWords'][int(i)] = self.DP_SupportWords[i]

        for i in self.DP_InformationWords.keys():
            if i >= max_allowed_length: continue
            DP['InformationWords'][int(i)] = self.DP_InformationWords[i]

        for i in self.DP_Category.keys():
            if i >= max_allowed_length: continue
            DP['Category'][int(i)] = self.DP_Category[i]

        for i in self.DP_Level.keys():
            if i >= max_allowed_length: continue
            DP['Level'][int(i)] = self.DP_Level[i]
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        pass

    self.DP = DP
    return DP


def phan_cap_DP(self, dictSupportWords):
    if isinstance(self.root, list): cap_bac = {0:self.root}
    else: cap_bac = {0:[self.root]}
    cnt = 0
    while len(cap_bac[cnt]) != 0:
        cnt = cnt + 1
        cap_bac[cnt] = []
        for i in cap_bac[cnt-1]:
            for j in dictSupportWords[i]:
                cap_bac[cnt].append(j)
    return cap_bac



def lay_thong_tin_cho_root(self):
    # Khởi tạo kết quả trả về
    result =  {
        "sub":      [],
        "mainverb": [],
        "ml":       [],
        "dob":      [],
        "iob":      [],
        "pob":      [],
        "vmod":     [],
        "nmod":     [],
        "tmp":      [],
        "loc":      [],
        "prp":      [],
        "mnr":      [],
        "adv":      [],
        "coord":    [],
        "det":      [],
        "dep":      []
    }

    # Ta kiểm tra xem cây có root không, nếu không thì trả về kết quả rỗng. Việc này sẽ tránh code dài dòng ở các task dưới
    if(self.empty): return result


    # Cập nhật DP
    df = self.update_DP()
    dictSupportWords = self.DP_SupportWords
    dictInformationWords = self.DP_InformationWords
    # Ta không cần kiểm tra empty do đã kiểm tra ở trên, do đó ở bước này vt chắc chắc không rỗng
    vt = df[df.Index == self.root].iloc[0]
    result['mainverb'] = [vt.Word]


    for i in dictSupportWords[self.root]:
        label = df[df.Index == i].iloc[0].Label
        text = ""
        for j in dictInformationWords[i]:
            text = text + df[df.Index == j].iloc[0].Word + " " 
        if  df[df.Index == i].iloc[0].Word == '' or len(df[df.Index == i].iloc[0].Word) < 2:
            continue
        if label in result.keys():
            # Ta đảm bảo các xâu trả về đã được xử lý "sạch", đồng thời các nhãn phải có trong dict 
            result[label].append(str(text).strip())

    return result

    