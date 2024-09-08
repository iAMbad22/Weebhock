from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import logging

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

# Connect to MongoDB Atlas
client = MongoClient('mongodb+srv://DushyantKore:Tangate%4022@cluster0.cfumeal.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['github_webhooks']
collection = db['events']

# Enable logging to track the data
logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logging.info(f"Received data: {data}")  # Log the incoming JSON data
    
    # Print the received data for debugging purposes
    print(f"Received data: {data}")

    # Process the event based on its type
    event_type = request.headers.get('X-GitHub-Event')
    
    if event_type == 'push':
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = datetime.utcnow()
        
        # Insert into MongoDB
        collection.insert_one({
            'event_type': 'push',
            'author': author,
            'to_branch': to_branch,
            'timestamp': timestamp
        })
        
    elif event_type == 'pull_request':
        action = data['action']  # Check the action type within the pull_request event
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.utcnow()

        # Handle standard pull request submission
        if action == 'opened':
            # Insert into MongoDB for a new pull request
            collection.insert_one({
                'event_type': 'pull_request',
                'author': author,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': timestamp
            })

        # Handle merge event when a pull request is merged
        elif action == 'closed':
            # Insert into MongoDB for a merged pull request
            collection.insert_one({
                'event_type': 'merge',
                'author': author,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': timestamp
            })
            print(f"Merged event detected: {author} merged branch {from_branch} to {to_branch} on {timestamp}")
    
    # Return a success response
    return jsonify({'message': 'Webhook received successfully'}), 200


@app.route('/events', methods=['GET'])
def get_events():
    try:
        events = list(collection.find())  # Fetch all documents from MongoDB
        for event in events:
            event['_id'] = str(event['_id'])  # Convert ObjectId to string
        return jsonify(events)  # Return JSON response
    except Exception as e:
        logging.error(f"Error fetching events: {e}")
        return jsonify({'error': 'Failed to fetch events'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
