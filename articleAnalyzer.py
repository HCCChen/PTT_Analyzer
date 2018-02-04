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

        self.stopWordDict = {}
        with open("stop_words.txt", "r") as fp:
            for line in fp.readlines():
                self.stopWordDict[line.strip('\n')] = 1

        self.wordIDFDict = {}
        try:
            with open("wordIDF.json", "r") as fp:
                self.wordIDFDict = json.load(fp)
        except Exception as e:
            print('Cannot load IDF library.')

        jieba.set_dictionary('dict.txt.big')


    def loadArticleMeta(self, filePath):
        with open(filePath, "r") as fp:
            articleMeta = json.load(fp)
        return articleMeta

    def __getIDFValue(self, keywordListParameter, topN=20):
        keywordIDFDict = {}
        totalCountOfArticle = len(self.articleIndex)
        keywordList = list(keywordListParameter)

        # Check IDF dict first
        for idx in range(len(keywordList)-1, -1, -1):
            if keywordList[idx] in self.wordIDFDict:
                keywordIDFDict[keywordList[idx]] = self.wordIDFDict[keywordList[idx]]
                keywordList.pop(idx)

        if len(keywordList) == 0:
            return keywordIDFDict

        # If have keywork not in IDF dict, search all file
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
                self.wordIDFDict[keywordList[idx]] = keywordIDFDict[keywordList[idx]]

        # Update Word IDF record
        fp = open('wordIDF.json', 'w')
        fp.write(json.dumps(self.wordIDFDict, ensure_ascii=False, indent=4))

        return keywordIDFDict

    def getKeywordSetByTFIDF(self, filePath, topN=20):
        articleMeta = self.loadArticleMeta(filePath)
        article = articleMeta['title'] + '\n' + articleMeta['context']
        # TF-IDF
        # Get keyword list and TF for each word
        wordListDwarf = list(jieba.cut(article, cut_all=False))
        wordList = []   
        for idx in range(0, len(wordListDwarf)):
            if not wordListDwarf[idx] in self.stopWordDict:
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
        keywordIDFDict = self.__getIDFValue(keywordList)

        # Calculate TF-IDF value
        for idx in range(0, len(keywordList)):
            if wordList[idx] in keywordFreqDict:
                keywordFreqDict[keywordList[idx]] = keywordFreqDict[keywordList[idx]] / len(wordList)
                keywordTFIDFDict[keywordList[idx]] = keywordFreqDict[keywordList[idx]] * keywordIDFDict[keywordList[idx]]

        del(wordListDwarf)
        del(wordList)
        sortedTFIDFResult = sorted(keywordTFIDFDict.items(), key=lambda d: d[1], reverse=True)

        if topN > 0:
            return sortedTFIDFResult[0:topN]
        else:
            return sortedTFIDFResult


    def getKeywordSetByTextRank(self, filePath):
        articleMeta = self.loadArticleMeta(filePath)
        article = articleMeta['title'] + '\n' + articleMeta['context']
        print(article)
        # TextRank
        wordFromTextRank = jieba.analyse.textrank(article, withWeight=True, topK=40)
        return wordFromTextRank

    def getTagFromArticle(self, fileIdx):
        print('Start to get tag from article')

        # Get article meta data
        for listIdx in range(0, len(self.articleIndex)):
            if self.articleIndex[listIdx]['index'] == fileIdx:
                filePath = self.articleIndex[listIdx]['filePath']
                articleTitle = self.articleIndex[listIdx]['title']
                break;

        # Get TF-IDF for each word to be weight
        keywordWeightDict = {}

        # Get keyword weight by TextRank
        keywordFromTextRank = self.getKeywordSetByTextRank(filePath)

        # Get top 5 keyword to be article tag by weighted TextRank
        tagCandidate = {}
        for idx in range(0, len(keywordFromTextRank)):
            if articleTitle.find(keywordFromTextRank[idx][0]) != -1:
                keywordWeightDict[keywordFromTextRank[idx][0]] = keywordFromTextRank[idx][1] + 1.5
            else:
                keywordWeightDict[keywordFromTextRank[idx][0]] = keywordFromTextRank[idx][1] + 1


        keywordFromTfIDF = self.getKeywordSetByTFIDF(filePath, -1)
        # Word is more important if it appear at title.
        for idx in range(0, len(keywordFromTfIDF)):
            if keywordFromTfIDF[idx][0] in keywordWeightDict:
                tagCandidate[keywordFromTfIDF[idx][0]] = keywordFromTfIDF[idx][1] * keywordWeightDict[keywordFromTfIDF[idx][0]]
            else:
                tagCandidate[keywordFromTfIDF[idx][0]] = keywordFromTfIDF[idx][1]

        sortedTag = sorted(tagCandidate.items(), key=lambda d: d[1], reverse=True)

        return sortedTag[0:5]

# Main function
if __name__ == '__main__':
    articleAnalyzer = ArticleAnalyzer('data/Gossiping')
    print(articleAnalyzer.getTagFromArticle('Gossiping_M_1514098616_A_3DE'))
