# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Bùi Tiến Thành (@bu1th4nh)
# Title: __init__.py
# Date: 2024/01/31 11:39:06
# Description: File class DependencyParsing
# 
# (c) 2023-2024 CMC ATI. All rights reserved
# -----------------------------------------------------------------------------------------------


import numpy as np
import pandas as pd






class DependencyParsing:
    def __init__(self, sentence, df_special_verb, dp_data = None):
        self.sentence = sentence
        self.special_verb_set = df_special_verb
        DP = self.make_DP(self.sentence, dp_data)
        self.empty = DP[DP.Label == 'root'].empty
        
        # self.root = None if self.empty else list(DP[DP.Label == 'root']['Index']) -- Liệu root có thể nhận nhiều giá trị không?
        self.root = None if self.empty else DP[DP.Label == 'root'].iloc[0].Index
        
        self.DP = DP
    


    # -----------------------------------------------------------------------------------------------
    # Hỗ trợ trích xuất thông tin
    # -----------------------------------------------------------------------------------------------
    from ._info_extraction import determine_category
    from ._info_extraction import determine_level
    from ._info_extraction import find_support_words
    from ._info_extraction import give_information_for_words
    from ._info_extraction import give_object
    from ._info_extraction import information_extraction

    # -----------------------------------------------------------------------------------------------
    # Phân quyền
    # -----------------------------------------------------------------------------------------------
    from ._authorization import check_noi_dung
    from ._authorization import calculate_tree
    from ._authorization import check_quy_dinh_phan_quyen
    from ._authorization import extract_agency_authority_jurisdiction
    

    # -----------------------------------------------------------------------------------------------
    # Xử lý chính
    # -----------------------------------------------------------------------------------------------
    from ._processing import make_DP
    from ._processing import update_DP
    from ._processing import phan_cap_DP
    from ._processing import lay_thong_tin_cho_root


    # -----------------------------------------------------------------------------------------------
    # Word2Vec
    # -----------------------------------------------------------------------------------------------
    from ._word2vec import common_words
    from ._word2vec import find_similarity
    
    # -----------------------------------------------------------------------------------------------
    # Reasoning
    # -----------------------------------------------------------------------------------------------
    from ._reasoning import make_class_and_relationship_knowledge
