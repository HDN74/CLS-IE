# /*==========================================================================================*\
# **                        _           _ _   _     _  _         _                            **
# **                       | |__  _   _/ | |_| |__ | || |  _ __ | |__                         **
# **                       | '_ \| | | | | __| '_ \| || |_| '_ \| '_ \                        **
# **                       | |_) | |_| | | |_| | | |__   _| | | | | | |                       **
# **                       |_.__/ \__,_|_|\__|_| |_|  |_| |_| |_|_| |_|                       **
# \*==========================================================================================*/


# -----------------------------------------------------------------------------------------------
# Author: Đặng Nhật Huy, Bùi Tiến Thành
# Title: _word2vec.py
# Date: 2024/01/31 15:03:40
# Description: File chứa các hàm liên quan đến mô hình word2vec
# 
# (c) 2023-2024 CMC ATI. All rights reserved.
# -----------------------------------------------------------------------------------------------


import logging
import difflib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
import time



def common_words(self, words1, words2):
    # Find the longest common subsequence
    matcher = difflib.SequenceMatcher(None, words1, words2)
    matches = matcher.get_matching_blocks()

    # Create a new sentence with the common words highlighted
    highlighted_sentence1 = ""
    highlighted_sentence2 = ""
    for match in matches:
        start1 = match.a
        start2 = match.b
        size = match.size
        end1 = start1 + size
        end2 = start2 + size

        # Add the common words to the highlighted sentences
        highlighted_sentence1 += " ".join(words1[start1:end1]) + " "
        highlighted_sentence2 += " ".join(words2[start2:end2]) + " "

    return highlighted_sentence1.strip()




def find_similarity(self, source, target_sentences):
    
    source = source.lower()
    sentences = [source]
    for i in target_sentences:
        sentences.append(i.lower())
    
    data = []
    for sentence in sentences:
        data.append(sentence.split())
    # Xây dựng mô hình word2vec
    gensim_logger = logging.getLogger('gensim')
    gensim_logger.setLevel(logging.DEBUG)
    gensim_logger.propagate = False
    model = Word2Vec(sentences=data, vector_size=100, window=5, min_count=1, workers=4)
    
    # Huấn luyện mô hình
    model.train(data, total_examples=len(data), epochs=10)

    word_vectors = model.wv
    word_vector_dim = model.vector_size
    kq = []
    for i in range(len(data)):
        target_sentence = data[i]
        target_vector = np.zeros(word_vector_dim)
        valid_word_count = 0
        
        for word in target_sentence:
            if word in word_vectors:
                target_vector += word_vectors[word]
                valid_word_count += 1

        if valid_word_count > 0:
            target_vector /= valid_word_count
        if i == 0 :
            source_vector = target_vector
            source_sentence = target_sentence
        else:
            similarity_score = cosine_similarity([source_vector], [target_vector]).flatten()[0]
            
            str = ""
            for i in target_sentence: 
                str = str + i + " "
            kq.append([similarity_score, source_sentence])
    # print(kq)
    #maxx = -1 
    #for j in kq: 
    #    if maxx < j[0]:
    #        maxx = j[0]
    #        KetQua = j
    #sorted_kq = sorted(kq, key=lambda x: x[0], reverse=True)
    KetQua = []
    for j in kq: 
        if j[0] > 0: 
            KetQua.append({
                "score": j[0],
                "higherelement": j[1]
            })
    return KetQua



