#!/bin/bash
sudo apt install openjdk-11-jre-headless
cp /etc/skel/.profile ~/.profile
cat >> ~/.profile <<EOF
export JAVA_HOME=/usr/lib/jvm/java-7-oracle
export PATH=$JAVA_HOME/bin
EOF
source ~/.profile
sudo apt-get install wget
wget https://dlcdn.apache.org/hadoop/common/stable/hadoop-3.3.4.tar.gz
sudo tar -xf hadoop-3.3.4.tar.gz -C /usr/local/ 
cat >> ~/.profile <<EOF
export HADOOP_PREFIX=/usr/local/hadoop-3.3.4
export PATH=$HADOOP_PREFIX/bin:$PATH
EOF
source ~/.profile
cat >> ~/etc/hadoop/hadoop-env.sh <<EOF
export JAVA_HOME=/usr/lib/jvm/java-7-oracle$ export HADOOP_PREFIX=/usr/local/hadoop-3.3.4
EOF
source ~/.profile