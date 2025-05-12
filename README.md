This project is an AI-powered chatbot assistant designed to help college students organize their classes, events, and academic schedules. The chatbot leverages the Gemini AI API for natural language understanding, and integrates with the Google Calendar API to automate event creation and scheduling. The project features a Flask-based user interface that allows users to interact with the chatbot smoothly through a web application.

Key Features
 AI Chatbot: Built using Google Gemini for free API access and flexible conversation capabilities.

Google Authentication: Secure login and permissions to manage the user’s Google Calendar.

Google Calendar Integration: Automatically schedules, updates, and manages events on behalf of the student.

Flask Front-End: User-friendly interface for chatting with the assistant and tracking event creation.

Persistent Event Tracking: Local storage of event counts and reset functionality.

Technologies Used
Python 3.x

Flask (Web framework)

Google Gemini API (LLM chatbot)

Google Calendar API

HTML/CSS (for templates)

Google OAuth 2.0 Authentication

How It Works
The user interacts with the chatbot via a Flask web interface.

The chatbot gathers details about the event: title, date/time, location, and optional attendees.

Once all details are collected, the chatbot confirms and creates the event directly in Google Calendar.

The number of scheduled events is tracked locally (event_count.txt).