import os
import json
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Union

import Utils.NLPHelper
from LawIEModel import LawIEModel
from LawSentence import Sentence
from DependencyParsing import DependencyParsing
from Utils.DataHelper.SupportData import SupportData



def save_error_data_ThamQuyenChuDe(json_input_data: dict):
    logging.info("Lưu dữ liệu lỗi")
    err_folder = f"{datetime.now()}".replace(":", "-")
    os.makedirs(f"Errors/{err_folder}", exist_ok=True)


    pd.read_excel("test.xlsx").to_excel(f"Errors/{err_folder}/pre-higher-id.xlsx")
    with open(f"Errors/{err_folder}/input.json", "w", encoding="utf-8") as f:
        json.dump(json_input_data, f, ensure_ascii=False, indent=4)
    

def refine_data(file):
    try:
        json_content = json.load(file.file)['document']
        return LawIEModel(
            json_content, 
            do_preprocess_path = True,
            do_find_higher_id = False,
            do_pos_dep_parsing = False,
            do_discourse_parsing = False,
        ).get_refined_data()
    except Exception as e:
        logging.fatal(f"Error: {e}", exc_info=True)
        return {}



def get_ThamQuyen(file):
    try:
        json_content = json.load(file.file)['document']
        return LawIEModel(json_content).SRLChuDeThamQuyen()
    except Exception as e:
        logging.fatal(f"Error: {e}", exc_info=True)
        save_error_data_ThamQuyenChuDe(json_content)
        return {}



def get_ChuDe(file):
    try:
        json_content = json.load(file.file)['document']
        return LawIEModel(json_content).SRLChuDeThamQuyen(chu_de_only=True)
    except Exception as e:
        logging.fatal(f"Error: {e}", exc_info=True)
        return {}



def get_SRL(file):
    try:
        json_content = json.load(file.file)['document']
        return LawIEModel(
            json_content,
            do_preprocess_path = True,
            do_find_higher_id = True,
            do_pos_dep_parsing = True,
            do_discourse_parsing = True,
        ).PlainSRL()
    except Exception as e:
        logging.fatal(f"Error: {e}", exc_info=True)
        return {}

        

def get_SRL_sentence(input):
    try:
        if isinstance(input, str): text = [input]
        else: text = input

        # Lấy dữ liệu hỗ trợ
        dp_labels = SupportData().get_dp_labels()
        translation_dp = SupportData().get_translation_dp()


        srl_batch_df = pd.DataFrame(columns = ["text", "dp"])
        srl_batch_df["text"] = pd.Series(text).apply(lambda x: Utils.NLPHelper.deindex(x)[1])
        srl_batch_df["text"] = Utils.NLPHelper.segmentize(srl_batch_df["text"].tolist())
        srl_batch_df["dp"] = Utils.NLPHelper.phonlp_annotate(srl_batch_df["text"].tolist())

        
        result = srl_batch_df.apply(
            lambda x: DependencyParsing(
                x["text"], 
                Sentence(
                    x["text"], 
                    SupportData().get_special_verbs()
                ).find_special_verb(), 
                x["dp"]
            ).lay_thong_tin_cho_root(),
            axis=1
        ).tolist()

        # df_sv = Sentence(text, SupportData().get_special_verbs()).find_special_verb()
        # kq = DependencyParsing(text, df_sv, dp_data).lay_thong_tin_cho_root()

        for idx in range(len(result)):
            for label in dp_labels:
                result[idx][translation_dp.get(label, "-1")] = result[idx].get(label, [""])


        if isinstance(input, str): result = result[0]
        return result
    

    except Exception as e:
        logging.fatal(f"Error: {e}", exc_info=True)
        return {}








if __name__ == "__main__":
    input_json_path = ""
    output_json_path = ""

    with open(input_json_path, "r", encoding="utf-8") as f:
        json_content = json.load(f)

    result = LawIEModel(json_content)