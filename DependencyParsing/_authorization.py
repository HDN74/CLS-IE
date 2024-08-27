# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Đặng Nhật Huy, Bùi Tiến Thành
# Title: _authorization.py
# Date: 2024/01/31 11:25:41
# Description: File chứa các hàm liên quan đến Dependency Parsing cho phân quyền
# 
# (c) 2023-2024 CMC ATI. All rights reserved.
# -----------------------------------------------------------------------------------------------

import logging
import numpy as np
import pandas as pd
import networkx as nx
from typing import List, Dict, Tuple, Union

# -----------------------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------------------
def calculate_tree(self, DP, s, t):
    edges = []
    for i in range(len(DP)):
        for j in DP['SupportWords'][i]:
            edges.append((i,j))
    #print(edges)   
    G = nx.Graph()
    G.add_edges_from(edges)
    #pos = nx.spring_layout(G)  # Xác định vị trí các nút trên đồ thị
    #nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', font_weight='bold')
    #plt.show()
    try:
        path_length = nx.shortest_path_length(G, source = s, target = t)
        shortest_path = nx.shortest_path(G, source = s, target = t)
        return path_length, shortest_path
    except nx.NetworkXNoPath:
        return "No path between source and target"



# -----------------------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------------------
def check_noi_dung(self, DP, nd1, nd2):
    min_score = 1000     
    rows = []  
    if nd1 == [] and nd2 != []:
        for i in nd2: 
            rows.append(['', '', DP['Word'][i]])
    else: 
        for i in nd1: 
            for j in nd2: 
                kq = self.calculate_tree(DP, i, j)
                if kq == 'No path between source and target':
                    continue
                else: 
                    dodai = kq[0]
                if dodai <= 5:
                    str1 = ""
                    str2 = ""
                    for k in DP['InformationWords'][i]:
                        word = DP[DP.Index == k].iloc[0].Word 
                        str1 = str1 + word + " "

                    word = DP[DP.Index == j].iloc[0].Word 
                    rows.append([dodai, str1, word])
                    if min_score > dodai: 
                        min_score = dodai
    #print(rows)
    #result_dataframe = pd.DataFrame(rows, columns = ["Score", "Chu the", "Dong tu tham quyen"]) 
    if min_score == 1000: 
        min_score = ''
    return rows, min_score



# -----------------------------------------------------------------------------------------------
# 
# -----------------------------------------------------------------------------------------------
def check_quy_dinh_phan_quyen(self, DP):
    # DP = self.update_DP()
    dict = {}
    for i in range(len(DP)):
        index = DP['Index'][i]
        category = DP['Category'][i]
        level = DP['Level'][i]
        postag = DP['Pos_Tag'][i]
        word = DP['Word'][i]
        if category == 'Thẩm quyền':
            dict[i] = [level, word, category]
        if category == 'Chủ thể ban hành':
            dict[i] = [level, word, category]
        if category == 'Chủ thể tham gia':
            dict[i] = [level, word, category]
        if category == 'Quyền hạn':
            dict[i] = [level, word, category]
    ctbh = []
    tq = []
    cttg = []
    qh = []
    for index, value in dict.items(): 
        if value[2] == 'Chủ thể ban hành':
            ctbh.append(index)
        if value[2] == 'Thẩm quyền':   
            tq.append(index)
        if value[2] == 'Chủ thể tham gia':
            cttg.append(index)
        if value[2] == 'Quyền hạn':
            qh.append(index)
    #print(ctbh, qh)
    result_tqbh, min_score_tqbh = self.check_noi_dung(DP, ctbh, tq)                  
    result_tqnd, min_score_tqnd = self.check_noi_dung(DP, ctbh, qh)
    return result_tqbh, result_tqnd, min_score_tqbh  

# def extract_agency_authority_jurisdiction(
#     self, 
#     compare_sentences  
# ):
#     DP = self.DP
#     result_tqbh , _ , _ = self.check_quy_dinh_phan_quyen(DP)
#     df = self.give_object(DP)
#     kq_chu_de = {
#         "chu_the": [],
#         "chu_de": [],
#         "dong_tu": []
#     }
#     print(df)
#     for i in range(len(df)):
#         information = df['Information'][i]
#         w2v = self.find_similarity(information, compare_sentences)
#     print(w2v)
# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------
def extract_agency_authority_jurisdiction(
    self, 
    compare_sentences
) -> Tuple[List[Dict[str, str]], Dict[str, List[str]]]:
    DP = self.DP 
    r_tqbh, r_tqnd, min_score = self.check_quy_dinh_phan_quyen(DP)   
    df = self.give_object(DP)
    
    kq_chu_de = {
        "chu_the": [],
        "chu_de": [],
        "dong_tu": []
    }
    dict_test = {}
    for i in r_tqbh: 
        dict_test[i[1]] = False
        dict_test[i[2]] = False
    for i in r_tqnd: 
        dict_test[i[1]] = False
        dict_test[i[2]] = False    
    for i in r_tqbh: 
        if dict_test[i[1]] == False and i[1] != '':
            kq_chu_de['chu_the'].append(i[1])
            dict_test[i[1]] = True
        if dict_test[i[2]] == False and i[2] != '':
            kq_chu_de['dong_tu'].append(i[2])
            dict_test[i[2]] == True
    for i in r_tqnd: 
        if dict_test[i[1]] == False and i[1] != '':
            kq_chu_de['chu_the'].append(i[1])
            dict_test[i[1]] = True
            print(i[1])
        if dict_test[i[2]] == False and i[2] != '':
            kq_chu_de['dong_tu'].append(i[2])
            dict_test[i[2]] == True
    
    cnt = 0
    
    for i in range(len(df)): 
        information = df['Information'][i]
        category = df['Category'][i]
        if category == '':
            w2v = self.find_similarity(information, compare_sentences)
            if w2v == []:
                continue
            if w2v[0]['score'] > 0.4: 
                cnt = cnt + 1
                kq_chu_de['chu_de'].append(information)
    # for i in range(len(df)): 
    #     information = df['Information'][i]
        
    #     category = df['Category'][i]
    #     w2v = self.find_similarity(information, compare_sentences)
        
    #     if w2v == []:
    #         continue
    #     if w2v[0]['score'] > 0.4: 
    #         cnt = cnt + 1
    #         kq_chu_de['chu_de'].append(information)    
    
    if cnt == 0: 
        for i in range(len(df)): 
            information = df['Information'][i]
            category = df['Category'][i]
            if category == '':
                kq_chu_de['chu_de'].append(information)
         
    # if len(dict_higher_element) != 0:
    #     if dict_higher_element['chu_the'] != []:
    #         high = dict_higher_element['chu_the']
        
    #         for k in high:
    #             if k != '':
    #                 kq_chu_de['chu_the'].append(k)
    print(kq_chu_de['chu_de'])      
    
    kq_tham_quyen = []
    for i in kq_chu_de['chu_the']:
        for j in kq_chu_de['chu_de']:
            kq_tham_quyen.append({
                "chu_the": i,
                "chu_de": j 
            })  
    return kq_tham_quyen, kq_chu_de
