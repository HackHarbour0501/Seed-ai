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

def insert_data_from_excel():
    try:
        df = pd.read_excel("C:\\Users\\hp\\Documents\\python\\output.xlsx")  # Replace with your actual Excel file path
        for column in df.select_dtypes(include=['datetime64[ns]']):
            df[column] = df[column].astype(str)
        data_dict = df.to_dict(orient='records')
        collection.insert_many(data_dict)
        print("Data inserted successfully into MongoDB!")
    except Exception as e:
        print(f"Error inserting data: {e}")

def upload_images_to_cloudinary_and_update_mongo(folder_path):
# Folder containing images to upload
    folder_path = f"D:\Python\Flask-tut\static\images"

# List to store image URLs
    image_urls = []

# Loop through files in the folder and upload to Cloudinary
    for filename in os.listdir(folder_path):
        if filename.endswith((".jpg", ".png")):
            file_path = os.path.join(folder_path, filename)
        
        try:
            # Upload to Cloudinary
            response = cloudinary.uploader.upload(file_path)
            image_url = response.get('url')
            
            if image_url:
                # Append image URL to the list
                image_urls.append(image_url)
                # print(f"Processed {filename}: {image_url}")
            else:
                print(f"Failed to upload {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

# Load the existing Excel file
    excel_path = r"C:\Users\hp\Documents\python\output.xlsx"
    sheet_name = "Sheet"  # Use your sheet name

    try:
    # Read the existing Excel file into a DataFrame
        df_existing = pd.read_excel(excel_path, sheet_name=sheet_name, engine='openpyxl')

    # Check if the number of uploaded images matches the rows needing URLs
        if len(image_urls) != len(df_existing):
            print(f"Warning: Number of images ({len(image_urls)}) does not match the rows in Excel ({len(df_existing)}).")

    # Update the 'image_url' column in the DataFrame with the uploaded URLs in order
        df_existing['image_url'] = image_urls[:len(df_existing)]  # Ensure not to exceed row count

    # Save the updated DataFrame back to the Excel file
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_existing.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"Image URLs updated in {excel_path}")

    except Exception as e:
        print(f"Error updating Excel file: {str(e)}")



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
    # insert_data_from_excel()
    # upload_images_to_cloudinary_and_update_mongo('')
    app.run(debug=True)