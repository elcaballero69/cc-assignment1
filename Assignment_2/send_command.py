

import paramiko
import binascii
import time
import os
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

def get_project_root() -> Path:
    return Path(__file__).parent



def compareCode():
    accesKey = paramiko.RSAKey.from_private_key_file("C:/Users/meste/PycharmProjects/CloudComputing/cc-assignment1/Assignment_2/labsuser.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname='3.235.230.126', username="ubuntu", pkey=accesKey)
    except:
        print("could not connect to client")
    try:
        stdin, stdout, stderr = client.exec_command("cat spark_execution_time.txt")
        # the read() function reads the output in bit form
        print("stderr.read():", stderr.read())
        # converts the bit string to str
        output = stdout.read().decode('ascii').split("\n")
        print("output", output)
        client.close()
        return output
    except:
        print("error occured in sending command")




def main():

    path = str(get_project_root()).replace('\\', '/')
    print("path", path)
    print(path + "/labsuser.pem")
    res = compareCode()

    print("res", res)
    execution_time = []
    for x in res:
        if (x != ''):
            time1 = x.replace('.', ':').replace('S', '')
            execution_time.append(datetime.strptime(time1[:8], '%S:%f'))

    print("execution time", execution_time)

    """ time_str = ['0m6.953s', '0m5.859s', '0m5.973s']
    hadoop_wordcount_time = []
    for x in time_str:
        t = x.split('m')
        time1= t[1].replace('s', '').replace('.', ':')
        #time2=time1.replace('s', '')
        #time3 = time2.replace('.', ':')
        print(time1)
        time = datetime.strptime(time1, '%S:%f')
        print(time)
        hadoop_wordcount_time.append(time)"""


    """   #spark time
        res = ['7.679384902394850S', '5.679384908904850S', '5.679864902394850S']
        print("res", res)
        execution_time = []
        for x in res:
            time1 = x.replace('.', ':').replace('S', '')
            print("time1", time1)
            execution_time.append(datetime.strptime(time1[:8], '%S:%f'))
    
        print("execution time", execution_time)"""


    """ x = [1,2,3]
        plt.plot(x, hadoop_wordcount_time, 'bo--', label="Hadoop")
        plt.plot(x, execution_time, 'ro--', label="Spark")
        plt.title("Hadoop Wordcount Execution Time")
        plt.legend(loc="upper right")
        plt.ylabel("Execution Time")
        plt.xlabel("Iteration")
        plt.show()"""

main()
