from flask import Flask, render_template, request, jsonify
from chatbot import EventPlanner
from schedule import create_event
import os  # Add this import

app = Flask(__name__)
planner = EventPlanner()

# Storing the event count
EVENT_COUNT_FILE = 'event_count.txt'

def get_event_count():
    if os.path.exists(EVENT_COUNT_FILE):
        with open(EVENT_COUNT_FILE, 'r') as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def increment_event_count():
    count = get_event_count() + 1
    with open(EVENT_COUNT_FILE, 'w') as f:
        f.write(str(count))
    return count

@app.route('/')
def index():
    return render_template('index.html', event_count=get_event_count())

@app.route('/index.html')
def index1():
    return render_template('index.html', event_count=get_event_count())

@app.route('/schedule.html', methods=['GET'])
def schedule():
    planner.reset()
    return render_template('schedule.html', event_count=get_event_count())

@app.route('/get', methods=['POST'])
def chat():
    user_input = request.form['msg']
    response = planner.get_response(user_input)
    
    # Check if the event is ready to be created
    if "optional details" in response.lower():
        # If the user says 'no', proceed to create the event
        if user_input.lower() == 'no':
            event_data = planner.event_template
            print("\nChatbot: Here's your event summary:")
            print(event_data)
            
            # Call the create_event function from schedule.py
            success = create_event(event_data)
            
            if success:
                # Increment the counter
                event_count = increment_event_count()
                # Reset the planner for the next event
                response = f"{success}\n\nTotal events created: {event_count}"
                planner.reset()
            else:
                response = "Failed to create the event. Please try again."
    return jsonify({"response": response})

# Add this new route
@app.route('/event_count')
def event_count():
    return jsonify({"count": get_event_count()})

if __name__ == '__main__':
    app.run(debug=True)