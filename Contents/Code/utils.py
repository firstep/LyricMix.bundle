# -*- coding: utf-8 -*-
# Author: firstep <https://github.com/firstep>
# Created: 2025-07-08
# LyricMix.bundle - Utility Module
import base64
import re
import os

from crypto.cipher.aes_cbc import AES_CBC

import t2s

try:
    bytes
except NameError:
    def bytes(iterable):
        return ''.join(chr(x) for x in iterable)

def aes_encode(text, key, iv):
    if isinstance(text, str):
        text = text.encode('utf-8')

    aes = AES_CBC(key.encode('utf-8'))
    ciphertext = aes.encrypt(text, iv=iv.encode('utf-8'))
    return base64.b64encode(ciphertext).decode('utf-8')

def ch_t2s(line):
    # replace chars
    new_line = ''
    for i in range(len(line)):
        c = line[i]
        new_line += t2s.chars.get(c, c) # type: ignore
    print(new_line)
    line = new_line
    # replace phrase
    for key in t2s.phrase:
        if key not in line:
            continue
        line = line.replace(key, t2s.phrase[key])
    return line

def levenshtein_score(raw, text):
    return 100 - (10 * abs(String.LevenshteinDistance(raw.lower(), text.lower())))

def extract_chinese_name(text):
    pattern = r'^[A-Za-z0-9\s]+\(([^\)]+)\)$'
    match = re.match(pattern, text)
    if match and match.end() == len(text):  # Simulate fullmatch functionality
        return match.group(1)
    return text

def has_local_lyric(track):
    lyric_file = ""
    if track.items:
        for item in track.items:
            for part in item.parts:
                if part.file:
                    (file_root, fext) = os.path.splitext(part.file)
                    lyric_file = file_root + '.lrc'
                    if os.path.exists(file_root + '.lrc'):
                        return True, lyric_file
    return False, lyric_file