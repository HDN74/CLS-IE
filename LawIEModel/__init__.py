# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Bùi Tiến Thành, Đặng Nhật Huy
# Title: __init__.py
# Date: 2024/01/31 11:43:42
# Description: File class LawIEModel phục vụ bóc tách thông tin sâu từ văn bản pháp luật
# 
# (c) 2023-2024 CMC ATI. All rights reserved
# -----------------------------------------------------------------------------------------------


from pyspark.sql.types import *
# import pyspark.pandas as ps
from tqdm import tqdm
import pandas as pd
import logging
import warnings
import requests
import json
import ast
tqdm.pandas()
warnings.filterwarnings("ignore")



from Utils.DataHelper.SupportData import SupportData



class LawIEModel:
    df_sv = None
    data = None

    do_experimental_features = False

    FIELDNAME_RAW_TEXT = "rawText"
    FIELDNAME_SEGMENTED_TEXT = "segmentedText"
    FIELDNAME_EDU_TEXT = "EDUText"

    FIELDNAME_PARA_INDEX = "paraIndex"
    FIELDNAME_PARA_LEVEL = "paraLevel"
    FIELDNAME_PARA_PATH = "paraPath"
    FIELDNAME_PARA_NAME = "paraName"
    FIELDNAME_PARA_CLASSIFICATION = "paraClassification"

    FIELDNAME_PARENT_INDEX = "parentIndex"
    FIELDNAME_HIGHER_INDEXES = "parentIndex"
    
    FIELDNAME_ELEMENT_SUBSET = "elementSubSet"
    FIELDNAME_ANNOTATION_DATA = "AnnotationData"


    def __init__(
        self, 
        json_data: dict, 
        do_preprocess_path = False,
        do_find_higher_id = True, 
        do_discourse_parsing = True, 
        do_pos_dep_parsing = True
    ):
        logging.info(f"Khởi tạo & nạp dữ liệu vào model")
        self.df_sv          = SupportData().get_special_verbs()
        raw_data            = pd.DataFrame(json_data).rename(columns={"textValue": "rawText"})


        logging.info(f"Tiền xử lý dữ liệu")
        preprocessed_data   = self.preprocess_data(raw_data)
        # preprocessed_data.to_excel("__pycache__/Sample/1.data_sau_khi_chuyen_json_to_rawdf.xlsx", index=False)


        if do_preprocess_path:
            logging.info(f"Tiền xử lý đường dẫn")
            preprocessed_data = self.path_preprocess_with_modification(preprocessed_data)


        logging.info(f"Xử lý đường dẫn QPPL")
        self.data = self.path_processing(preprocessed_data)
        # path_processed_data.to_excel("__pycache__/Sample/2.data_sau_khi_xu_ly_duong_dan.xlsx", index=False)


        if do_find_higher_id:
            self.data = self.finding_higher_index(self.data)
            # path_processed_data.to_excel("__pycache__/Sample/3.data_sau_khi_tim_higher_index.xlsx", index=False)


        if do_discourse_parsing:
            logging.info(f"Phân tích diễn ngôn")
            self.data = self.find_clauses_in_DF(self.data)
            # edu_processed_data.to_excel("__pycache__/Sample/4.data_sau_khi_tach_mde.xlsx", index=False)


        if do_pos_dep_parsing:
            logging.info(f"POS tag + DP")
            self.data = self.init_pos_dependency_parsing(self.data)
        
        

    # -----------------------------------------------------------------------------------------------
    # UDFs
    # -----------------------------------------------------------------------------------------------
    from ._preprocessing import udf_process_sentence
    from ._info_extraction import UDF_DependencyParsing
    from ._info_extraction import UDF_Authorization


    # -----------------------------------------------------------------------------------------------
    # Tiền xử lý dữ liệu
    # -----------------------------------------------------------------------------------------------
    from ._preprocessing import preprocess_data


    # -----------------------------------------------------------------------------------------------
    # Xử lý đường dẫn
    # -----------------------------------------------------------------------------------------------
    from ._path_operations import path_preprocess_with_modification
    from ._path_operations import path_processing
    from ._path_operations import finding_higher_index


    # -----------------------------------------------------------------------------------------------
    # NLP
    # -----------------------------------------------------------------------------------------------
    from ._nlp_processing import init_pos_dependency_parsing
    from ._nlp_processing import find_clauses_in_DF


    # -----------------------------------------------------------------------------------------------
    # Trích xuất thông tin
    # -----------------------------------------------------------------------------------------------
    from ._info_extraction import lay_thong_tin_trong_DP
    from ._info_extraction import lay_thong_tin_phan_quyen


    # -----------------------------------------------------------------------------------------------
    # Hậu xử lý
    # -----------------------------------------------------------------------------------------------
    from ._postprocessing import general_normalize
    from ._postprocessing import normalize_co_quan_ban_hanh
    from ._postprocessing import postprocess_thamquyen
    from ._postprocessing import humanize_parapath


    # -----------------------------------------------------------------------------------------------
    # SRL
    # -----------------------------------------------------------------------------------------------
    def PlainSRL(self):
        # Các trường data sử dụng: EDUText; AnnotationData
        result = self.lay_thong_tin_trong_DP(self.data.copy(deep=True))
        # result.to_excel("5.xlsx")
        
        result.rename(
            columns = SupportData().get_translation_dp(),
            inplace = True
        )
        result['paraPath'] = result['paraPath'].apply(self.humanize_parapath)

        for unnecessary_col in ['AnnotationData', 'fileId', 'fileName', 'segmentedText']:
            if unnecessary_col in result.columns: result.drop(columns=[unnecessary_col], inplace=True)
        return result
    
    

    # -----------------------------------------------------------------------------------------------
    # Thẩm quyền
    # -----------------------------------------------------------------------------------------------
    def SRLChuDeThamQuyen(self, chu_de_only = False):
        res_phan_quyen, res_chu_de = self.lay_thong_tin_phan_quyen(self.data)
        logging.info(f"Phân quyền: {len(res_phan_quyen)}, Chủ đề: {len(res_chu_de)}")


        # res_phan_quyen.to_excel("res_tham_quyen.xlsx")
        # res_chu_de.to_excel("res_chu_de.xlsx")
        # return res_chu_de[['paraIndex', 'paraName', 'paraClassification', 'paraPath', 'paraChuDe', 'EDUText']]
        
        
        if 'AnnotationData' in res_chu_de.columns: res_chu_de.drop(columns=['AnnotationData'], inplace=True)
        if chu_de_only: 
            logging.info(f"Kích cỡ kết quả chủ đề trả về: {len(res_chu_de)}")
            return res_chu_de
        else:
            # final = res_phan_quyen
            final = self.postprocess_thamquyen(res_phan_quyen)
            logging.info(f"Kích cỡ kết quả phân quyền trả về: {len(final)}")
            return final
        

    # -----------------------------------------------------------------------------------------------
    # Làm sạch dữ liệu
    # -----------------------------------------------------------------------------------------------
    def get_refined_data(self):
        result = self.data[['paraIndex', 'paraClassification', 'paraPath', 'paraName', 'rawText', 'parentIndex', 'paraModification']].copy(deep=True)
        result['paraPath'] = result['paraPath'].apply(self.humanize_parapath)

        # with open("__pycache__/test.json", "wb") as f:
        #     result[["rawText", "paraModification", "paraPath"]].to_json(f, orient="records", force_ascii=False, indent=4)
        return result

