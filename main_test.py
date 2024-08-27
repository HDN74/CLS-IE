from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_utils.inferring_router import InferringRouter
from fastapi.middleware.cors import CORSMiddleware 
from fastapi import FastAPI, File, UploadFile, Request
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import uvicorn
import warnings


from helpers import get_SRL, get_SRL_sentence, get_ThamQuyen, get_ChuDe, refine_data
from Utils.DataHelper.SparkAccess import SparkAccess
from Utils.DataHelper.SupportData import SupportData
from Utils.LoggingHelper import initialize_logging
from LawSentence import Sentence
from DependencyParsing import DependencyParsing
import config

initialize_logging()
support_data = SupportData()
support_data.initialize()



sentence = "Ủy ban nhân dân cấp xã có trách nhiệm quản lý, bảo vệ đất chưa sử dụng tại địa phương và đăng ký vào hồ sơ địa chính"
sentence = "Đối với đất có di tích lịch sử - văn hóa, danh lam thắng cảnh bị lấn, bị chiếm, sử dụng không đúng mục đích, sử dụng trái pháp luật thì Chủ tịch Ủy ban nhân dân cấp xã nơi có đất có trách nhiệm phát hiện, ngăn chặn và xử lý kịp thời."
sentence = "Cơ quan tài nguyên và môi trường có trách nhiệm cập nhật các thông tin trong hệ thống theo dõi, đánh giá vào hệ thống thông tin đất đai."
sentence = "Cơ quan tài nguyên và môi trường có trách nhiệm quản lý hệ thống theo dõi và đánh giá; tổ chức thực hiện đánh giá việc thực thi pháp luật, hiệu quả quản lý và sử dụng đất đai, tác động của chính sách, pháp luật về đất đai đến kinh tế - xã hội và môi trường trên phạm vi cả nước và các địa phương; kết quả đánh giá được gửi định kỳ đến Chính phủ, Quốc hội."
sentence = "Bộ Tài nguyên và Môi trường, cơ quan quản lý đất đai của tỉnh, thành phố trực thuộc trung ương, huyện, quận, thị xã, thành phố thuộc tỉnh có trách nhiệm cung cấp tài liệu cần thiết và phối hợp với cơ quan nhà nước có thẩm quyền để giải quyết tranh chấp địa giới hành chính."

sentence = "Căn cứ vào quy hoạch phát triển nguồn nhân lực quốc gia, Bộ trưởng Bộ Khoa học và Công nghệ phê duyệt quy hoạch phát triển nguồn nhân lực khoa học và công nghệ trên cơ sở đề xuất của bộ, cơ quan ngang bộ, cơ quan thuộc Chính phủ, Ủy ban nhân dân cấp tỉnh và cơ quan nhà nước khác."
sentence = "Nghị quyết này quy định thể thức và kỹ thuật trình bày văn bản quy phạm pháp luật của Quốc hội, Ủy ban Thường vụ Quốc hội, Chủ tịch nước và văn bản quy phạm pháp luật liên tịch trong đó Ủy ban Thường vụ Quốc hội là một chủ thể ban hành (sau đây gọi chung là văn bản)."
sen = Sentence(sentence, SupportData().get_special_verbs())
sentence = sen.segmentize()

sen = Sentence(sentence, SupportData().get_special_verbs())
df_sv = sen.find_special_verb()
# print(df_sv)
dp = DependencyParsing(sentence=sentence, df_special_verb=df_sv)
DP = dp.update_DP()
# print(DP)
result = dp.extract_agency_authority_jurisdiction(["phát_triển nguồn nhân_lực "])
# print(result)
# result = dp.information_extraction(DP)
# #print(result)
# result.to_excel('/home/huydn74/Documents/legal-information-extraction-main/KQ.xlsx', index=False)
# DP.to_excel('/home/huydn74/Documents/legal-information-extraction-main/KQDP.xlsx', index=False)
# menh_lenh = dp.make_class_and_relationship_knowledge(result, DP)
# print(menh_lenh)
# for i in range(len(result)):
#     head_category = result['Head_Category'][i]
#     information_category = result['Information_Category'][i]
#     head = result['Head'][i]
#     information = result['Information'][i]
#     if information_category == 'Điều kiện' or information_category == 'Mục tiêu':
#         print(f"{information_category}:")
#         print(f"-   Thong tin: {head}")
#         print(f"-   Dieu kien: {information} ") 
# for i in menh_lenh:
#     loai_thong_tin = i['loai_thong_tin']
#     menh_lenh = DP[DP.Index == int(i['loai_menh_lenh'])].iloc[0].Word
#     if i['chu_the'] == '':
#         chu_the = ''
#     else:
#         chu_the = ""
#         for j in DP[DP.Index == int(i['chu_the'])].iloc[0].InformationWords: 
#             chu_the = chu_the + DP[DP.Index == j].iloc[0].Word + " "
#     if i['dong_tu_chinh'] == '':
#         dong_tu_chinh = ''
#     else:
#         dong_tu_chinh = DP[DP.Index == int(i['dong_tu_chinh'])].iloc[0].Word
#     if i['van_de_phap_ly'] == '':
#         van_de_phap_ly = '1'
#     else:
#         van_de_phap_ly = ""
#         for j in DP[DP.Index == int(i['van_de_phap_ly'])].iloc[0].InformationWords: 
#             van_de_phap_ly = van_de_phap_ly + DP[DP.Index == j].iloc[0].Word + " "
#     print(f"Quyen han:")
#     print(f"-  Loai menh lenh: {menh_lenh}")
#     print(f"-  Chu the thuc hien: {chu_the}")
#     print(f"-  Dong tu chinh: {dong_tu_chinh}")
#     print(f"-  Van de phap ly: {van_de_phap_ly}")


# for i in menh_lenh:
#     loai_thong_tin = i['loai_thong_tin']
#     menh_lenh = i['loai_menh_lenh']
#     chu_the = i['chu_the']
#     dong_tu_chinh = i['dong_tu_chinh']
#     van_de_phap_ly = i['van_de_phap_ly']
#     print(f"Quyen han:")
#     print(f"-  Loai menh lenh: {menh_lenh}")
#     print(f"-  Chu the thuc hien: {chu_the}")
#     print(f"-  Dong tu chinh: {dong_tu_chinh}")
#     print(f"-  Van de phap ly: {van_de_phap_ly}")


   