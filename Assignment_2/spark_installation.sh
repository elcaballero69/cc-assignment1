#!/bin/bash
sudo apt-get update
sudo apt install default-jdk scala git -y
sudo apt-get install wget
sudo wget https://archive.apache.org/dist/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz
sudo tar xvf spark-*
sudo mv spark-3.0.1-bin-hadoop2.7 /opt/spark
sudo cat << EOF >> .profile
export SPARK_HOME=/opt/spark
export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3
EOF
source ~/.profile
yes | sudo apt install python3-pip
pip install urllib3
pip install xlsxwriter
pip install pyspark

y | echo -ne '\n' | mycommand

source ~/.profile \n
pyspark \n
print("hello world")