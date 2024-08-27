# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Đặng Nhật Huy, Bùi Tiến Thành
# Title: _nlp_processing.py
# Date: 2024/01/31 11:59:09
# Description: File chứa các hàm xử lý phân tích diễn ngôn và xử lý mệnh đề
# 
# (c) 2023-2024 CMC ATI. All rights reserved
# -----------------------------------------------------------------------------------------------


import numpy as np
import pandas as pd
import logging
from tqdm import tqdm


from LawSentence import Sentence
import Utils.NLPHelper



# -----------------------------------------------------------------------------------------------
# Dep. Parsing & POS Tagging
# -----------------------------------------------------------------------------------------------
def init_pos_dependency_parsing(self, data):
    # Phân tích câu dùng PhoNLP
    logging.info(f"Phân tích câu dùng PhoNLP")
    anno_data = Utils.NLPHelper.phonlp_annotate(data['EDUText'].tolist())
    


    
    logging.info(f"Kích cỡ dữ liệu: {data.shape[0]}")
    logging.info(f"Kích cỡ kết quả phân tích câu: {len(anno_data)}")
    
    data['AnnotationData'] = anno_data
    return data



# -----------------------------------------------------------------------------------------------
# Discourse Parsing
# -----------------------------------------------------------------------------------------------
def find_clauses_in_DF(self, data):
    logging.info(f"Bắt đầu tách mệnh đề cho câu")
    data_mde = pd.DataFrame(
        columns=[
            "fileId",
            "fileName",
            "parentIndex",
            "parentLevel",
            "paraIndex",
            "paraHigherIndex", # Lấy từ mâu thuẫn TQ nội dung
            "paraLevel",
            "paraName",        
            "paraClassification",   # Tương đương với cột "Dạng" trong code Huy
            "paraPath",
            "rawText",
            "segmentedText", 
            "EDUText",    # Chuyển từ RawText ở code cũ vì text đã được xử lý, ko được gọi là raw nữa
        ]
    )



    # Sửa: Duyệt theo index
    for data_idx in tqdm(data.index, "Tách mệnh đề"):
        level = data.loc[data_idx, 'paraLevel']
        paraindex = data.loc[data_idx, 'paraIndex']
        name = data.loc[data_idx, 'paraName']
        rawtext = data.loc[data_idx, 'rawText']
        file_id = data.loc[data_idx, 'fileId']
        file_name = data.loc[data_idx, 'fileName']
        segmented_text = data.loc[data_idx, 'segmentedText']
        para_classification = data.loc[data_idx, 'paraClassification']
        para_path = data.loc[data_idx, 'paraPath']
        higher_index_set = data.loc[data_idx, 'paraHigherIndex']

        if level != 0: 
            EDUs = Sentence(segmented_text, self.df_sv).find_all_menh_de()
        else:
            EDUs = [segmented_text]
            continue

        for EDU_count, EDU in enumerate(EDUs): # Ta có thể dùng EDU_count để đếm số câu 
            data_mde.loc[len(data_mde.index)] = {
                "fileId"                : file_id,
                "fileName"              : file_name,
                "parentIndex"           : paraindex,
                "parentLevel"           : level,
                "paraIndex"             : f"{paraindex}.{EDU_count + 1}",
                "paraLevel"             : 9,
                "paraName"              : name,
                "paraClassification"    : para_classification,
                "paraPath"              : f"{para_path}_MenhDe{EDU_count + 1}",
                "rawText"               : rawtext,
                "segmentedText"         : segmented_text,
                "EDUText"               : EDU,
                "paraHigherIndex"       : higher_index_set,
            }
    
    logging.info(f"Đã tách xong mệnh đề.")
    return data_mde
    
