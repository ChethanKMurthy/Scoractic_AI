Gemini-Powered Streamlit Application

This project is a modern Python web application built using Streamlit for the frontend and the Google Gemini API for powerful generative AI capabilities. It uses best practices for environment management with python-dotenv.

✨ Features

Interactive Web UI: Built with Streamlit, providing a clean and intuitive interface.

Generative AI Integration: Leverages the google-generativeai SDK to interact with the Gemini models.

Secure API Key Management: Uses .env files and python-dotenv to safely load the API key without hardcoding it.

Standard Python Implementation: Uses native modules like json, os, and datetime.

🚀 Getting Started

Follow these steps to set up and run the application locally.

1. Prerequisites

Python 3.9+

Google Gemini API Key: You can obtain a key from [Google AI Studio].

2. Setup (Create and Activate Virtual Environment)

It is highly recommended to use a virtual environment to manage dependencies.

# 1. Create a virtual environment (named .venv)
python3 -m venv .venv

# 2. Activate the virtual environment (for macOS/Linux)
source .venv/bin/activate


3. Install Dependencies

Install the required packages using the requirements.txt file (which contains streamlit, google-generativeai, and python-dotenv).

pip install -r requirements.txt


4. Configure API Key

The application requires your Gemini API key to run. Create a file named .env in the root directory of your project and add your key:

# .env file content
GEMINI_API_KEY="YOUR_API_KEY_HERE"


Replace "YOUR_API_KEY_HERE" with the actual key you obtained from Google AI Studio.

5. Run the Application

Once the environment is activated, the dependencies are installed, and the .env file is set up, you can run the application using Streamlit:

streamlit run your_main_app_file.py


(Note: Replace your_main_app_file.py with the actual name of your Python script.)

The command will automatically open the web application in your default browser.

🛠️ Dependencies

The core external dependencies are:

Package

Purpose

streamlit

Creates the interactive web UI.

google-generativeai

Connects to the Gemini API for AI generation.

python-dotenv

Loads environment variables from the .env file.

🛑 Important Notes

Security: Never commit your .env file or API key directly to version control (like Git). Ensure .env is listed in your .gitignore file.

Python Version: If you have multiple Python versions, use python3 -m venv and ensure the activated environment is using Python 3.
