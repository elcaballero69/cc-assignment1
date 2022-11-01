#hadoop installation script and wordcount execution for the example file

userdata="""#!/bin/bash
cd /home/ubuntu
sudo apt-get update
yes | sudo apt install openjdk-11-jdk-headless
sudo apt-get install wget
wget https://dlcdn.apache.org/hadoop/common/stable/hadoop-3.3.4.tar.gz
sudo tar -xf hadoop-3.3.4.tar.gz -C /usr/local/
cat << EOF >> .profile
#!/bin/sh
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=\$JAVA_HOME/bin:\$PATH
#!/bin/sh
export HADOOP_PREFIX=/usr/local/hadoop-3.3.4
export PATH=\$HADOOP_PREFIX/bin:\$PATH
EOF
sudo chmod ugo+rw /usr/local/hadoop-3.3.4/etc/hadoop/hadoop-env.sh
cat << EOF >> /usr/local/hadoop-3.3.4/etc/hadoop/hadoop-env.sh
# export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
# export HADOOP_PREFIX=/usr/local/hadoop-3.3.4
EOF
source ~/.profile
wget -d --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36" https://www.gutenberg.org/cache/epub/4300/pg4300.txt.utf8.gzip
cp pg4300.txt.utf8.gzip pg4300.txt.gz
gunzip -kv pg4300.txt.gz
{ time cat pg4300.txt | tr ' ' '\n' | sort | uniq -c  ; } 2> time_linux.txt
hdfs dfs -mkdir input
hdfs dfs -copyFromLocal pg4300.txt input
{ time hadoop jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/input/pg4300.txt output 2> hadoop.stderr  ; } 2> time_hadoop.txt
"""