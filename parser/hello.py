import json
#from bson.json_util import dumps
#from bson import json_util
from flask import Flask 
from flask import request
from flask import jsonify
from flask_cors import CORS
import base64
import requests
import os
import sys
#import pymysql
#from sqlalchemy import create_engine
import pandas as pd
app = Flask(__name__)
CORS(app)
sys.path.insert(0,"/home/shivank/parser/parser_class")
import main
@app.route("/",methods=['GET'])
def hello():
    return jsonify("Hello World")


###################################parser resume #################################
@app.route("/careerletics/parser/resume",methods=['POST'])
def parserresume():
     file = request.files['resume']
     filename = request.files['resume'].filename
     UPLOAD_FOLDER = '/home/shivank/parser/parsed_resume'
     file.save(os.path.join(UPLOAD_FOLDER, filename))
     filepath='/home/shivank/parser/parsed_resume/'+filename
     print (filepath)
     return main.final_output_json(filepath)
     #try:
     #  file = request.files['resume']
     #  filename = request.files['resume'].filename
     #  UPLOAD_FOLDER = '/home/shivank/parser/parsed_resume'
     #  file.save(os.path.join(UPLOAD_FOLDER, filename))
     #  filepath='/home/shivank/parser/parsed_resume/'+filename
     #  return jsonify(main.final_output_json(filepath))
     #except:
     # return "No resume parsed."



if __name__ == "__main__":
   app.debug = True 
   app.run()


