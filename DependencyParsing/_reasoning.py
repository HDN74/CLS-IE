

# -----------------------------------------------------------------------------------------------
# Author: Đặng Nhật Huy
# Title: _reasoning.py
# Date: 2024/04/09 
# Description: Khởi tạo kiến thức cho quá trình suy diễn
# 
# (c) 2023-2024 CMC ATI. All rights reserved.
# -----------------------------------------------------------------------------------------------
import pandas as pd
from unidecode import unidecode

import owlready2 as owl
onto = owl.get_ontology("http://test.org/onto.owl")

def give_index(chuoi):
    ky_tu_sau_dau_gach = chuoi.rsplit("_", 1)[-1]
    return ky_tu_sau_dau_gach
    
with onto:
    class Word(owl.Thing): 
        pass
    class Chu_the(Word):
        pass
    class Chu_the_ban_hanh(Chu_the): 
        pass 
    class Chu_the_tham_gia(Chu_the):
        pass
    
    class Verb(Word):
        pass
    class Noun(Word):
        pass
    class Menh_lenh(Noun):
        pass
    class Cho_phep(Menh_lenh):
        pass
    class Dieu_kien_khong_rang_buoc(Cho_phep):
        pass
    
    class Bat_buoc(Menh_lenh):
        pass
    class Dieu_kien_rang_buoc(Bat_buoc):
        pass
    
    class Cam(Menh_lenh):
        pass
    
    class Dieu_kien(Word):
        pass
    class So_huu(Verb): 
        pass
    class Nhiem_vu(Word): 
        pass
    class Tham_quyen(Verb): 
        pass
    class Muc_tieu(Word):
        pass
    
    class has_nmod(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
        
    class has_vmod(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
        
    class has_sub(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    
    class has_adv(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_dob(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_coord(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word] 
    class has_conj(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]   
    class has_Dieu_kien(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_Tham_quyen(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]  
    class has_Chu_the(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word] 
    class has_Menh_lenh(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]  
    class has_Quyen_han(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_So_huu(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_Nhiem_vu(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_Muc_tieu(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_Dieu_kien_rang_buoc(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_Dieu_kien_khong_rang_buoc(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    
    class has_Dong_tu_chinh(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_Chu_the_thuc_hien(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_Van_de_phap_ly(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_Dong_tu_bo_sung(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_Doi_tuong(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
          
    rule_dong_tu_bo_sung_1 = owl.Imp()
    rule_dong_tu_bo_sung_1.set_as_rule(
        "has_vmod(?v1, ?v2) -> has_Dong_tu_bo_sung(?v1, ?v2)"
    )
    
    rule_dong_tu_bo_sung_3 = owl.Imp()
    rule_dong_tu_bo_sung_3.set_as_rule(
        "has_coord(?v1, ?va), has_conj(?va, ?v2) -> has_Dong_tu_bo_sung(?v1, ?v2)"
    )
    
    rule_doi_tuong_1 = owl.Imp()
    rule_doi_tuong_1.set_as_rule(
        "has_dob(?v1, ?dt) -> has_Doi_tuong(?v1, ?dt)"
    )
    rule_doi_tuong_2 = owl.Imp()
    rule_doi_tuong_2.set_as_rule(
        "has_Dong_tu_bo_sung(?v1, ?v2), has_Doi_tuong(?v2, ?dt) -> has_Doi_tuong(?v1, ?dt)"
    )
    r'''
        Suy dien MENH LENH
    '''   
    # rule_menh_lenh = owl.Imp()
    # rule_menh_lenh.set_as_rule(
    #     "So_huu(?c), Chu_the(?ct), Menh_lenh(?ml), has_Chu_the(?c, ?ct), has_Menh_lenh(?c, ?ml)-> has_Chu_the_thuc_hien(?ml, ?ct)"
    # )
    # rule_menh_lenh_2 = owl.Imp()
    # rule_menh_lenh_2.set_as_rule(
    #     "So_huu(?c), Menh_lenh(?ml), has_Menh_lenh(?c,?ml), has_dob(?c, ?ml), has_nmod(?ml, ?dtc) -> has_Dong_tu_chinh(?ml, ?dtc) "
    # )
    # rule_menh_lenh_3 = owl.Imp()
    # rule_menh_lenh_3.set_as_rule(
    #     "Menh_lenh(?ml), has_Dong_tu_chinh(?ml, ?dtc), has_Doi_tuong(?dtc, ?vdpl) -> has_Van_de_phap_ly(?ml, ?vdpl) "
    # )
    # rule_menh_lenh_3 = owl.Imp()
    # rule_menh_lenh_3.set_as_rule(
    #     "Menh_lenh(?ml), has_Dong_tu_chinh(?ml, ?dtc), has_dob(?dtc, ?vdpl) -> has_Van_de_phap_ly(?ml, ?vdql)"
    # )
    #, has_dob(?c, ?ml), has_nmod(?ml, ?dtc), has_dob(?dtc, ?vdpl) 
    #, has_Dong_tu_chinh(?ml, ?dtc), has_Van_de_phap_ly(?ml, ?vdpl)
    # rule_menh_lenh_2 = owl.Imp()
    # rule_menh_lenh_2.set_as_rule(
    #     "Verb(?dtc), Chu_the(?ct), has_Chu_the(?dtc, ?ct), has_sub(?dtc, ?ct) -> has_Dong_tu_chinh(?ct, ?dtc)"
    # )
    
    
def make_class_and_relationship_knowledge(self, dataframe, DP_df):
    for i in range(len(DP_df)):
        index = DP_df['Index'][i]
        word = DP_df['Word'][i]
        pos_tag = DP_df['Pos_Tag'][i]
        category = DP_df['Category'][i]
        
        if pos_tag == 'N':
            sr = f"{unidecode(word)}_{index} = Noun(\"{word}_{str(index)}\")"
            exec(sr)   
        elif pos_tag == 'V': 
            sr = f"{unidecode(word)}_{index} = Verb(\"{word}_{str(index)}\")"  
            exec(sr)
        elif pos_tag == 'CH': 
            continue
        else: 
            sr = f"{unidecode(word)}_{index} = Word(\"{word}_{str(index)}\")"  
            exec(sr)
        if category != '':
            sr = f"{unidecode(word)}_{str(index)} = {unidecode(category).replace(' ','_')}(\"{word}_{str(index)}\")"
            exec(sr)
            #print(sr)
        if word == 'phải': 
            sr = f"{unidecode(word)}_{index} = Dieu_kien_rang_buoc(\"{word}_{str(index)}\")"  
            exec(sr)
        if word == 'được': 
            sr = f"{unidecode(word)}_{index} = Dieu_kien_khong_rang_buoc(\"{word}_{str(index)}\")"  
            exec(sr)
    
    instances = list(onto.individuals())
    
    for i in range(len(DP_df)): 
        index = DP_df['Index'][i]
        word = DP_df['Word'][i]
        head = DP_df['Head'][i]
        label = DP_df['Label'][i]
        head_index = DP_df['Head_Index'][i]
        if label == 'nmod' or label == 'vmod' or label == 'sub' or label == 'adv' or label == 'dob' or label == 'coord' or label == 'conj':
            sr = f"{unidecode(head)}_{str(head_index)}.has_{label}.append({unidecode(word)}_{str(index)})"
            exec(sr)
        category = DP_df['Category'][i]
        if category == '' or head == '':
            continue
        reasoning_category = category
        if category in ['Bắt buộc', 'Cấm', 'Cho phép']:
            reasoning_category = 'Mệnh lệnh'
        if category in ['Chủ thể ban hành', 'Chủ thể tham gia']:
            reasoning_category = 'Chủ thể'
        sr = f"{unidecode(head)}_{str(head_index)}.has_{unidecode(reasoning_category).replace(' ','_')}.append({unidecode(word)}_{str(index)})"
        exec(sr)
        
    
    for i in range(len(dataframe)):
        print(i)
        owl.sync_reasoner_hermit(infer_property_values=True)

    for i in instances: 
        w = str(i)[5:]
        ml = locals()[unidecode(w)] 
        if ml.has_Doi_tuong == [] and ml.has_Dong_tu_bo_sung == []: 
            continue
        print("-----------------------------")
        print(ml)
        if ml.has_Doi_tuong != []:
            print(f"Dong tu chinh la {ml} tuong ung voi doi tuong la {ml.has_Doi_tuong}")
        if ml.has_Dong_tu_bo_sung != []:
            for j in ml.has_Dong_tu_bo_sung:
                print(f"Dong tu bo sung la {j} tuong ung voi doi tuong la {j.has_Doi_tuong}")
        
    #instances_in_Menh_lenh = list(Menh_lenh.instances())
    ketqua = []
    # for i in instances_in_Menh_lenh:
    #     w = str(i)[5:]
    #     ml = locals()[unidecode(w)]
    #     result = {
    #             "loai_thong_tin": "Quyen han",
    #             "loai_menh_lenh": give_index(str(ml)),
    #             "chu_the": give_index(str(ml.has_Chu_the_thuc_hien)[1:-1]),
    #             "dong_tu_chinh": give_index(str(ml.has_Dong_tu_chinh)[1:-1]),
    #             "van_de_phap_ly": give_index(str(ml.has_Van_de_phap_ly)[1:-1])
    #         }
        
    #     ketqua.append(result)    
    # for i in instances_in_Menh_lenh:
    #     w = str(i)[5:]
    #     ml = locals()[unidecode(w)]
    #     result = {
    #             "loai_thong_tin": "Quyen han",
    #             "loai_menh_lenh": str(ml),
    #             "chu_the": str(ml.has_Chu_the_thuc_hien),
    #             "dong_tu_chinh": str(ml.has_Dong_tu_chinh),
    #             "van_de_phap_ly": str(ml.has_Van_de_phap_ly)
    #         }
      
    #     ketqua.append(result)         
    return ketqua