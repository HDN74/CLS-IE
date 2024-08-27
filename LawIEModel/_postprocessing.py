# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Bùi Tiến Thành (@bu1th4nh)
# Title: _postprocessing.py
# Date: 2024/02/07 14:30:47
# Description: File chứa các hàm xử lý dữ liệu sau khi đã phân tích xong
# 
# (c) CMC ATI. All rights reserved
# -----------------------------------------------------------------------------------------------


import re
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
from unidecode import unidecode



# -----------------------------------------------------------------------------------------------
# Hậu xử lý thẩm quyền
# -----------------------------------------------------------------------------------------------
def normalize_co_quan_ban_hanh(self, text):
    if getattr(self, "co_quan_nha_duoc_dict", None) is None:
        self.co_quan_nha_duoc_dict = {
            "quoc hoi"                                      : "quoc hoi",
            "uy ban thuong vu"                              : "uy ban thuong vu quoc hoi",
            "uy ban thuong vu quoc hoi"                     : "uy ban thuong vu quoc hoi",
            "doan chu tich"                                 : "doan chu tich uy ban trung uong mat tran to quoc viet nam",
            "uy ban trung uong"                             : "doan chu tich uy ban trung uong mat tran to quoc viet nam",
            "mat tran to quoc"                              : "doan chu tich uy ban trung uong mat tran to quoc viet nam",
            "mat tran to quoc viet nam"                     : "doan chu tich uy ban trung uong mat tran to quoc viet nam",
            "to quoc viet nam"                              : "doan chu tich uy ban trung uong mat tran to quoc viet nam",
            "chinh phu"                                     : "chinh phu",
            "chu tich nuoc"                                 : "chu tich nuoc",
            "thu tuong"                                     : "thu tuong chinh phu",
            "thu tuong chinh phu"                           : "thu tuong chinh phu",
            "hoi dong tham phan toa an nhan dan toi cao"    : "hoi dong tham phan toa an nhan dan toi cao",
            "hoi dong tham phan"                            : "hoi dong tham phan toa an nhan dan toi cao",
            "toa an nhan dan toi cao"                       : "toa an nhan dan toi cao",
            "vien kiem sat"                                 : "vien kiem sat nhan dan toi cao",
            "vien kiem sat nhan dan"                        : "vien kiem sat nhan dan toi cao",
            "vien kiem sat nhan dan toi cao"                : "vien kiem sat nhan dan toi cao",
            "tong kiem toan"                                : "tong kiem toan nha nuoc",
            "tong kiem toan nha nuoc"                       : "tong kiem toan nha nuoc",
            "bo quoc phong"                                 : "bo, co quan ngang bo",
            "bo cong an"                                    : "bo, co quan ngang bo",
            "bo ngoai giao"                                 : "bo, co quan ngang bo",
            "bo tu phap"                                    : "bo, co quan ngang bo",
            "bo tai chinh"                                  : "bo, co quan ngang bo",
            "bo cong thuong"                                : "bo, co quan ngang bo",
            "bo lao dong thuong binh va xa hoi"             : "bo, co quan ngang bo",
            "bo giao thong van tai"                         : "bo, co quan ngang bo",
            "bo xay dung"                                   : "bo, co quan ngang bo",
            "bo thong tin va truyen thong"                  : "bo, co quan ngang bo",
            "bo giao duc va dao tao"                        : "bo, co quan ngang bo",
            "bo nong nghiep va phat trien nong thon"        : "bo, co quan ngang bo",
            "bo ke hoach va dau tu"                         : "bo, co quan ngang bo",
            "bo noi vu"                                     : "bo, co quan ngang bo",
            "bo y te"                                       : "bo, co quan ngang bo",
            "bo khoa hoc va cong nghe"                      : "bo, co quan ngang bo",
            "bo van hoa the thao va du lich"                : "bo, co quan ngang bo",
            "bo tai nguyen va moi truong"                   : "bo, co quan ngang bo",
            "van phong chinh phu"                           : "bo, co quan ngang bo",
            "thanh tra chinh phu"                           : "bo, co quan ngang bo",
            "ngan hang nha nuoc"                            : "bo, co quan ngang bo",
            "uy ban dan toc"                                : "bo, co quan ngang bo",
            "hoi dong nhan dan"                             : "hoi dong nhan dan",
            "uy ban nhan dan"                               : "uy ban nhan dan",
        }
        


    text = text.replace("_", " ").strip().lower()
    text = unidecode(text)
    text = self.co_quan_nha_duoc_dict.get(text, None)
    return text
    
    
def general_normalize(self, text):
    if " _ " in str(text):
        text = str(text).replace(" _ ", "_")
    return str(text)


def postprocess_thamquyen(self, data: pd.DataFrame):
    if data.empty: return data
    data['chu_the'] = data['chu_the'].apply(self.general_normalize)
    data['van_de_ban_hanh'] = data['van_de_ban_hanh'].apply(self.general_normalize)
    data['chu_the_ban_hanh'] = data['chu_the'].apply(self.normalize_co_quan_ban_hanh)


    # data.dropna(subset=['chu_the'], inplace=True)
    data.dropna(subset=['chu_the_ban_hanh'], inplace=True)
    data.drop_duplicates(inplace=True, keep='first')
    return data



# -----------------------------------------------------------------------------------------------
# Hậu xử lý chung
# -----------------------------------------------------------------------------------------------
def humanize_parapath(self, parapath: str) -> str:
    ignore_case_setting = re.IGNORECASE
    paths = parapath.split("_")
    paths = paths[1:] # Do vi_tri có dạng <văn_bản>_<phần>...., mà ta ko cần văn bản do đã có metadata rồi

    return_paths = []
    for path in paths:
        # Phần -> chương -> mục -> điều -> khoản -> điểm
        if   re.match("Phan",   path, ignore_case_setting): return_paths.append("Phần " + path.split("Phan")[-1])
        elif re.match("Chuong", path, ignore_case_setting): return_paths.append("Chương " + path.split("Chuong")[-1])
        elif re.match("Muc",    path, ignore_case_setting): return_paths.append("Mục " + path.split("Muc")[-1])
        elif re.match("Dieu",   path, ignore_case_setting): return_paths.append("Điều " + path.split("Dieu")[-1])
        elif re.match("Khoan",  path, ignore_case_setting): return_paths.append("Khoản " + path.split("Khoan")[-1])
        elif re.match("Diem",   path, ignore_case_setting): return_paths.append("Điểm " + path.split("Diem")[-1])
        elif re.match("HaDiem", path, ignore_case_setting): return_paths.append("Hạ điểm " + path.split("HaDiem")[-1])
        elif re.match("MenhDe", path, ignore_case_setting): return_paths.append("Mệnh đề " + path.split("MenhDe")[-1])

    return "/".join(return_paths)