from pymongo import MongoClient, ASCENDING
# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['airbnb']
collection = db['listings']

# Create indexes on the selected fields
collection.create_index('name')
collection.create_index('price')
collection.create_index('number_of_reviews')


# Close the MongoDB connection
client.close()
