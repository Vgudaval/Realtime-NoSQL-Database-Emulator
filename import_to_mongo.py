import json
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['airbnb']
collection = db['listings']

  # Load JSON data
with open('AB_NYC_2019.json', 'r') as json_file:
    data = json.load(json_file)

  # Insert JSON data into MongoDB
collection.insert_many(data)

  # Close MongoDB connection
client.close()
