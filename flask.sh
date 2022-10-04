# Do the necessary installations for flask
sudo apt-get update
# Install python, pip, flask, nginx and gunicorn3
sudo apt-get install python3
sudo apt-get install python3 -V
sudo apt-get install python3-venv
mkdir flash_app && cd flask_app
python3 -m venv venv
source venv/bin/activate
pip install flask
vi flask_app.py



# Make flask application - it is opened automatically
# TODO give each instance a unique ID and include this in the return statement!
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello, World!'
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

# To execute above code 
# export flask_app=flask_app.py
# flask run
python3 flask_app.py

change the security group to Custom TCP and port rangr 8080 and source 0.0.0.0/0

