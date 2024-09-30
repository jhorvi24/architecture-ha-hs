from flask import Flask, render_template

import boto3

app = Flask(__name__)



@app.route('/')
def home():
	return render_template("index.html")

@app.route('/about_us')
def about_us():
    return render_template("about.html")

@app.route('/gallery')
def gallery():
    return render_template("gallery.html")

@app.route('/services')
def services():
    return render_template("services.html")

if __name__=='__main__':
	app.run(host='0.0.0.0')
