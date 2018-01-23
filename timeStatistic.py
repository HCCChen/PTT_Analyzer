# -*- coding: utf-8 -*-                                                                                                                                                                                  

import os
import re
import requests
import time
import datetime
import sys
import json
import argparse


class TimeStatistic:
    def __init__(self, rootPath):
        self.rootPath = rootPath
        # load index file
        indexFilePath = self.rootPath + "/index.json"
        with open(indexFilePath, "r") as fp:
            self.articleIndex = json.load(fp)

    def loadArticleMeta(self, filePath):
        with open(filePath, "r") as fp:
            articleMeta = json.load(fp)
        return articleMeta

    # Get the statistic info about author
    # Return: article counter for each author
    def getAuthorStatistic(self, year, month, day):
        authorCount = {}
        for idx in range(0, len(self.articleIndex)):
            if self.articleIndex[idx]['author'] in authorCount:
                authorCount[self.articleIndex[idx]['author']] += 1
            else:
                authorCount[self.articleIndex[idx]['author']] = 1

        return authorCount

    # Get time distribution for all article
    # Return: article count for each time slot (a hour)
    def getArticleTimeDistribution(self):
        articleTimeCount = [0] * 24
        for idx in range(0, len(self.articleIndex)):
            # Add timestmap for GMT+8
            dayTimeStamp = (self.articleIndex[idx]['timeStamp'] + 28800) % 86400
            timeSlot = (int) (dayTimeStamp / 3600)
            articleTimeCount[timeSlot] += 1
        return articleTimeCount

    # Get time distrubution for each comment
    # Return: comment count for each time slot (a half hour)
    def getCommentTimeDistrbution(self):
        # one slot is a half hour, record to 7 days, last one is more than 7 days
        commentTimeCount = [0] * 337
        # Error count - Record negative value
        errorNegativeTimeStamp = 0
        for listIdx in range(0, len(self.articleIndex)):
            articleMeta = self.loadArticleMeta(self.articleIndex[listIdx]['filePath'])
            postTimeStamp = articleMeta['timeStamp']
            for idx in range(0, len(articleMeta['pushMetaData'])):
                diffTime = articleMeta['pushMetaData'][idx]['timeStamp'] - postTimeStamp
                timeSlot = (int)(diffTime/1800)
                if timeSlot > 336:
                    timeSlot = 336
                elif timeSlot < 0:
                    timeSlot = 336
                    errorNegativeTimeStamp += 1
                commentTimeCount[timeSlot] += 1
        print('getCommentTimeDistrbution done, error time stamp is ', errorNegativeTimeStamp)
        return commentTimeCount

# Main function
if __name__ == '__main__':
    timeStatistic = TimeStatistic('data/Gossiping')
    ## Example for loadArticleMeta ##
    #print(json.dumps(timeStatistic.loadArticleMeta('data/Gossiping/2018_01_18/Gossiping_M_1516263600_A_FC3.json'), indent=4, sort_keys=True, ensure_ascii=False))

    ## Example for getAuthorStatistic ##
    #authorCount_20180118 = timeStatistic.getAuthorStatistic(2018,1,18)
    #authorCount_20180118_sorted = sorted(authorCount_20180118.items(), key=lambda x: x[1])
    #print(authorCount_20180118_sorted)

    ## Example for getArticleTimeDistribution ##
    #articleTimeDistribution = timeStatistic.getArticleTimeDistribution()
    #fp = open('ArticleTimeDistribution.json', 'w')
    #fp.write(json.dumps(articleTimeDistribution, ensure_ascii=False))

    print(timeStatistic.getCommentTimeDistrbution())
