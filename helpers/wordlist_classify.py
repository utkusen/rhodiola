#!/usr/bin/env python
# encoding: utf-8

import multiprocessing
from textwrap import dedent
from itertools import izip_longest
import nltk
from nltk import word_tokenize
import os
from nltk.corpus import wordnet

def process_chunk(word):
    word = ''.join([i for i in word if i.isalpha()])
    if not wordnet.synsets(word):
        pass
    else:
        result = nltk.tag.pos_tag([word.rstrip()])[0][1]
        os.system('echo ' + result + ' >> result_ashley.txt')

def grouper(n, iterable, padvalue=None):
    """grouper(3, 'abcdefg', 'x') -->
    ('a','b','c'), ('d','e','f'), ('g','x','x')"""

    return izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

if __name__ == '__main__':

    files = open("ashley.txt", "r").read()
    test_data = dedent(files)
    test_data = test_data.split("\n")

    p = multiprocessing.Pool(4)
    i=0
    for chunk in grouper(1000, test_data):
        p.map(process_chunk, chunk)
        print i
        i = i+1