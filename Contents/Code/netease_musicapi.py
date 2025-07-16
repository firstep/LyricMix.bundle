# -*- coding: utf-8 -*-
# Author: firstep <https://github.com/firstep>
# Created: 2025-07-08
# LyricMix.bundle - Netease Music API Module
import string
import binascii
import random
import json

import urllib

import utils
from core import MusicApiBase

class NeteaseMusicApi(MusicApiBase):
    NOT_LOGIN_CODE = 50000005
    NONCE = "0CoJUm6Qyw8W8jud"
    MODULUS = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    PUBLIC_KEY = "010001"
    AES_IV = "0102030405060708"
    COMMON_HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "Referer": "https://music.163.com/",
        }

    def __init__(self):
        self.secret_key = self.create_secret_key(16)
        self.encode_key = self.rsa_encode(self.secret_key)
        self.headers = dict(self.COMMON_HEADERS)

    def search(self, artist=None, album=None, track=None):
        url = "https://music.163.com/weapi/cloudsearch/get/web"

        params = {
            "csrf_token": "",
            "limit": "10",
            "offset": "0"
        }

        # 1: 单曲, 10: 专辑, 100: 歌手, 1000: 歌单, 1002: 用户, 1004: MV, 1006: 歌词, 1009: 电台, 1014: 视频, 1018:综合, 2000:声音
        if artist and not album and not track :
            params["type"] = "100"
            params["s"] = utils.extract_chinese_name(utils.ch_t2s(artist))
        elif artist and album:
            params["type"] = "10"
            params["s"] = utils.extract_chinese_name(utils.ch_t2s(artist)) + " " + utils.ch_t2s(album)
        elif artist and track:
            params["type"] = "1"
            params["s"] = utils.extract_chinese_name(utils.ch_t2s(artist)) + " " + utils.ch_t2s(track)
        else:
            Log.Warn("[search] Search params not valid, artist: %s, album: %s, track: %s", artist, album, track) # type: ignore
            return []
        Log.Debug("[search] Search params: %s", params)

        data = self.exchange(url, data=self.encode_data(json.dumps(params)))
        if not data:
            return []
        
        if params["type"] == "100":
            return data["result"].get("artists", [])
        elif params["type"] == "10":
            return data["result"].get("albums", [])
        elif params["type"] == "1":
            return data["result"].get("songs", [])
        else:
            return data["result"]

    def album_info(self, album_id):
        url = "https://music.163.com/weapi/v1/album/{}?csrf_token=".format(album_id)

        params = {
            "csrf_token": ""
        }

        return self.exchange(url, data=self.encode_data(json.dumps(params)))

    def lyrics(self, track_id):
        url = "https://music.163.com/weapi/song/lyric?csrf_token="

        params = {
            "id": track_id,
            "os": "pc",
            "lv": "-1",     # native lyrics
            "kv": "-1",
            "tv": "-1",     # translated lyrics
            "rv": "-1",     # transliteration lyrics
            "yv": "-1",     # word lyrics
            "ytv": "-1",    # word lyrics
            "yrv": "-1",    # word lyrics
            "csrf_token": ""
        }

        data = self.exchange(url, data=self.encode_data(json.dumps(params)))
        return data
    
    def set_secret(self, secret, key=None):
        Log.Debug("[lyrics] Setting Netease Music API secret key: %s", secret)
        self.headers["Cookie"] = secret.strip() if secret else ""

    def enabled(self):
        cookie = self.headers.get("Cookie")
        return cookie is not None and cookie != ""
    
    def encode_data(self, params):
        return {
            "params": utils.aes_encode(utils.aes_encode(params, self.NONCE, self.AES_IV), self.secret_key, self.AES_IV),
            "encSecKey": self.encode_key
        }

    def exchange(self, url, data=None, json=None):
        try:
            req = HTTP.Request(
                url, 
                data=urllib.urlencode(data) if isinstance(data, dict) else data, 
                headers=self.headers, 
                method='POST'
            )
        except Exception as e:
            import traceback
            Log.Error("[exchange] Netease Music API Error: %s\n", e, traceback.format_exc())
            return None
    
        content = req.content
        if content == "":
            Log.Warn("[exchange] Empty Response")
            return None
        
        data = JSON.ObjectFromString(content)
        if data["code"] == self.NOT_LOGIN_CODE:
            Log.Warn("[exchange] Not Login")
            self.headers["Cookie"] = ""  # clear cookie
            return None
        elif data["code"] != 200:
            Log.Warn("[exchange] %s, response: %s", data["code"], content)
            return None
        
        return data
    
    @staticmethod
    def create_secret_key(length):
        chars = string.digits + string.ascii_letters
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def rsa_encode(text):
        text_str = text[::-1]  # reverse the string
        hex_str = binascii.hexlify(text_str.encode('utf-8')).decode('utf-8') # convert to hex string
        a = int(hex_str, 16)
        b = int(NeteaseMusicApi.PUBLIC_KEY, 16)
        c = int(NeteaseMusicApi.MODULUS, 16)
        
        key = pow(a, b, c)
        key_hex = "{:x}".format(key)
        key_hex = key_hex.zfill(256)  # fill with leading zeros
    
        return key_hex[-256:] if len(key_hex) > 256 else key_hex



