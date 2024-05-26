import piheaan as heaan
from piheaan.math import sort
from piheaan.math import approx # for piheaan math function
import math
import numpy as np
import pandas as pd
import os

def calculate_result(user_id):
    # Function for making the dictionary by User ID
    def making_dict(column_name):
        result = df.groupby('User ID')[column_name].apply(list).reset_index()
        user_dictionary = {}
        for index, row in result.iterrows():
            user_dictionary[row[0]] = row[1]
        return user_dictionary

    # price is Average Price
    user_dict_price = making_dict('price')
    user_dict_price_diff = making_dict('평균 가격 대비')
    user_dict_qty = making_dict('qty')

    # To decide log_slots and num_slots, find the max length of the user's data
    temp = []
    for i in user_dict_qty.keys():
        temp.append(len(user_dict_qty[i]))
    max_len = max(temp)
    max_len

    # Find the most near 2 powered number of max_len
    log_slots = 0
    num_slots = 2**log_slots
    while max_len > num_slots:
        log_slots += 1
        num_slots = 2**log_slots

    data1 = user_dict_qty[user_id]
    actual_len = len(data1)
    data1_padded = [0] * num_slots
    for i in range(len(data1)):
        data1_padded[i] = data1[i]
        
    message_1 = heaan.Message(log_slots)
    for i in range(num_slots):
        message_1[i] = data1_padded[i]

    data2 = user_dict_price_diff[user_id]
    data2_padded = [0] * num_slots
    for i in range(len(data2)):
        data2_padded[i] = data2[i]
        
    message_2 = heaan.Message(log_slots)
    for i in range(num_slots):
        message_2[i] = data2_padded[i]
        
    data3 = user_dict_price[user_id]
    data3_padded = [0] * num_slots
    for i in range(len(data3)):
        data3_padded[i] = data3[i]

    message_3 = heaan.Message(log_slots)
    for i in range(num_slots):
        message_3[i] = data3_padded[i]

    ciphertext_1 = heaan.Ciphertext(context) # qty
    ciphertext_2 = heaan.Ciphertext(context) # price difference 현재 가격과 평균 가격 차이
    ciphertext_3 = heaan.Ciphertext(context) # price 평균 가격

    enc.encrypt(message_1, pk, ciphertext_1)
    enc.encrypt(message_2, pk, ciphertext_2)
    enc.encrypt(message_3, pk, ciphertext_3)

    # (ciphertext * ciphertext)
    result_mult = heaan.Ciphertext(context)
    eval.mult(ciphertext_1, ciphertext_2, result_mult)

    result_mult_message = heaan.Message(log_slots)
    dec.decrypt(result_mult, sk, result_mult_message)

    # (ciphertext * ciphertext)
    result_mult2 = heaan.Ciphertext(context)
    eval.mult(ciphertext_1, ciphertext_3, result_mult2)

    result_mult_message2 = heaan.Message(log_slots)
    dec.decrypt(result_mult2, sk, result_mult_message2)

    data = [0.01] * num_slots
    message_01 = heaan.Message(log_slots)
    for i in range(num_slots):
        message_01[i] = data[i]

    ciphertext_4 = heaan.Ciphertext(context) # 0.1만 있는거
    enc.encrypt(message_01, pk, ciphertext_4)

    # (ciphertext * ciphertext)
    result_mult3 = heaan.Ciphertext(context)
    eval.mult(ciphertext_4, result_mult2, result_mult3)

    result_mult_message3 = heaan.Message(log_slots)
    dec.decrypt(result_mult3, sk, result_mult_message3)

    data = result_mult_message3
    message = heaan.Message(log_slots)
    for i in range(num_slots):
        message[i] = data[i]
        
    ciphertext = heaan.Ciphertext(context)
    result_inv = heaan.Ciphertext(context)

    enc.encrypt(message, pk, ciphertext)
    approx.inverse(eval, ciphertext, result_inv) 

    decryptor = heaan.Decryptor(context)
    result_inv_message = heaan.Message(log_slots)

    decryptor.decrypt(result_inv, sk, result_inv_message)

    # (message * message)
    result_final_message = heaan.Message(log_slots)
    eval.mult(result_inv_message, result_mult_message, result_final_message)

    # (message * message)
    result_final_message2 = heaan.Message(log_slots)
    eval.mult(result_final_message, message_01, result_final_message2)

    final_result= [] # 한 유저의 각 주식별 수익률
    for i in range(actual_len):
        final_result.append(result_final_message2[i])

    total_result = sum(result_mult_message)/sum(result_mult_message2) # 한 유저의 전체 수익률

    return final_result, total_result