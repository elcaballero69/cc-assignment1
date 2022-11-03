

import paramiko
import binascii
import time
import os
from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).parent

def waiter(ec2_client, ins_hadoop, ins_spark):
    instance_ids = [ins_hadoop[0], ins_spark[0]]
    instance_running_waiter = ec2_client.get_waiter('instance_running')
    instance_running_waiter.wait(InstanceIds=(instance_ids))

    ready = False
    accesKey = paramiko.RSAKey.from_private_key_file("C:/Users/meste/PycharmProjects/CloudComputing/cc-assignment1/Assignment_2/labsuser.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    while (ready == False):
        try:
            client.connect(hostname=ins_hadoop[1], username="ubuntu", pkey=accesKey)
            client.connect(hostname=ins_spark[1], username="ubuntu", pkey=accesKey)
        except:
            time.sleep(10)
        else:
            ready = True

    return True

def compareCode(ip):
    accesKey = paramiko.RSAKey.from_private_key_file("C:/Users/meste/PycharmProjects/CloudComputing/cc-assignment1/Assignment_2/labsuser.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=ip, username="ubuntu", pkey=accesKey)
    except:
        print("could not connect to client")
    try:
        stdin1, stdout1, stderr1 = client.exec_command('cat time_linux.txt')
        print("stderr.read():", stderr1.read())
        time_b = stdout1.read().decode('ascii').split("\n")
        print("stdout.read()", time_b[1])
        time_real = time_b[1].split("\t")
        print("real:", time_real[1])

        """stdin2, stdout2, stderr2 = client.exec_command("mv pg4300.txt input")
        print("stderr.read():", stderr2.read())"""
        """stdin, stdout, stderr = client.exec_command('source ~/.profile \n time hadoop jar /usr/local/hadoop-3.3.4/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount ~/input/pg4300.txt output')
        print("stderr.read():", stderr.read())
        print("stdout", stdout.read())"""
        client.close()
    except:
        print("error occured")



def main():
    ins_hadoop=[['i-0f91b5b69c7d7c668'], '3.228.16.17']
    path = str(get_project_root()).replace('\\', '/')
    print("path", path)
    #newPath = path.replace('\\', '/')
    print(path + "/labsuser.pem")
    #hadoopoutput = compareCode(ins_hadoop[1])
    print("Check the instance: \n", str(ins_hadoop[1]), "\n")


main()
