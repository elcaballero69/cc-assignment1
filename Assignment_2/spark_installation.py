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
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3
EOF
source ~/.profile

sudo apt install python3-pip
pip install jupyter
sudo apt install firefox

"""

# second export must be entered manually

# use for installing of Spark 2.0.0 but not working due to Python failures
#sudo wget https://archive.apache.org/dist/spark/spark-2.0.0/spark-2.0.0-bin-hadoop2.3.tgz


#echo "export SPARK_HOME=/opt/spark" >> ~/.profile
#echo "export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin" >> ~/.profile
#echo "export PYSPARK_PYTHON=/usr/bin/python3" >> ~/.profile

# Can be used for the wordcountproblem
'''
content = "How happy I am that I am gone"
rdd = sc.parallelize(content.split(' '))\
    .map(lambda x: (x, 1))\
    .reduceByKey(lambda x,y: x + y)
rdd.toDF(['word','count'])\
    .orderBy('count')\
    .show()
'''