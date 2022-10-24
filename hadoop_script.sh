sudo apt install openjdk-11-jre-headless
gedit <<EOF >~/.profile
export JAVA_HOME=/usr/lib/jvm/java-7-oracle
export PATH=$JAVA_HOME/bin
EOF
source ~/.profile