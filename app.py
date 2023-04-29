import streamlit as st
import openai
from dotenv import load_dotenv
import os

# Calling key from environment variables

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_itinerary(dest_name, length_of_stay):

    # Call the OpenAI API

    response = openai.Completion.create(
        engine="text-davinci-003",  # Which GPT-3 engine to use
        prompt="Can you recommend a " + str(length_of_stay) + \
        "day itinerary for " + str(dest_name) + "?" + \
        "in detail ? And they should be in format day1, day2, etc",  # The input text
        temperature=0.2,  # How creative the response should be
        max_tokens=1024,  # Maximum length of the response
        n=2,  # How many responses to generate
        stop=None  # Text to stop generation at (optional)
    )

    # Extract the response text

    itinerary = response.choices[0].text.strip()
    
    # Inserting a line break after each day

    itinerary = itinerary.replace("Day:", ":\nDay")

    return itinerary

# Set up the app name


st.title("Travel Advisory")

# Defining the footer content and the link to the source code

descript = """Made by Prayag Shah with ❤️. Check out the source code at [GitHub](https://github.com/prayagnshah/travel-advisory)"""

# Add the footer to the app
st.markdown(descript, unsafe_allow_html=True)

# Set the maximum number of words in the destination name
MAX_WORDS = 10

# Get user input

destination_name = st.text_input("Enter your destination")

# Count the number of words in the input

num_words = len(destination_name.split())

# Show a warning message if the number of words exceeds the limit

if num_words > MAX_WORDS:
    st.warning("The destination name should be less than 10 words")
    st.stop()

length_of_stay = st.slider("Enter the length of your stay", 1, 10)

# Generate itinerary and show loading message

if st.button("Generate Itinerary"):

    # Creating a placeholder for the loading message

    placeholder = st.empty()
    placeholder.text("Building itinerary...")

    # Call the function to generate the itinerary

    itinerary = get_itinerary(destination_name, length_of_stay)
    placeholder.text("")
    st.success(itinerary)