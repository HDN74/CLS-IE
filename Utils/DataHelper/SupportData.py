import pandas as pd
import logging

import Utils.NLPHelper
import config


# -----------------------------------------------------------------------------------------------
# Support Data
# -----------------------------------------------------------------------------------------------
class SupportData:
    special_verbs = None
    dp_labels  = [
        'sub',
        'mainverb',
        'ml',
        'dob',
        'iob',
        'pob',
        'vmod',
        'nmod',
        'tmp',
        'loc',
        'prp',
        'mnr',
        'adv',
        'coord',
        'det',
        'dep'
    ]
    translation_dp = {
        'sub'       : 'Chủ thể chính', 
        'mainverb'  : 'Động từ chính',
        'ml'        : 'ml',
        'dob'       : 'Chủ thể phụ trực tiếp',
        'iob'       : 'Chủ thể phụ gián tiếp',
        'pob'       : 'pob',
        'vmod'      : 'Động từ bổ trợ cho động từ trước đó',
        'nmod'      : 'Danh từ bổ trợ cho danh từ trước đó',
        'tmp'       : 'Thời gian',
        'coord'     : 'coord',
        'prp'       : 'Mục tiêu',
        'mnr'       : 'Phương thức',
        'adv'       : 'Trạng ngữ',
        'loc'       : 'Địa điểm',
        'det'       : 'det',
        'dep'       : 'dep',
    }


    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SupportData, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass


    def initialize(self):
        logging.info(f"Khởi tạo dữ liệu bổ trợ")

        logging.info(f"Xử lý động từ đặc biệt")
        logging.info(f"Tải dữ liệu động từ đặc biệt từ file {config.PATH_SPECIAL_VERBS}")
        self.special_verbs = self.__process_special_verbs(pd.read_excel(config.PATH_SPECIAL_VERBS))
        logging.info(f"Xử lý động từ đặc biệt hoàn tất")


        logging.info(f"Đã khởi tạo xong dữ liệu bổ trợ")
        self._instance = self
        

    def __process_special_verbs(self, raw_special_verbs):
        # Mặc định data phải có 2 cột: 'Words' và 'Group'
        assert 'Words' in raw_special_verbs.columns
        assert 'Group' in raw_special_verbs.columns

        logging.info(f"Xử lý dữ liệu động từ đặc biệt")
        # Xử lý cột 'Words'. Cột này có xâu các từ cách nhau bởi dấu phẩy
        def process_words_column(words):
            words = words.strip().lower().split(',')
            words = [Utils.NLPHelper.segmentize(word.strip()) for word in words]
            return words
        raw_special_verbs['Words'] = raw_special_verbs['Words'].apply(process_words_column)

        logging.info(f"Xử lý dữ liệu động từ đặc biệt hoàn tất")
        # Trả về kết quả
        return raw_special_verbs


    def get_special_verbs(self): return self.special_verbs.copy(deep=True)
    def get_dp_labels(self): return self.dp_labels
    def get_translation_dp(self): return self.translation_dp