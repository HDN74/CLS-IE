# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Đặng Nhật Huy, Bùi Tiến Thành
# Title: _info_extraction.py
# Date: 2024/01/31 11:28:56
# Description: File chứa các hàm liên quan đến Dependency Parsing cho bóc tách thông tin
# 
# (c) 2023-2024 CMC ATI. All rights reserved.
# -----------------------------------------------------------------------------------------------
import pandas as pd


# -----------------------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------------------
def determine_category(self, df_special_verb):
    df = self.DP
    dictCategory = {}
    special_verb_index_set = []
    for index, value in enumerate(df_special_verb.Index):
        special_verb_index_set.append(value)
    for i in range(len(df)):
        dictCategory[i] = ''
    for i in range(len(df)):
        pos_tag = df['Pos_Tag'][i]
        if i in special_verb_index_set:
            if len(df_special_verb[df_special_verb.Index == i].Category) == 1:
                dictCategory[i] = df_special_verb[df_special_verb.Index == i].iloc[0].Category
            if len(df_special_verb[df_special_verb.Index == i].Category) == 2:
                if pos_tag == 'V':
                    dictCategory[i] =  df_special_verb[df_special_verb.Index == i].iloc[0].Category
                if pos_tag == 'N':
                    dictCategory[i] =  df_special_verb[df_special_verb.Index == i].iloc[1].Category
    return dictCategory



# -----------------------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------------------
def determine_level(self, dictPhanCap):
    dictLevel = {}
    for key, value in dictPhanCap.items():
        for j in value: 
            dictLevel[j] = key
    return dictLevel



# -----------------------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------------------
def find_support_words(self):
    """
        Output: Tạo ra 1 dictionary bao gồm: 1 từ trong câu và các từ bổ trợ cho nó 
    """
    dp = self.DP
    dictSupportWords = {}
    for i in range(len(dp)):
        dictSupportWords[dp['Index'][i]] = []
    for i in range(len(dp)):
        if dp['Label'][i] == 'root':
            continue
        if dp['Head_Index'][i] not in dictSupportWords:
            continue
        dictSupportWords[dp['Head_Index'][i]].append(dp['Index'][i])
    return dictSupportWords



# -----------------------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------------------
def give_information_for_words(self, dictSupportWords, dictPhanCap):
    df = self.DP
    information = {}
    for i in range(len(df)):
        information[i] = []    
    for i in reversed(range(len(dictPhanCap))):
        for j in dictPhanCap[i]:
            for k in dictSupportWords[j]:
                if df['Word'][k] == '':
                    continue
                information[j].append(k)
                for l in information[k]:
                    information[j].append(l)
    for i in range(len(df)):
        information[i].append(i)
        information[i] = sorted(information[i])
    return information

    

# -----------------------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------------------
def give_object(self, DP):
    object = []
    target_sentence = []
    bol = {}
    for i in range(len(DP)):
        bol[i] = False
    for i in range(len(DP)):
        label = DP['Label'][i]
        index = DP['Index'][i]
        word = DP['Word'][i]
        level = DP['Level'][i]
        category = DP['Category'][i]
        if (label == 'dob' or label == 'iob' or label ==  'pob' or label == 'sub') and bol[i] == False:
            infor = DP['InformationWords'][i]
            #str = DP['Head'][i] + " "
            str = " "
            bol[i] = True
            for j in infor: 
                bol[j] = True
                str = str + DP[DP.Index == j].iloc[0].Word + " "
            object.append([label, index, word, str, level, category])
            target_sentence.append(str)
    df = pd.DataFrame(object, columns = ["Label", "Index", "Word", "Information", "Level", "Category"])
    return df
    
    
# -----------------------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------------------
def information_extraction(self, DP):
    level = self.DP_PhanCap
    result = []
    for index, value in reversed(level.items()):
        for i in value:             
            for j in DP['SupportWords'][i]:
                category_information = DP[DP.Index==j].iloc[0].Category

                
                information = ""
                for k in DP['InformationWords'][j]:
                    information = information + DP['Word'][k] + " "
                word = ""
                for h in DP['InformationWords'][i]:
                    if i < j:
                        if h < j:
                            word = word + DP[DP.Index == h].iloc[0].Word + " "
                    if i > j:
                        if DP['InformationWords'][j][len(DP['InformationWords'][j])-1] < h:
                            word = word + DP[DP.Index == h].iloc[0].Word + " "
                result.append([DP['Level'][i], i, j, DP['Word'][i], DP['Word'][j], DP['Pos_Tag'][i], DP['Pos_Tag'][j], DP['Category'][i], DP['Category'][j], DP['Label'][j] , word, information])
    df = pd.DataFrame(result, columns = ['Level','Head_Index', 'Information_Index', 'Head_Word','Information_Word', 'Head_PosTag', 'Information_PosTag','Head_Category','Information_Category', 'DP_Label','Head','Information'])            
    return df
