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
            "end.dateTime": "When does it end? (e.g., '2 hours after it starts' or '2025-03-15 16:30')"
        }

    def parse_datetime(self, time_str, reference_time = None):
        """Convert natural language time to ISO format using Gemini"""
        prompt = f'''Convert this time reference to ISO 8601 format in America/New_York timezone: "{time_str}". 
        Current time is {datetime.now().strftime("%Y-%m-%d %H:%M")}. 
        '''
        if reference_time:
            prompt += f" The end time must be after {reference_time} and if not then use your judgement for it"
        prompt += " Respond ONLY with the ISO timestamp."
        response = model.generate_content(prompt)
        return response.text.strip()

    def collect_info(self):
        print("Chatbot: Let's schedule your event! (Type 'cancel' anytime to exit)")
        
        for field, question in self.required_fields.items():
            while True:
                # Creative prompt to engage user
                creative_question = f"Chatbot: {question}\nYou can also tell me about location, description, or attendees!"
                print(creative_question)
                
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'cancel':
                    print("Chatbot: Event creation cancelled!")
                    return None

                # Extract core field using AI
                if field.startswith('start.') or field.startswith('end.'):
                    key = field.split('.')[0]
                    reference_time = None
                    if key == 'end':
                        reference_time = self.event_template.get('start', {}).get("dateTime")
                    try:
                        iso_time = self.parse_datetime(user_input, reference_time=reference_time)
                
                        # New validation check for end time
                        if key == 'end':
                            # Get already set start time
                            start_iso = self.event_template['start']['dateTime']
                    
                        # Convert to datetime objects for comparison
                            start_dt = datetime.fromisoformat(start_iso)
                            end_dt = datetime.fromisoformat(iso_time)
                    
                            if end_dt <= start_dt:
                                print("Chatbot: ❌ The end time must be AFTER the start time. Please try again!")
                                continue  # Restart the loop to re-prompt

                        self.event_template[key]["dateTime"] = iso_time
                        break
                    except Exception as e:
                        print(f"Chatbot: ⏳ Hmm, I didn't quite get that time. Let's try again! ({str(e)})")
                else:
                    # Use AI to extract relevant info from free-form input
                    extraction_prompt = f'''Extract the {field.replace('_', ' ')} from this message: "{user_input}". 
                    Respond ONLY with the extracted value.'''
                    extracted = model.generate_content(extraction_prompt).text.strip()
                    
                    if extracted.lower() != 'none':
                        self.event_template[field] = extracted
                        print(f"Chatbot: Great! I'll set '{field}' to: {extracted}")
                        break

        # Collect optional fields through creative prompts
        print("Chatbot: Want to add anything special? (Location, description, guests, or 'no')")
        extras = input("You: ")
        if extras.lower() != 'no':
            extraction_prompt = f'''Extract event details from: "{extras}". Return as JSON with keys: 
            location, description, attendees (comma-separated emails). Unknown values as null.'''
            
            try:
                extras_data = model.generate_content(extraction_prompt).text
                extras_json = eval(extras_data)
                
                if 'location' in extras_json:
                    self.event_template['location'] = extras_json['location'] or "Online"
                if 'description' in extras_json:
                    self.event_template['description'] = extras_json['description'] or "Created by AI Assistant"
                if 'attendees' in extras_json:
                    self.event_template['attendees'] = [{"email": e.strip()} 
                                                      for e in extras_json['attendees'].split(',') 
                                                      if e.strip()]
            except:
                print("Chatbot: Oops, I'll stick to the basics then!")

        return self.event_template

def main():
    planner = EventPlanner()
    
    while True:
        print("\nChatbot: Ready to create an event! Type 'start' to begin or 'exit' to quit")
        user_input = input("You: ").lower()
        
        if user_input in ['exit', 'quit', 'bye']:
            print("Chatbot: Farewell! May your calendar stay organized 🌟")
            break
            
        if user_input == 'start':
            event_data = planner.collect_info()
            if event_data:
                # Connect to schedule.py here
                print("\nChatbot: Here's your event summary:")
                print(event_data)
                # Uncomment to actually create event
                from schedule import create_event
                create_event(event_data)
                
if __name__ == "__main__":
    main()