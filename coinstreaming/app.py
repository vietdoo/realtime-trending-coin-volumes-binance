import ast
from collections import OrderedDict

from flask import Flask, jsonify, request
from flask import render_template

from config import *
import time

app = Flask(__name__)

dataValues = []
categoryValues = []

tags = {}

def get_top_players(data, n = 20):
    top = sorted(data.items(), key = lambda x: x[1], reverse = True)[:n]
    return OrderedDict(top)


@app.route("/")
def home():
    return render_template('index.html', dataValues = dataValues, categoryValues = categoryValues)


@app.route("/clearData")
def clearData():
    global tags, dataValues, categoryValues
    tags = {}
    dataValues = []
    categoryValues = []

    return 'ok'

@app.route('/refreshData')
def refresh_data():
    global dataValues, categoryValues
    return jsonify(dataValues = dataValues, categoryValues = categoryValues)


@app.route('/updateData', methods=['POST'])
def update_data():


    global tags, dataValues, categoryValues
    data = ast.literal_eval(request.data.decode("utf-8"))

    tags[data['name']] = data['total_volume']
    sorted_tags = get_top_players(tags)

    categoryValues.clear()
    dataValues.clear()
    categoryValues = [x for x in sorted_tags]
    dataValues = [int(tags[x]) for x in sorted_tags]
   # print(dataValues, categoryValues)
    return "success", 201




if __name__ == "__main__":
    app.run(host = '0.0.0.0', debug = True, port = FLASK_PORT)