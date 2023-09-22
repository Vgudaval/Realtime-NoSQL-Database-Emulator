from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import json_util
import json
import uuid

from pymongo import ASCENDING, DESCENDING

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["airbnb"]
collection = db["listings"]

@app.route('/listings.json', methods=['GET'])
@app.route('/listings/<listing_id>.json', methods=['GET'])

def get_listings(listing_id=None):
    if listing_id:
        # Convert the listing_id to an integer if possible
        try:
            listing_id = int(listing_id)
        except ValueError:
            pass

        listing = collection.find_one({"id": listing_id})
        if listing:
            return json.dumps(json.loads(json_util.dumps(listing)), indent=2)
        else:
            return jsonify({"error": "Listing not found."}), 404

    query_params = request.args
    query = {}
    sort_by = query_params.get("orderBy", "order_id")
    sort_order = DESCENDING if query_params.get("limitToLast") else ASCENDING
    limit = int(query_params.get("limitToFirst", query_params.get("limitToLast", 0)))
    start_at = query_params.get("startAt")
    end_at = query_params.get("endAt")
    equal_to = query_params.get("equalTo")

    if sort_by:
        query["sort"] = [(sort_by, sort_order)]

    if limit:
        query["limit"] = int(limit)

    if start_at:
        query["startAt"] = {sort_by: {'$gte': int(start_at)}}

    if end_at:
        query["endAt"] = {sort_by: {'$lte': int(end_at)}}

    if equal_to:
        query["equalTo"] = {sort_by: {'$eq': int(equal_to)}}

    query_filters = {}
    if query.get("startAt"):
        query_filters.update(query["startAt"])
        query.pop("startAt", None)
    if query.get("endAt"):
        query_filters.update(query["endAt"])
        query.pop("endAt", None)
    if query.get("equalTo"):
        query_filters.update(query["equalTo"])
        query.pop("equalTo", None)

    print("qf", query_filters)
    print("q", query)

    orders = collection.find(query_filters, **query)
    return json.dumps([json.loads(json_util.dumps(order)) for order in orders], indent=2)




@app.route('/listings.json', methods=['PUT'])
def put_listing():
    # Retrieve the data from the request
    data = request.get_json()
    listing_id = data.get("id")

    # Check if the listing_id exists
    if not listing_id:
        return jsonify({"error": "ID is required"}), 400

    # Try to convert the listing_id to an integer if possible
    try:
        listing_id = listing_id
    except ValueError:
        pass

    # Replace the existing object or insert a new one if it doesn't exist
    collection.replace_one({"id": listing_id}, data, upsert=True)

    return jsonify(data)



@app.route('/listings.json', methods=['POST'])
def post_listing():
    try:
        # Retrieve the data from the request
        data = request.get_json()

        # Generate a unique listing ID using UUID
        new_listing_id = str(uuid.uuid4())
        data["id"] = new_listing_id

        # Insert the new listing into MongoDB
        collection.insert_one(data)

        return jsonify({'message': 'Listing created successfully.', 'listing_id': new_listing_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/listings/<string:listing_id>.json', methods=['PATCH'])
def patch_listing(listing_id):
    try:
        # Try to convert the listing_id to an integer if possible
        try:
            listing_id = int(listing_id)
        except ValueError:
            pass

        # Retrieve the update data from the request
        update_data = request.get_json()

        # Update the listing in MongoDB using the given ID and update data
        response = collection.update_one({'id': listing_id}, {'$set': update_data})

        # Check if the update was successful
        if response.modified_count > 0:
            return jsonify({"result": "Listing updated successfully."}), 200
        else:
            return jsonify({"result": "Listing not found or no changes made."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/listings/<string:listing_id>.json', methods=['DELETE'])
def delete_listing(listing_id):
    try:
        # Try to convert the listing_id to an integer
        try:
            listing_id = int(listing_id)
        except ValueError:
            pass

        # Remove the listing in MongoDB using the given ID
        response = collection.delete_one({'id': listing_id})

        # Check if the delete operation was successful
        if response.deleted_count > 0:
            return jsonify({"result": "Listing deleted successfully."}), 200
        else:
            return jsonify({"result": "Listing not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500





if __name__ == '__main__':

    app.run(debug=True, port=5000)



