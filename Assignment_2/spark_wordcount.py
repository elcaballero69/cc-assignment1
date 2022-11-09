# run this script on the remote machine's pyspark
import urllib3
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

execution_time = []
for i in range(1,4):
    start = time.time()
    for content in data_files:
        rdd = sc.parallelize(content.split(' ')) # form RDD
        rdd = rdd.map(lambda x: (x,1))  # map each word to a key
        rdd = rdd.reduceByKey(lambda x,y: x + y).sortByKey() #  merge the values of each key
    end = time.time()
    running_time = end - start
    execution_time.append(running_time)

with open('spark_execution_time.txt', 'w') as file:
    for iteration in execution_time:
        file.write(str(iteration))
        file.write('\n')

for timer in execution_time:
    print('WORDCOUNT TAKES ' + str(timer) + 'S FOR SPARK')