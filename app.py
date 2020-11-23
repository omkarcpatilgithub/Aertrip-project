import numpy as np
from flask import Flask, request, jsonify, render_template
import test_single_sent
from named_entity_recognition import Parser
import dateparser

from named_entity_recognition import Parser
import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''

    sent = [str(x) for x in request.form.values()][0]

    dict = test_single_sent.pred(sent)
    response = jsonify(dict)
    # response = "intent: Return search \n\nnext line"


    return response



if __name__ == "__main__":
    app.run(port=5000,debug=True,threaded=False)