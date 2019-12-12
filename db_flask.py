import sqlite3
from flask import g, Flask, render_template, request, flash, redirect, url_for
import json

app = Flask(__name__)

# Intro page rendered and shows data description
@app.route('/', methods=['GET'])
def intro_link():

    return render_template('hello.html')


# This route is to return up to 1000 records of data
@app.route('/item', methods=['GET'])
def show_all():
    con = sqlite3.connect("phishing_db.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from phishing_dataset limit 1000")

    rows = cur.fetchall()
    return render_template('full_db.html', rows = rows)


# This route is to get one record back, specified by the id. It can also DELETE
@app.route('/item/<string:id>', methods=['GET'])
def show_single(id):
    con = sqlite3.connect("phishing_db.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute('select * from phishing_dataset where id = ?', [id])

    row_id = id
    rows = cur.fetchall()
    return render_template('single.html', rows=rows, row_id = row_id)


""" This block of code is used only for the jupyter notebook connection. 
    It needs to be returned in JSON format for the Jupyter notebook to
    grab the data via the API. This way of querying the database returns
    JSON in a way I can use. 
"""
#########################################################################
# This is the connection that is made to the local SQLite database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('phishing_db.db')
        db.row_factory = sqlite3.Row
    return db


# function to query the database
def query_db(query, args=(), one=False):
    data = []
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    columns = [column[0] for column in cur.description]
    cur.close()

    for row in rv:
        data.append(dict(zip(columns, row)))
    return json.dumps(data, indent=4, sort_keys=True, default=str)


# route for the jupyter notebook to grab the data
@app.route('/item/jupyter', methods=['GET'])
def jupyter():

    return query_db("select * from phishing_dataset")
#########################################################################


# This is the closing function. On teardown
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run()