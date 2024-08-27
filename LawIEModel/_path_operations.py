# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Đặng Nhật Huy, Bùi Tiến Thành
# Title: _path_operations.py
# Date: 2024/01/31 11:54:54
# Description: File chứa các hàm xử lý đường dẫn
# 
# (c) 2023-2024 CMC ATI. All rights reserved
# -----------------------------------------------------------------------------------------------

import re
import logging
import pandas as pd
import numpy as np
from tqdm import tqdm



            
# -----------------------------------------------------------------------------------------------
# Tiền xử lý đường dẫn với văn bản có sửa đổi bổ sung
# -----------------------------------------------------------------------------------------------
def path_preprocess_with_modification(self, data: pd.DataFrame):
    """
        Gộp các đoạn tham chiếu lại với nhau, i.e. các phần sửa đổi bổ sung

        Nguyên lý
        --------
        Tác giả dựa vào flag BIO của trường 'paraModification' và số dấu ngoặc kép để gộp các đoạn tham chiếu lại với nhau.
        Do trong thực nghiệm, tác giả xét thấy việc chỉ sử dụng flag BIO không hiệu quả và việc gộp bị sót dẫn đến bóc tách sai index
        nên tác giả sẽ sử dụng số dấu ngoặc kép để gộp các đoạn tham chiếu lại với nhau. Nếu số dấu ngoặc kép là chẵn => kết thúc gộp

        Tham số đầu vào
        ----------------
        data : pd.DataFrame
            DataFrame chứa trường 'paraModification' chứa thông tin đoạn tham chiếu

        Kết quả trả về
        --------------
        [TODO]
    """
    def find_quotation_number(text: str) -> int: return len(re.findall(r'"', text))
    old_size = data.shape[0]
    if data.empty: return data
    result = pd.DataFrame(columns=data.columns)

    integer_index = 0
    while integer_index < data.shape[0]:
        if data.iloc[integer_index]['paraModification'] == 'O':
            # Trường hợp không có dấu ngoặc kép
            result.loc[result.shape[0]] = data.iloc[integer_index].copy(deep=True)

        elif data.iloc[integer_index]['paraModification'] == 'B':
            # Trường hợp có dấu ngoặc kép, ta sẽ gộp câu cho đến bao giờ số ngoặc kép là chẵn
            number_of_quotation = find_quotation_number(data.iloc[integer_index]['rawText'])
            new_row = data.iloc[integer_index].copy(deep=True)

            # Duyệt lên
            while integer_index + 1 < data.shape[0] and number_of_quotation % 2 != 0: 
                integer_index += 1
                new_row['rawText'] += '\n' + data.iloc[integer_index]['rawText']
                number_of_quotation += find_quotation_number(data.iloc[integer_index]['rawText'])
                


            result.loc[result.shape[0]] = new_row
        integer_index += 1


    new_size = result.shape[0]
    logging.info(f"Tiền xử lý đường dẫn với văn bản có sửa đổi bổ sung: {old_size} -> {new_size}, chênh lệch {old_size - new_size} dòng.")
    return result




# -----------------------------------------------------------------------------------------------
# Xây dựng đường dẫn
# -----------------------------------------------------------------------------------------------
def path_processing(self, data):
    logging.info(f"Bắt đầu xây dựng đường dẫn")
    classification_set = ['VanBan', 'Chuong', 'Muc', 'Dieu', 'Khoan', 'Diem', 'HaDiem']
    df = pd.DataFrame(
        '0',
        index = data.index,
        columns = [
            'VanBan', 
            'Chuong', 
            'Muc', 
            'Dieu', 
            'Khoan', 
            'Diem', 
            'HaDiem', 
            'Level', 
            'paraIndex', 
            'elementSubSet', 
            'parentIndex', 
            'paraPath'
        ]
    )

    
    df[['Level', 'paraIndex', 'elementSubSet', 'parentIndex', 'paraPath']] = ''
    data['paraPath'] = ''
    dictHaDiem = {}
    dictIndex = {}
    
    for i in range(len(data)):
        dictIndex[i] = []
    
    logging.info(f"BFS cho các điều khoản")
    for i in range(len(data)-1): 
        para_name = data['paraName'][i]
        level1 = data['paraLevel'][i]
        level2 = data['paraLevel'][i+1]
        classification = data['paraClassification'][i]
        classification2 = data['paraClassification'][i+1]
        cnt = i+1
        while classification != classification2 and level1 <= level2:
            dictIndex[i].append(cnt)
            if cnt == len(data) - 1: 
                break
            cnt = cnt + 1
            classification2 = data['paraClassification'][cnt]
            level2 = data['paraLevel'][cnt]
        classification = classification2
        level = level2
    #0 : VanBan ;  1 : Chuong ; 2 : Muc ; 3 : Dieu ; 4  : Khoan; 7 : Diem ; 8 : HaDiem
    
    
    logging.info(f"Xây dựng cặp [paraName, Index] cho các quy định")
    for index in dictIndex.keys():  
        classification = data['paraClassification'][index]
        if classification == '':
            continue
        para_name = data['paraName'][index]
        df[classification][index] = [para_name, index]
        for j in dictIndex[index]: 
            df[classification][j] = [para_name, index]

                
    # df.to_excel('test.xlsx')
    # except Exception as e:
    #     logging.error(f"Lỗi khi xây dựng cặp cls={classification}, prn={paraname}, name={name} cho các điều khoản: {e}")
    #     return None
    
    logging.info(f"Xây dựng lại ParaIndex")
    for i in range(len(df)):
        classification = data['paraClassification'][i]
        df['Level'][i] = classification

        luat = df['VanBan'][i][0]
        chuong = df['Chuong'][i][0]
        muc = df['Muc'][i][0]
        dieu = df['Dieu'][i][0]
        khoan = df['Khoan'][i][0]
        diem = df['Diem'][i][0]
        
        

        if classification == 'HaDiem':
            ha_diem = dictHaDiem[i]
            data['paraName'][i] = dictHaDiem[i]
            df['HaDiem'][i][0] = ha_diem
        else:
            ha_diem = df['HaDiem'][i][0]
        df['paraIndex'][i] = f"{0}.{chuong}.{muc}.{dieu}.{khoan}.{diem}.{ha_diem}"
        df['elementSubSet'][i] = dictIndex[i]
        if classification in ['Diem','Khoan', 'Chuong','Muc', 'Dieu'] and dictIndex[i] != []:
            for j in range(len(dictIndex[i])): 
                kq = j + 1
                kq = str(kq) 
                dictHaDiem[dictIndex[i][j]] = kq


    
    logging.info(f"Xây dựng đường dẫn / paraPath và ParentIndex")
    for i in range(len(data)):
        classification = df['Level'][i]

        if classification != 'VanBan': data['paraName'][i] = data['paraClassification'][i] + data['paraName'][i]
        
        
        if classification == 'VanBan':
            start = 7
        elif classification == 'Chuong':
            start = 6
        elif classification == 'Muc': 
            start = 5
        elif classification == 'Dieu':
            start = 4
        elif classification == 'Khoan':
            start = 3
        elif classification == 'Diem':
            start = 2
        elif classification == 'HaDiem':
            start = 1
        else: 
            pass
        
    
        path_list = [df['VanBan'][i][0]]
        for j in range(1, len(classification_set)):
            if df[classification_set[j]][i] != '0':
                path_list.append(classification_set[j] + df[classification_set[j]][i][0])
        path = '_'.join(path_list)

        data['paraPath'][i] = path
        for j in reversed(range(len(classification_set)-start)):
            if df[classification_set[j]][i] != '0':
                df['parentIndex'][i] = df['paraIndex'][df[classification_set[j]][i][1]]
                break
            
    data['paraIndex'] = df['paraIndex']
    data['parentIndex'] = df['parentIndex']
    #data = data.drop(['paraClassification', 'nosegmentedText'], axis=1)

    logging.info(f"Xây dựng đường dẫn thành công")
    return data



# -----------------------------------------------------------------------------------------------
# Tìm index cha
# -----------------------------------------------------------------------------------------------
def finding_higher_index(self, data):
    logging.info(f"Tim higher level cho tung quy dinh")
    dictHigherIndex = {}
    for index in data.index: 
        para_index = data.loc[index, 'paraIndex']
        dictHigherIndex[para_index] = []
    for index in tqdm(data.index, "Tìm các quy định cha cho elements"):
        para_level = data.loc[index, 'paraLevel']
        if para_level == 0: 
            continue
        para_index = data.loc[index, 'paraIndex']
        parent_index = data.loc[index, 'parentIndex']
        now_element = para_index
        after_element = parent_index
        try:
            while after_element != '0.0.0.0.0.0.0':
                dictHigherIndex[para_index].append(after_element)
                now_element = after_element
                # if data[data.paraIndex == now_element].empty: break
                after_element = data[data.paraIndex == now_element].iloc[0].parentIndex
        except Exception as e:
            logging.error(f"Lỗi khi tìm các quy định cha cho elements tại index {index}, para_index={para_index}, parent_index={parent_index}, now_element={now_element}, after_element={after_element}, para_name={data.loc[index, 'paraName']}, paraClassification={data.loc[index, 'paraClassification']} và nội dung '{data.loc[index, 'segmentedText']}'")
            raise e
    
    data['paraHigherIndex'] = ''
    for i in range(len(data)):
        para_index = data['paraIndex'][i]
        data['paraHigherIndex'][i] = sorted(list(set(dictHigherIndex[para_index])), reverse=True)

    logging.info(f"Đã tim xong higher level elements.")
    return data

        
