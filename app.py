from flask import Flask, render_template
import mysql.connector
import boto3

app = Flask(__name__)
ssm_client = boto3.client('ssm', region_name='us-east-1')

host='/book/host'
user='/book/user'
password='/book/password'
database='/book/database'

response = ssm_client.get_parameters(
        Names=[host, user, password, database],
        WithDecryption=True
)

rds_database = response['Parameters'][0]['Value']
rds_host = response['Parameters'][1]['Value']
rds_password = response['Parameters'][2]['Value']
rds_user = response['Parameters'][3]['Value']


@app.route('/')
def home():
	return render_template("index.html")

@app.route('/books')
def books():
    conn = mysql.connector.connect(
        host=rds_host,
        user=rds_user,
        password=rds_password,
        database=rds_database)
    
    c = conn.cursor()
    c.execute("SELECT * FROM Books")
    books = c.fetchall()
    conn.close()
    return render_template("books.html", books=books)

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
