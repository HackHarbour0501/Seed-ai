from flask import Flask, render_template, request, jsonify
import os
from pymongo import MongoClient
import pandas as pd
import cloudinary
import cloudinary.api
import cloudinary.uploader
from flask import request
from pymongo import MongoClient
from datetime import datetime


# Configuration and Initialization
app = Flask(__name__)
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://user:BkrCNdfdQBiEXgl8@seed.6sftq.mongodb.net/')


cloudinary.config(
    cloud_name="dortbrd2t",
    api_key="568456243884785",
    api_secret="c7YeNGnxDGaTs-1gGpzy0p6PMFg",
    secure=True,
)

client = MongoClient("mongodb+srv://user:BkrCNdfdQBiEXgl8@seed.6sftq.mongodb.net/BkrCNdfdQBiEXgl8")
db = client['Excel']
collection = db['Sample']

# Route Definitions
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/index.html")
def dashboard():
    return render_template('index.html')

@app.route("/images.html")
def images():
    images_folder = os.path.join(app.static_folder, 'images')
    images = [img for img in os.listdir(images_folder) if img.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template('images.html', images=images)


@app.route("/tables-data.html", methods=['GET'])
def tables():
    # Get filter inputs
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    seed_type = request.args.get('seed_type')
    print("Start Date:", start_date)
    print("End Date:", end_date)
    print("Seed Type:", seed_type)
    query = {}

    # Check if filter is applied
    if start_date and end_date:
        query["Start Date"] = {"$gte": start_date, "$lte": end_date}

    if seed_type:
        query["Seed Type"] = seed_type

    # Fetch the filtered or unfiltered data based on the query
    data = list(collection.find(query,{"_id": False}))

    # Render the same template for both filtered and unfiltered views
    return render_template('tables-data.html',data=data)

@app.route('/data', methods=['GET'])
def get_data():
    data = list(collection.find({}, {"_id": False}))
    return jsonify(data)



if __name__ == "__main__":
    insert_data_from_excel()
    upload_images_to_cloudinary_and_update_mongo('')
    app.run(debug=True)
