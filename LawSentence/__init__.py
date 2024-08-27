import pandas as pd
import math
import difflib 
from config import *
import requests
import re
from unidecode import unidecode
import Utils.NLPHelper





class Sentence:
    def __init__(self, sentence, support_verb_data):
        self.sentence = sentence
        self.special_verb_data = support_verb_data
    
        """
        Parameters
        ----------
        `sentence`: `string`
            1 sentence
        """       
    
    
    def processing_law_sentence(self, level, van_ban_name):
        pattern_chuong  = '^((chương)( )*[IVXABCD0-9]+)'
        pattern_muc     = '^((mục)( )*[IVXABCD0-9]+)'
        pattern_dieu    = '^((điều)( )*[IVXABCD0-9]+)'
        pattern_khoan   = '^([IVXABCD0-9]+)'
        pattern_diem    = '^([a-zđ]|(-))'
        pattern_mauso   = '^((mẫu số)( )*[IVXABCD0-9]+)'
        level = int(float(level))
        if level == 1: #Chuong
            text = ''
            kq = re.findall(pattern_chuong, self.sentence, flags=re.IGNORECASE)
            kq1 = re.findall(pattern_mauso, self.sentence, flags=re.IGNORECASE)
            if len(kq) == 0 and len(kq1) == 0: 
                index = ''
                classification = ''
            else: 
                if len(kq) != 0:
                    w = kq[0][0].split()
                    classification = unidecode(w[0]).lower().capitalize()
                    index = w[1]
                    text = re.sub(pattern_chuong, '', self.sentence, flags=re.IGNORECASE).replace('?', '')[1:].strip().lower()
                elif len(kq1) != 0:
                    w = kq1[0][0].split()
                    classification = unidecode(w[0]).lower().capitalize()
                    index = w[1]
                    text = re.sub(pattern_mauso, '', self.sentence, flags=re.IGNORECASE).replace('?', '')[1:].strip().lower()
        elif level == 2: #Muc
            kq = re.findall(pattern_muc, self.sentence, flags=re.IGNORECASE)
            if len(kq) == 0:
                index = ''
                classification = ''
            else:
                w = kq[0][0].split()
                classification = unidecode(w[0]).lower().capitalize()
                index = w[1]
            text = re.sub(pattern_muc, '', self.sentence, flags=re.IGNORECASE).replace('?', '')[1:].strip().lower()
        elif level == 3: #Dieu
            kq = re.findall(pattern_dieu, self.sentence, flags=re.IGNORECASE)
            if len(kq) == 0:
                index = ''
                classification = ''
            else:
                w = kq[0][0].split()
                classification = unidecode(w[0])
                index = w[1]
            text = re.sub(pattern_dieu, '', self.sentence, flags=re.IGNORECASE)[1:].strip()
        elif level == 4: #Khoan
            kq = re.findall(pattern_khoan, self.sentence, flags=re.IGNORECASE)
            if len(kq) == 0:
                index = ''
                classification = ''
            else:
                classification = 'Khoan'
                index = kq[0]
            text = re.sub(pattern_khoan, '', self.sentence, flags=re.IGNORECASE)[1:].strip()
        elif level == 7: #Diem 
            kq = re.findall(pattern_diem, self.sentence, flags=re.IGNORECASE)
            if len(kq) == 0:
                index = ''
                classification = ''
            else:
                index = kq[0][0]
                classification = 'Diem'
            text = re.sub(pattern_diem, '', self.sentence, flags=re.IGNORECASE)[1:].strip()
        elif level == 8:    
            kq = re.findall(pattern_diem, self.sentence, flags=re.IGNORECASE)
            if len(kq) == 0:
                index = ''
                classification = ''
            else:
                index = kq[0][0]
                classification = 'HaDiem'
            text = re.sub(pattern_diem, '', self.sentence, flags=re.IGNORECASE)[1:].strip()
        else: 
            classification = 'VanBan'
            index = van_ban_name
            text = ''
        return classification, index, text
    
    #-------------------------------------------------------------------------------------------------------#    
    """
        Output: 1 sentence gồm các từ đã được tokenize
    """
    def segmentize(self):
        return Utils.NLPHelper.segmentize(self.sentence)
    
    #-------------------------------------------------------------------------------------------------------#
    """
        Output: Tất cả các mệnh đề được tìm thấy trong câu bằng rule-based    
    """
    def find_all_menh_de(self):
        ds_menh_de = []
        vt_dau_cau = []
        words = self.sentence.split()
        for i in range(len(words)):
            if words[i] == '.' or words[i] == ':' or words[i] == '?':
                vt_dau_cau.append(i)
        subarrays = []
        current_subarray = ""
        for i in range(len(words)):
            current_subarray = current_subarray + words[i] + " "
            if i in vt_dau_cau:
                subarrays.append(current_subarray)
                current_subarray = ""
        if current_subarray:
            subarrays.append(current_subarray)
        mde = []
        for i, subarray in enumerate(subarrays, 1):
            mde.append(subarray)
        if len(mde) != 0:
            cnt = len(mde)-1
            for i in reversed(range(cnt)): 
                mde[i] = ' '.join(mde[i].replace('?','').split())
                if len(mde[i+1]) == 0:
                    mde.pop(i+1)
                    continue
                if mde[i+1][0].isupper(): 
                    continue
                
                mde[i] = mde[i] + " " + mde[i+1]
                mde.pop(i+1)
        return mde


    def find_special_verb(self):
        """
            Đưa ra danh sách các mệnh lệnh xuất hiện trong câu
        """
        special_verbs_data = self.special_verb_data
        special_verb_result = pd.DataFrame(columns=["Index", "Word", "Category"])

        assert (not special_verbs_data.empty)
        for special_verb_index in special_verbs_data.index:

            word_list = special_verbs_data.loc[special_verb_index, 'Words']
            words_sentence = self.sentence.lower().split()
            for word_index, word_value in enumerate(words_sentence):
                if word_value in word_list:
                    special_verb_result.loc[len(special_verb_result.index)] = {
                        "Index": word_index,
                        "Word": word_value,
                        "Category": special_verbs_data.loc[special_verb_index, 'Group']
                    }           
        return special_verb_result


