from flask import Flask, render_template, request, jsonify
from chatbot import EventPlanner

app = Flask(__name__)
planner = EventPlanner()

@app.route('/')
def index():
    return render_template('index.html')

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
            from schedule import create_event
            success = create_event(event_data)
            
            if success:
                # Reset the planner for the next event
                response = success
                planner.reset()
                
            else:
                response = "Failed to create the event. Please try again."
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=False)