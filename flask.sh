# Do the necessary installations for flask
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
sudo pip3 install flask
sudo apt-get install nginx
sudo apt-get install gunicorn3
mkdir flask_application
cd flask_application

# Make flask application
# TODO give each instance a unique ID and include this in the return statement!
at << EOF > flask_pythonscript.py
#!/usr/bin/python
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello, World!'

EOF

chmod 755 flask_pythonscript.py

./flask_pythonscript.py
