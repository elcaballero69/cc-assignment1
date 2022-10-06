chmod 600 labsuser.pem
ssh -o "StrictHostKeyChecking no" $1
ssh -i labsuser.pem ubuntu@$1 << REALEND
# Always update first
sudo apt-get update
# Install venv, used to create virtual environment
yes | sudo apt-get install python3-venv
mkdir flask_app && cd flask_app
# Activating venv, now entering venv 'virtual environment'
python3 -m venv venv
source venv/bin/activate
# Install flask
pip install flask
# Write a small python script
cat <<EOF >flask_app.py
from flask import Flask
app = Flask(__name__)
@app.route('/')
def flask_app():
    return 'Hello, World from ' + str($2)
# This is needed to run on port 80, else flask will run on 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
EOF
# Authbind
sudo apt install authbind
sudo touch /etc/authbind/byport/80
sudo chmod 777 /etc/authbind/byport/80
# Now deploy the flask application
# authbind -deep flask --app flask_app run --host 0.0.0.0 --port 80 &
authbind --deep python3 flask_app.py

REALEND