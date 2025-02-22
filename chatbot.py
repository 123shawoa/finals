import os
import google.generativeai as genai
from datetime import datetime, timedelta
import re

genai.configure(api_key=os.environ['GEMINI_APP_KEY'])

# Create the model with creative config
generation_config = {
    "temperature": 1.2,
    "top_p": 0.9,
    "top_k": 60,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

class EventPlanner:
    def __init__(self):
        self.event_template = {
            "summary": None,
            "location": "Online",
            "description": "Created by AI Assistant",
            "colorId": 6,
            "start": {"timeZone": "America/New_York"},
            "end": {"timeZone": "America/New_York"},
            "attendees": []
        }
        self.required_fields = {
            "summary": "What's the title of your event?",
            "start.dateTime": "When does it start? (e.g., 'tomorrow 2 PM' or '2025-03-15 14:30')",
            "end.dateTime": "When does it end? (e.g., '2 hours after it starts' or '2025-03-15 16:30')",
            "location": "Where is it happening? (e.g., 'Central Park, New York' or 'Online')"  # Add location as a required field
        }
        self.current_field = None
        self.current_question = None
        self.fields_iterator = iter(self.required_fields)  # Iterator for required fields

    def get_response(self, user_input):
        if self.current_field is None:
            # Start the conversation by asking the first question
            try:
                self.current_field = next(self.fields_iterator)
                self.current_question = self.required_fields[self.current_field]
                return self.current_question
            except StopIteration:
                # All fields have been processed, reset the iterator
                return "All required fields have been filled. Do you want to add any optional details? (Type 'no' to skip)"
        if user_input.lower() == 'cancel':
            self.reset()
            return "Event creation cancelled!"

        # Handle the current field
        if self.current_field.startswith('start.') or self.current_field.startswith('end.'):
            key = self.current_field.split('.')[0]
            reference_time = None
            if key == 'end':
                reference_time = self.event_template.get('start', {}).get("dateTime")
            try:
                iso_time = self.parse_datetime(user_input, reference_time=reference_time)
                if key == 'end':
                    start_iso = self.event_template['start']['dateTime']
                    start_dt = datetime.fromisoformat(start_iso)
                    end_dt = datetime.fromisoformat(iso_time)
                    if end_dt <= start_dt:
                        return "❌ The end time must be AFTER the start time. Please try again!"
                self.event_template[key]["dateTime"] = iso_time
                # Move to the next field
                self.current_field = next(self.fields_iterator, None)
                if self.current_field is None:
                    # All required fields are filled, proceed to optional fields
                    return "Great! Do you want to add any optional details like description, or attendees? (Type 'no' to skip)"
                self.current_question = self.required_fields[self.current_field]
                return self.current_question
            except Exception as e:
                return f"⏳ Hmm, I didn't quite get that time. Let's try again! ({str(e)})"
        else:
            # Handle non-date fields (e.g., summary)
            extraction_prompt = f'''Extract the {self.current_field.replace('_', ' ')} from this message: "{user_input}". 
            Respond ONLY with the extracted value.'''
            extracted = model.generate_content(extraction_prompt).text.strip()
            if extracted.lower() != 'none':
                self.event_template[self.current_field] = extracted
                # Move to the next field
                self.current_field = next(self.fields_iterator, None)
                if self.current_field is None:
                    # All required fields are filled, proceed to optional fields
                    return "Great! Do you want to add any optional details like description, or attendees? (Type 'no' to skip)"
                self.current_question = self.required_fields[self.current_field]
                return self.current_question
            else:
                return "I didn't catch that. Could you please repeat?"

    def reset(self):
        """Reset the conversation state"""
        self.event_template = {
            "summary": None,
            "location": "Online",
            "description": "Created by AI Assistant",
            "colorId": 6,
            "start": {"timeZone": "America/New_York"},
            "end": {"timeZone": "America/New_York"},
            "attendees": []
        }
        self.current_field = None
        self.current_question = None
        self.fields_iterator = iter(self.required_fields)  # Reset the iterator

    def parse_datetime(self, time_str, reference_time=None):
        """Convert natural language time to ISO format using Gemini"""
        prompt = f'''Convert this time reference to ISO 8601 format in America/New_York timezone: "{time_str}". 
        Current time is {datetime.now().strftime("%Y-%m-%d %H:%M")}. 
        '''
        if reference_time:
            prompt += f" The start time is {reference_time} meaning your answer must be after the start time and for 2 hours after it starts just add two hours to the start time"
        prompt += " Respond ONLY with the ISO timestamp."
        response = model.generate_content(prompt)
        return response.text.strip()
def chatting(planner):
    planner = EventPlanner()
    while True:
        # print("\nChatbot: Ready to create an event! Type 'start' to begin or 'exit' to quit")
        user_input = input("You: ").lower()
        
        #if user_input in ['exit', 'quit', 'bye']:
            # print("Chatbot: Farewell! May your calendar stay organized 🌟")
            # break
            
        event_data = planner.collect_info()
        if event_data:
            # Connect to schedule.py here
            print("\nChatbot: Here's your event summary:")
            print(event_data)
            # Uncomment to actually create event
            from schedule import create_event
            create_event(event_data)
                
