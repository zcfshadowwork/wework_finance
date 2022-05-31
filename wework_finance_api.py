# -*- coding:utf-8 -*-

import base64
import ctypes
import json
import random
import os
import time
import Crypto

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from . import conf


class WeworkFinanceApi:

    def __init__(self, corp_id, chat_secret, pri_key):
        self.corp_id = corp_id
        self.chat_secret = chat_secret
        self.pri_key = pri_key
        self.dll = ctypes.cdll.LoadLibrary("libWeWorkFinanceSdk_C.so")
        self.cipher = Crypto.Cipher.PKCS1_v1_5.new(RSA.importKey(self.pri_key))
        self.new_sdk = self.dll.NewSdk()
        self.result = self.dll.Init(self.new_sdk, self.corp_id.encode(), self.chat_secret.encode())

    def get_msg(self, seq=0):
        # 从接口提取消息 每次获取1000条
        if self.result != 0:
            raise Exception('api error')
        s = self.dll.NewSlice()
        res = self.dll.GetChatData(self.new_sdk, seq, 1000, '', '', 0, ctypes.c_long(s))
        if res != 0:
            raise Exception('api error')
        data = self.dll.GetContentFromSlice(s)
        data = ctypes.string_at(data, -1).decode("utf-8")
        self.dll.FreeSlice(s)
        raw_data = json.loads(data)
        if raw_data["errcode"] == 301042:
            raise Exception("wrong ip!")
        elif raw_data['errcode'] == 301052:
            raise Exception("please recharge")
        data = raw_data.get('chatdata')
        if not data:
            return None, []
        next_seq = data[-1].get('seq')
        result_list = [self._decrypt_msg(msg) for msg in data]
        return next_seq, result_list

    def _decrypt_msg(self, msg):
        # 解密消息
        encrypt_key = self.cipher.decrypt(base64.b64decode(msg.get('encrypt_random_key')), "ERROR")
        ss = self.dll.NewSlice()
        self.dll.DecryptData(encrypt_key, msg.get('encrypt_chat_msg').encode(), ctypes.c_long(ss))
        decrypt_msg = self.dll.GetContentFromSlice(ss)
        decrypt_msg = ctypes.string_at(decrypt_msg, -1).decode("utf-8")
        decrypt_msg = json.loads(decrypt_msg)
        self.dll.FreeSlice(ss)
        return decrypt_msg


    def get_media_data(self, sdk_file_id, file_type, file_size, file_name=None):
        # 获取视频、图片或者声音文件
        file_chunk_size, file_end_chunk_size = self._get_chunk_size(file_size)
        file_name = file_name or self._get_file_name(file_type)
        indexbuf = b''
        is_finish = False
        while True:
            data_struct = self.dll.NewMediaData()
            res = self.dll.GetMediaData(self.new_sdk, indexbuf,
                                        ctypes.create_string_buffer(sdk_file_id.encode()),
                                        b'', b'', 0, ctypes.c_long(data_struct))
            if res != 0:
                raise Exception('api error')
            data = self.dll.GetData(data_struct)
            if self.dll.IsMediaDataFinish(data_struct):
                chunk_size = file_end_chunk_size
                is_finish = True
            else:
                chunk_size = file_chunk_size
                is_finish = False
            data = ctypes.string_at(data, chunk_size)
            with open(CONF.temp_folder + file_name, 'ab+') as f:
                f.write(data)
            if is_finish:
                self.dll.FreeMediaData(data_struct)
                break
            else:
                indexbuf = self.dll.GetOutIndexBuf(data_struct)
                indexbuf = ctypes.string_at(indexbuf, -1)
                self.dll.FreeMediaData(data_struct)
        return file_name


    @staticmethod
    def _get_chunk_size(file_size):
        end_file_size = file_size % (512 * 1024) or 512 * 1024
        return 512 * 1024, end_file_size

    @staticmethod
    def _get_file_name(file_type):
        if file_type in conf.FILE_TYPE_MAP:
            fn = time.strftime('%Y%m%d%H%M%S') + '_%d' % random.randint(0, 100) + conf.FILE_TYPE_MAP[file_type]
            return fn

    @staticmethod
    def _bytes(data):
        if isinstance(data, str):
           data = data.encode('utf8')
        return data


WEWORK_FINANCE_API = WeworkFinanceApi(conf.CORP_ID, conf.CHAT_SECRET, conf.PRI_KEY )

if __name__ == '__main__':
    # 会话存档支持存档语音通话（非会议），视频通话暂不支持，图片是jpg格式、语音是amr格式、视频是mp4格式、文件格式类型包括在消息体内，表情分为动图与静态图，在消息体内定义
    pass
