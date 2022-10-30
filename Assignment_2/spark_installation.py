userdata="""
sudo apt-get update
sudo apt install default-jdk scala git -y
sudo wget https://archive.apache.org/dist/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz
sudo tar xvf spark-*
sudo mv spark-3.0.1-bin-hadoop2.7 /opt/spark
cd ..
cd ..
cat << EOF >> .profile
export SPARK_HOME=/opt/spark
export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3
EOF
source ~/.profile

sudo apt install python3-pip | ENTER
pip install urllib3
pip install pandas
"""

# second export must be entered manually

# use for installing of Spark 2.0.0 but not working due to Python failures
#sudo wget https://archive.apache.org/dist/spark/spark-2.0.0/spark-2.0.0-bin-hadoop2.3.tgz


#echo "export SPARK_HOME=/opt/spark" >> ~/.profile
#echo "export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin" >> ~/.profile
#echo "export PYSPARK_PYTHON=/usr/bin/python3" >> ~/.profile

# Can be used for the wordcountproblem
'''
import urllib3
import pandas as pd
http = urllib3.PoolManager()

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

result = pd.DataFrame()

for link in LINKS:
    r = http.request('GET', link)
    content = r.data.decode('latin-1')
    content = content.replace('\n',' ')
    rdd = sc.parallelize(content.split(' '))
    rdd = rdd.map(lambda x: (x,1))
    rdd = rdd.reduceByKey(lambda x,y: x + y).sortByKey()
    df = rdd.toDF(['Word', f'Count_Link{str(LINKS.index(link))}']).toPandas().sort_values(f'Count_Link{str(LINKS.index(link))}', axis=0, ascending = False).set_index('Word')
    result = pd.concat([result, df], axis=1)
'''