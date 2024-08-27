# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Bùi Tiến Thành, Đặng Nhật Huy
# Title: _preprocessing.py
# Date: 2024/01/31 11:44:18
# Description: File chứa các hàm tiền xử lý dữ liệu từ JSON vào DF
# 
# (c) 2023-2024 CMC ATI. All rights reserved
# -----------------------------------------------------------------------------------------------

from tqdm import tqdm
import pandas as pd
import unicodedata
import logging
import warnings
import re
tqdm.pandas()
warnings.filterwarnings("ignore")



from LawSentence import Sentence
import Utils.NLPHelper
import config


# -----------------------------------------------------------------------------------------------
# UDF
# -----------------------------------------------------------------------------------------------
def udf_process_sentence(self, row, default_paraname):
    rawText = str(row['rawText'])
    paraLevel = str(row['paraLevel'])
    classification, paraname, raw_sentence = Sentence(rawText, None).processing_law_sentence(paraLevel, default_paraname)

    return {
        'paraName': paraname,
        'paraClassification': classification,
        'segmentedText': raw_sentence,
    }




# -----------------------------------------------------------------------------------------------
# Tiền xử lý dữ liệu
# -----------------------------------------------------------------------------------------------
def preprocess_data(self, data):
    """
        Tiền xử lý text và path cho data.
    """
    # -----------------------------------------------------------------------------------------------
    # Thêm hàng chỉ thị điểm bắt đầu dữ liệu
    # -----------------------------------------------------------------------------------------------
    logging.info(f"Thêm hàng chỉ thị điểm bắt đầu dữ liệu")
    top_row = pd.DataFrame.from_dict(
        {
            0: {
                "fileId"        : data['fileId'][0], 
                "fileName"      : data['fileName'][0], 
                "paraIndex"     : "0.0.0.0.0.0.0.0.0.0", 
                "parentIndex"   : "0.0.0.0.0.0.0.0.0.0", 
                "paraLevel"     : 0, 
                "rawText"       : "",
            }
        },
        orient = 'index'
    )
    data = pd.concat([top_row, data], ignore_index=True)


    # -----------------------------------------------------------------------------------------------
    # Chuẩn hóa toàn bộ Unicode
    # -----------------------------------------------------------------------------------------------
    logging.info(f"Chuẩn hóa Unicode")
    for col in data.columns:
        if data[col].dtype == 'object' or data[col].dtype == 'string':
            try:
                logging.info(f"Chuẩn hóa Unicode cho cột {col}")
                new_col = data[col].progress_apply(lambda x: unicodedata.normalize("NFC", x) if x else x)
            except Exception as e:
                new_col = data[col]
                logging.error(f"Không thể chuẩn hóa Unicode cho cột {col} do lỗi {e}. Bỏ qua cột này", exc_info=True)
                pass
            data[col] = new_col



    # -----------------------------------------------------------------------------------------------
    # Chuẩn hóa dấu câu
    # -----------------------------------------------------------------------------------------------
    data['rawText'] = data['rawText'].progress_apply(
        lambda x: (
            re.sub('[“”‘’]', '"', x)
        )
    )



    # -----------------------------------------------------------------------------------------------
    # Gộp câu
    # -----------------------------------------------------------------------------------------------
    for i in tqdm(range(len(data)), desc = "Gộp câu"):
        rawtext = data['rawText'][i]
        paraindex = data['paraIndex'][i]
        
        if len(rawtext) < 3:
            continue
        if paraindex is None:
            data['rawText'].loc[data['paraIndex'] == data['parentIndex'][i]] = data['rawText'].loc[data['paraIndex'] == data['parentIndex'][i]] + " ? " + data['rawText'][i]
        # else: 
        #     data['rawText'][i] = data['rawText'][i] # wtf???
    data = data.dropna().reset_index(drop=True)


    # -----------------------------------------------------------------------------------------------
    # Tách heading + xử lý heading
    # Ta sẽ tách heading từ rawText. Dựa vào heading, ta sẽ xác định paraName và paraClassification
    # Trường dữ liệu ParaName và ParaClassification sẽ được tạo ra từ quy tắc này.
    # Trường dữ liệu segmentedText sẽ được tạo ra từ quy tắc này nhưng chưa mang đầy đủ thông tin, 
    # phải đưa qua NLP để tokenize.
    # -----------------------------------------------------------------------------------------------
    default_paraname = data['fileName'][0][:-5].replace('_','.')
    logging.info(f"Xử lý paraName")
    contents = (
        pd.DataFrame(data, dtype=str)
        .apply(
            lambda row: self.udf_process_sentence(row, default_paraname), 
            axis = 1
        )
    )

    # Pandas - Uncomment code này và comment code trên để chạy trên Pandas
    # contents = data.progress_apply(udf_process_sentence, axis = 1).apply(json.loads)
    # Tạo các cột mới -- [TODO]: Có thể gộp bước này vào UDF hay không?
    data['paraName'] = ''
    data['segmentedText'] = ''
    data['paraClassification'] = ''
    for idx, content in enumerate(tqdm(contents, desc="Lưu ParaName và dữ liệu phân mảnh")):
        data['paraName'][idx] = content['paraName']
        data['segmentedText'][idx] = content['segmentedText']
        data['paraClassification'][idx] = content['paraClassification']



    # -----------------------------------------------------------------------------------------------
    # Tokenize (phân mảnh/word segmentation) câu
    # Hoàn thiện trường dữ liệu segmentedText
    # -----------------------------------------------------------------------------------------------
    logging.info(f"Phân đoạn/tokenize câu")
    data['segmentedText'] = Utils.NLPHelper.segmentize(data['segmentedText'].tolist())



    # -----------------------------------------------------------------------------------------------
    # Xử lý nội dung thừa và drop các hàng không có text
    # -----------------------------------------------------------------------------------------------
    logging.info(f"Xử lý nội dung thừa")
    termination_index = None
    for index in data.index:
        if data.loc[index, 'rawText'].lower().startswith('mẫu số'):
            termination_index = index
            break
        if data.loc[index, 'rawText'].lower().startswith('phụ lục'):
            termination_index = index
            break
    if termination_index is not None: data = data.drop(data.index[termination_index:]).reset_index(drop=True)


    # Kiểm tra và loại bỏ các hàng không có text, NGOẠI TRỪ hàng đầu vì nó là hàng chỉ thị điểm bắt đầu dữ liệu
    has_text = data['segmentedText'].apply(lambda x: len(x) > 0 and x != '')
    # Update 2024/03/05: Bổ sung kiểm tra paraName do có thể có trường hợp có paraName nhưng không có text
    has_heading = data['paraName'].apply(lambda x: len(x) > 0 and x != '') 
    # Update 2024/03/11: Bổ sung kiểm tra paraClassification do cần bỏ trường hợp văn bản
    non_vanban  = data['paraClassification'].apply(lambda x: x.lower() != "vanban")
    has_text[0] = True # Bỏ qua hàng chỉ thị điểm bắt đầu dữ liệu
    data = data[has_text | (has_heading & non_vanban)].reset_index(drop=True).copy(deep=True)



    # -----------------------------------------------------------------------------------------------
    # Xử lý sửa đổi - bổ sung hay reference đến 1 đoạn văn nào đó
    # 
    # Mục đích: Với các văn bản sửa đổi bổ sung, hay mở rộng ra là các văn bản 
    # tham chiếu đến 1 đoạn văn nào đó, ta cần biết được đoạn văn đó là đoạn văn nào
    # và nó nằm ở đâu trong văn bản. Trong trường hợp sửa đổi bổ sung, nếu ko có
    # thông tin này, phần index bóc tách ra sẽ bị nhiễu do VB có thể trích dẫn 1 đoạn văn dài
    # 
    # Nguyên lý: Ta sẽ dựa vào dấu ngoặc kép trong câu và quy tắc B-I-O trong NER.
    # Khi gặp dấu ngoặc kép, ta sẽ gán câu đó với nhãn B và các câu sau với nhãn I
    # cho đến khi gặp dấu ngoặc kép tiếp theo thì ta sẽ gán nhãn O cho các câu sau.
    # 
    # Hạn chế: Cách làm này chưa xử lý được trường hợp OCR nhận dạng sai dấu ngoặc kép
    # 
    # Trường dữ liệu ParaModification sẽ được tạo ra từ quy tắc này.
    # -----------------------------------------------------------------------------------------------
    logging.info(f"Xử lý sửa đổi - bổ sung")
    data['paraModification'] = 'O'

    previous_quotation_index = None
    for index in tqdm(data.index, "Xử lý sửa đổi - bổ sung"):
        text = data.loc[index, 'rawText']
        pidx = data.loc[index, 'paraIndex']
        if pidx == "": continue


        for _ in re.finditer(r'"', text):
            if previous_quotation_index is None:
                # Đánh dấu BEGIN
                data.loc[index, 'paraModification'] = 'B'

                # Trường hợp dò được dấu ngoặc kép đầu tiên
                # Ghi nhận lại vị trí của dấu ngoặc kép đầu tiên
                previous_quotation_index = index
            else:
                # Trường hợp dò được dấu ngoặc kép thứ 2 nhưng KHÔNG cùng vị trí với dấu ngoặc kép trước đó => đánh dấu lại INSIDE
                if index != previous_quotation_index: 
                    data.loc[index, 'paraModification'] = 'I'

                # Reset lại vị trí của dấu ngoặc kép đầu tiên vì đã hết cặp ngoặc
                previous_quotation_index = None

        if previous_quotation_index is not None and index != previous_quotation_index:
            data.loc[index, 'paraModification'] = 'I'


    # with open("__pycache__/test.json", "wb") as f:
    #     data[["rawText", "paraModification"]].to_json(f, orient="records", force_ascii=False, indent=4)

    # -----------------------------------------------------------------------------------------------
    # Lưu lại dữ liệu
    # -----------------------------------------------------------------------------------------------
    logging.info(f"Tiền xử lý dữ liệu thành công")
    return data

