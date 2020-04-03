"Plot a PNG using matplotlib in a web request, using Flask."

# Install dependencies, preferably in a virtualenv:
#
#     pip install flask matplotlib
#
# Run the development server:
#
#     python app.py
#
# Go to http://localhost:5000/plot.png and see a plot of random data.

import random
import io

from flask import Flask, make_response
from flask import request

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
from scipy.stats import t, sem
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

import base64

# Imports for Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

import time
import sys
# # # Imports the Google Cloud client library
# from google.cloud import storage

# # Instantiates a client
# storage_client = storage.Client()
#
# # The name for the new bucket
# bucket_name = "my-new-bucket"
#
# # Creates the new bucket
# bucket = storage_client.create_bucket(bucket_name)
#
# print("Bucket {} created.".format(bucket.name))

# '''
# Firebase storage
# '''
# cred = credentials.Certificate(r'C:\Users\chris\Desktop\CS4471\SOA\cs4471-group5-firebase-adminsdk-cbxeo-921f4626c0.json')
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'gs://cs4471-group5.appspot.com'
# })
#
# bucket = storage.bucket()

# 'bucket' is an object defined in the google-cloud-storage Python library.
# See https://googlecloudplatform.github.io/google-cloud-python/latest/storage/buckets.html
# for more details.
'''
Firebase Setup
'''
cred = credentials.Certificate(r'C:\Users\chris\Desktop\CS4471\SOA\cs4471-group5-firebase-adminsdk-cbxeo-921f4626c0.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)


@app.route('/plot.png', methods = ['GET', 'POST'])
def plot():
    start_time = time.time()
    ticker = ''
    uid = ''
    start_look = ''
    end_look = ''

    if request.method == 'POST':
        data = request.form # a multidict containing POST data
        ticker = request.args.get('ticker') #if key doesn't exist, returns None
        print('PRINT TICKER: ', ticker)
        uid = request.args.get('uid') #if key doesn't exist, returns None
        start_look = request.args.get('start') #if key doesn't exist, returns None
        end_look = request.args.get('end') #if key doesn't exist, returns None

        fig = Figure()
        plt = fig.add_subplot(1, 1, 1)
        fig.suptitle(str(ticker))

        msft = yf.Ticker(ticker)
        DNE_ticker = yf.Ticker('YHOO')
        print(start_look)
        history = msft.history(start = start_look, end = end_look)
        DNE_history = DNE_ticker.history(perdio = 'max')
        close = history['Close']
        DNE_close = DNE_history['Close']
        print(close.shape)
        print(DNE_close.shape)
        if close.equals(DNE_close):
            sys.exit()
        # plt.subplots(dpi = 100)
        img = plt.plot(history.index, close)
        # plt.title('hi')

        # xs = range(100)
        # ys = [random.randint(1, 50) for x in xs]

        fig.savefig('plot.png')

        encoded = base64.b64encode(open("plot.png", "rb").read())
        # plt.plot(xs, ys)
        canvas = FigureCanvas(fig)
        output = io.BytesIO()
        canvas.print_png(output)
        response = make_response(output.getvalue())
        response.mimetype = 'image/png'

        import os
        # stream = os.popen('echo Returned output')
        stream = os.popen('node app.js' + ' ' + ticker)
        output = stream.read()
        print(output)
        output

        # Write to Firebase
        doc_ref = db.collection(u'lookup').document(uid)
        doc_ref.set({
            u'img_url': output,
            u'ticker': ticker,
            u'uid': uid,
        })

        end_time = time.time()
        print(end_time - start_time)

        # # Imports the Google Cloud client library
        # from google.cloud import storage
        # # # Instantiates a client
        # # storage_client = storage.Client()
        # #
        # # # The name for the new bucket
        # # bucket_name = "my-new-bucket"
        # #
        # # # Creates the new bucket
        # # bucket = storage_client.create_bucket(bucket_name)
        # #
        # # print("Bucket {} created.".format(bucket.name))
        # def upload_blob(bucket_name, source_file_name, destination_blob_name):
        #     # """Uploads a file to the bucket."""
        #     # bucket_name = "your-bucket-name"
        #     # source_file_name = "local/path/to/file"
        #     # destination_blob_name = "storage-object-name"
        #
        #     storage_client = storage.Client()
        #     bucket = storage_client.bucket(bucket_name)
        #     blob = bucket.blob(destination_blob_name)
        #
        #     blob.upload_from_filename(source_file_name)
        #
        #     print(
        #         "File {} uploaded to {}.".format(
        #             source_file_name, destination_blob_name
        #         )
        #     )
        #
        # upload_blob(bucket, r"C:\Users\chris\Desktop\CS4471\SOA\plot.png", r"plot.png")

        return encoded



if __name__ == '__main__':
    app.run(debug=True)


# # -*- coding: utf-8 -*-
# """MSFT_20yrs.ipynb
#
# Automatically generated by Colaboratory.
#
# Original file is located at
#     https://colab.research.google.com/drive/12Mgld2wHfq4eALG9KxkY0T7tQ8pl3NPr
# """
#
#
#
# msft = yf.Ticker("FB")
# print(msft)
# history = msft.history(start = '2010-01-01', end = '2020-02-18')
# close = history['Close']
# plt.subplots(dpi = 100)
# plt.plot(history.index, close)
#
# plt.savefig('FB.png')
