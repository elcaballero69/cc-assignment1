#hadoop installation script

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
source .profile
"""