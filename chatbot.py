import os
import google.generativeai as genai

genai.configure(api_key=os.environ['GEMINI_APP_KEY'])


# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[

  ]
)
while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Chatbot: Goodbye!")
        break

    # Send the user's message to the chatbot
    response = chat_session.send_message(user_input)

    # Print the chatbot's response
    print(f"Chatbot: {response.text}")