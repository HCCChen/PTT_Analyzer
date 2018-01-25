# -*- coding: utf-8 -*-                                                                                                                                                                                  

import os
import re
import requests
import time
import datetime
import sys
import json
import math
import string
import argparse
import jieba
import jieba.analyse

class ArticleAnalyzer:
    def __init__(self, rootPath):
        self.rootPath = rootPath
        # load index file
        indexFilePath = self.rootPath + "/index.json"
        with open(indexFilePath, "r") as fp:
            self.articleIndex = json.load(fp)

        self.stopWordList = {}
        with open("stop_words.txt", "r") as fp:
            for line in fp.readlines():
                self.stopWordList[line.strip('\n')] = 1

        jieba.set_dictionary('dict.txt.big')


    def loadArticleMeta(self, filePath):
        with open(filePath, "r") as fp:
            articleMeta = json.load(fp)
        return articleMeta

    def getIDFValue(self, keywordList, topN=20):
        keywordIDFDict = {}
        totalCountOfArticle = len(self.articleIndex)

        for listIdx in range(0, totalCountOfArticle):
            try:
                articleMeta = self.loadArticleMeta(self.articleIndex[listIdx]['filePath'])
                articleString = articleMeta['title'] + '\n' + articleMeta['context']
            except Exception as e:
                continue

            for keywordIdx in range(0, len(keywordList)):
                if not articleString.find(keywordList[keywordIdx]) is -1:
                    if keywordList[keywordIdx] in keywordIDFDict:
                        keywordIDFDict[keywordList[keywordIdx]] += 1
                    else:
                        keywordIDFDict[keywordList[keywordIdx]] = 1

        for idx in range(0, len(keywordList)):
            if keywordList[idx] in keywordIDFDict:
                keywordIDFDict[keywordList[idx]] = math.log(totalCountOfArticle / keywordIDFDict[keywordList[idx]])

        return keywordIDFDict

    def getKeywordSetByTFIDF(self, filePath, topN=20):
        articleMeta = self.loadArticleMeta(filePath)
        article = articleMeta['title'] + '\n' + articleMeta['context']
        # TF-IDF
        # Get keyword list and TF for each word
        wordListDwarf = list(jieba.cut(article, cut_all=False))
        wordList = []   
        for idx in range(0, len(wordListDwarf)):
            if not wordListDwarf[idx] in self.stopWordList:
                wordList.append(wordListDwarf[idx])

        keywordFreqDict = {}
        keywordTFIDFDict = {}
        keywordList = []   
        for idx in range(0, len(wordList)):
            if wordList[idx] in keywordFreqDict:
                keywordFreqDict[wordList[idx]] += 1
            else:
                keywordFreqDict[wordList[idx]] = 1 
                keywordList.append(wordList[idx])

        # Get IDF info
        keywordIDFDict = self.getIDFValue(keywordList)

        # Calculate TF-IDF value
        for idx in range(0, len(keywordList)):
            if wordList[idx] in keywordFreqDict:
                keywordFreqDict[keywordList[idx]] = keywordFreqDict[keywordList[idx]] / len(wordList)
                keywordTFIDFDict[keywordList[idx]] = keywordFreqDict[keywordList[idx]] * keywordIDFDict[keywordList[idx]]

        del(wordListDwarf)
        del(wordList)
        sortedTFIDFResult = sorted(keywordTFIDFDict.items(), key=lambda d: d[1], reverse=True)

        return sortedTFIDFResult[0:topN]


    def getKeywordSetByTextRank(self, filePath):
        articleMeta = self.loadArticleMeta(filePath)
        article = articleMeta['title'] + '\n' + articleMeta['context']
        # TextRank
        wordFromTextRank = jieba.analyse.textrank(article, withWeight=True)
        return wordFromTextRank


# Main function
if __name__ == '__main__':
    articleAnalyzer = ArticleAnalyzer('data/Gossiping')
    #print(articleAnalyzer.getKeywordSetByTextRank("data/Gossiping/2018_01_23/Gossiping_M_1516679909_A_5F9.json"))
    #print(articleAnalyzer.getKeywordSetByTFIDF("data/Gossiping/2018_01_23/Gossiping_M_1516679909_A_5F9.json"))
