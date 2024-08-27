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
# Date: 2024/01/31 13:37:18
# Description: 
# 
# (c) 2023-2024 CMC ATI. All rights reserved
# -----------------------------------------------------------------------------------------------


import json
import logging
import numpy as np
import pandas as pd
import pyspark.pandas as ps
from tqdm import tqdm

from LawSentence import Sentence
from DependencyParsing import DependencyParsing
from Utils.DataHelper.SupportData import SupportData

# -----------------------------------------------------------------------------------------------
# UDF
# -----------------------------------------------------------------------------------------------
class UDF_DependencyParsing:
    support_words_data = None

    def __init__(self, support_words_data):
        self.support_words_data = support_words_data

    def solve(self, row):
        text = row['EDUText']
        dp_data = row['AnnotationData']
        df_sv = Sentence(text, self.support_words_data).find_special_verb()
        DP = DependencyParsing(text, df_sv, dp_data)
        result = DP.lay_thong_tin_cho_root()
        return result
    

class UDF_Authorization:
    support_words_data = None
    dictExtract = {}

    def __init__(self, support_words_data, dictExtract):
        self.support_words_data = support_words_data
        self.dictExtract = dictExtract

    def solve(self, row):
        higher_index_set = row['paraHigherIndex']
        para_index = row['paraIndex']
        para_path = row['paraPath']
        edu_text = row['EDUText']
        dp_data = row['AnnotationData']

        try:
            result = {
                "chu_de": {
                    "chu_the": [],
                    "chu_de": [],
                    "dong_tu": []
                },
                "phan_quyen": []
            }


            text = Sentence(edu_text, self.support_words_data)
            df_sv = text.find_special_verb()
            dp = DependencyParsing(edu_text, df_sv, dp_data)
            
            if dp.empty == True:
                logging.error(f"Không thể phân tích câu: '{edu_text}'")
                return result
            dp.update_DP()

            
            if higher_index_set != []:
                higher = higher_index_set[0] + ".1"
                kq_tham_quyen, kq_chu_de = dp.extract_agency_authority_jurisdiction(higher_index_set, self.dictExtract[higher])
                self.dictExtract[para_index] = kq_chu_de

                for kq_tq_index in range(len(kq_tham_quyen)): 
                    kq_tham_quyen[kq_tq_index]['paraPath'] = para_path
                    kq_tham_quyen[kq_tq_index]['rawText'] = edu_text
                # if len(kq_tham_quyen) > 0: 
                #     print()
                    # logging.info(f"Tìm được {len(kq_tham_quyen)} bản ghi thông tin phân quyền tại {para_path}")
                

                result = {
                    "phan_quyen": kq_tham_quyen,
                    "chu_de": kq_chu_de,
                }

            return result
        
        except Exception as e:
            logging.error(f"Lỗi khi phân tích thẩm quyền và chủ đề")
            logging.error(f"Tại vị trí: {para_path} - {edu_text} với higher: {higher_index_set} và para_index: {para_index}")
            return result




# -----------------------------------------------------------------------------------------------
# Trích xuất thông tin từ Dependency Parsing
# -----------------------------------------------------------------------------------------------
def lay_thong_tin_trong_DP(self, data):
    labels = SupportData().get_dp_labels()    


    # Sử dụng UDF để vectorize việc xử lý
    UDFParser = self.UDF_DependencyParsing(self.df_sv)
    logging.info(f"Bắt đầu phân tích câu")
    DP_result = data.progress_apply(UDFParser.solve, axis=1)
    logging.info(f"Đã phân tích xong câu. Phân phối kết quả")


    for label in tqdm(labels, desc="Phân phối kết quả"):
        data[label] = DP_result.apply(lambda x: x.get(label, [""]))  
    return data



# -----------------------------------------------------------------------------------------------
# Trích xuất thông tin phân quyền - Updated
# -----------------------------------------------------------------------------------------------
def lay_thong_tin_phan_quyen(self, data): # 
    dictExtract = {}
    for i in range(len(data)): 
        para_index = data['paraIndex'][i]
        dictExtract[para_index] = []
    
    logging.info(f"Bắt đầu phân tích thông tin phân quyền")

    # Sử dụng UDF
    UDF_AuthorizationSolver = self.UDF_Authorization(self.df_sv, dictExtract)
    IE_result = pd.DataFrame(data).progress_apply(lambda row: UDF_AuthorizationSolver.solve(row), axis = 1)


    # Phân phối kết quả: Phân quyền
    result_PhanQuyen = (
        pd.DataFrame.from_records(
            IE_result.apply(lambda x: x['phan_quyen'])
            .sum()
        ).rename(columns = {
            "paraPath"          : "vi_tri",
            "rawText"           : "noi_dung",
            "chu_de"            : "van_de_ban_hanh",
            "chu_the"           : "chu_the",
        })
    )


    # Phân phối kết quả: Chủ đề
    # Hàm này luôn đảm bảo rằng IE_result không bao giờ rỗng
    IE_ChuDe = IE_result.apply(lambda x: x['chu_de'])
    data['paraChuTheBanHanh'] = IE_ChuDe.apply(lambda x: x['chu_the'])
    data['paraChuDe'] = IE_ChuDe.apply(lambda x: x['chu_de'])
    data['paraDongTu'] = IE_ChuDe.apply(lambda x: x['dong_tu'])
    result_ChuDe = (
        data[["paraChuDe", "paraChuTheBanHanh", "paraDongTu", "paraPath", "rawText"]]
        .rename(columns = {
            "paraPath"          : "vi_tri",
            "rawText"           : "noi_dung",
            "paraChuDe"         : "chu_de",
            "paraChuTheBanHanh" : "chu_the_ban_hanh",
            "paraDongTu"        : "dong_tu"
        })
    )


    return result_PhanQuyen, result_ChuDe


