import boto3
import botocore
import paramiko




if __name__ == '__main__':
    IP_ADRESS = '3.91.20.60'
    KEY = paramiko.RSAKey.from_private_key_file('mykey.pem')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect/ssh to an instance
    # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
    client.connect(hostname= IP_ADRESS, username='ubuntu', pkey=KEY)

    # Easy exemplary calculation
    stdin, stdout, stderr = client.exec_command('echo "var=10;++var" | bc')
    print('stdout:', stdout.read())
    print('stderr:', stderr.read())

    # close the client connection once the job is done
    client.close()
    print('TRY')

    #except Exception:
     #   print('EXCEPTION')



