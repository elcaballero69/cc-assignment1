# run this script on the remote machine's pyspark
import urllib3
import pandas as p
import time
http = urllib3.PoolManager()

# texts to analyze
LINKS = ['http://www.gutenberg.ca/ebooks/buchanj-midwinter/buchanj-midwinter-00-t.txt',
         'http://www.gutenberg.ca/ebooks/carman-farhorizons/carman-farhorizons-00-t.txt',
         'http://www.gutenberg.ca/ebooks/colby-champlain/colby-champlain-00-t.txt',
         'http://www.gutenberg.ca/ebooks/cheyneyp-darkbahama/cheyneyp-darkbahama-00-t.txt',
         'http://www.gutenberg.ca/ebooks/delamare-bumps/delamare-bumps-00-t.txt',
         'http://www.gutenberg.ca/ebooks/charlesworth-scene/charlesworth-scene-00-t.txt',
         'http://www.gutenberg.ca/ebooks/delamare-lucy/delamare-lucy-00-t.txt',
         'http://www.gutenberg.ca/ebooks/delamare-myfanwy/delamare-myfanwy-00-t.txt',
         'http://www.gutenberg.ca/ebooks/delamare-penny/delamare-penny-00-t.txt'
         ]

data_files= []
for link in LINKS:
    r = http.request('GET', link)
    content = r.data.decode('latin-1')  # decode the text from bin to string
    content = content.replace('\n', ' ')  # replace all paragraphs
    data_files.append(content)

executionTime = []

for i in range(0,3):
    start = time.time()
    for content in data_files:
        rdd = sc.parallelize(content.split(' ')) # form RDD
        rdd = rdd.map(lambda x: (x,1))  # map each word to a key
        rdd = rdd.reduceByKey(lambda x,y: x + y).sortByKey() #  merge the values of each key
        """df = rdd.toDF(['Word', f'Count_Link{str(data_files.index(content))}']).toPandas().sort_values(f'Count_Link{str(data_files.index(content))}', axis=0, ascending = False).set_index('Word')
        print(df)"""

    end = time.time()
    time = end - start
    executionTime.append(time)

for time in executionTime:
    print('WORDCOUNT TAKES ' + str(time) + 'S FOR SPARK')