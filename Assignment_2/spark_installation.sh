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
sudo apt install python3-pip
y | echo -ne '\n' | mycommand
pip install urllib3
pip install pandas
pip install xlsxwriter