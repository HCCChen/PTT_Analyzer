# PTT_Analyzer

Text Analyzer for ptt article, it can statistic and text mining from the data set.
Data set is many JSON file which collect by PTT_Aritcal_Crawler.

### Run Environment
* Python 3
* jieba

### Method and Output result
#### timeStatistic.py: 
* getArticleTimeDistribution - Get the post time distribution for all data set
* getCommentTimeDistrbution - Get the comment time distribution for all data set
* getAuthorStatistic - Get the number that each auther post the aritcle.

#### articleAnalyzer.py: 
* getKeywordSetByTFIDF - Get keyword by TF-IDF method, default select the top 20 word
* getKeywordSetByTextRank - Get keyword by TextRank method, default select the top 20 word

### Demo
Result will update to below website, it will show by d3.js
https://paulchen.csie.io/
