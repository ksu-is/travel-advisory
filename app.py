import streamlit as st
import openai
import os
import redis
import requests
from dotenv import load_dotenv

# Calling key from environment variables

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

host = os.environ.get('REDIS_HOST')
port = os.environ.get('REDIS_PORT')
password = os.environ.get('REDIS_PASSWORD')


def get_itinerary(dest_name, length_of_stay):
    
    # Reading redis credentials from environment variables
    redis_client = redis.Redis(host=host, port=port, password=password, decode_responses=True)
    
    # Creating a key for the destination name and length of stay
    key = f"{dest_name}_{length_of_stay}"
    placeholder = st.empty()
    
    # If same key is called then return the value from redis
    if redis_client.exists(key):
        itinerary = redis_client.get(key)
        placeholder.text("")
        st.success(itinerary)
        st.stop()
        
    
    # Getting the IP address of the user
    user_ip = requests.get('https://api.ipify.org').text
    
    # Checking if IP address exists in database
    if redis_client.exists(user_ip):
        request_count = int(redis_client.get(user_ip))
        
        if request_count > 10:
            st.write("You have exceeded the maximum number of requests. Please try again tomorrow or reach out to me to increase rate-limit.")
            st.stop()
    else:
        redis_client.set(user_ip, 0, ex=86400)
    
    # Incrementing the request count for the IP address
    redis_client.incr(user_ip)

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
    itinerary = itinerary.replace("Day:", "\nDay")
    
    # Storing the key and value in redis for 1 week
    redis_client.set(key, itinerary, ex=604800)

    return itinerary

# Set up the app name
st.title("Travel Advisory")

# Defining the footer content and the link to the source code

descript = """Made by Prayag Shah with ❤️. Check out the source code at [GitHub](https://github.com/prayagnshah/travel-advisory). <br> Feel free to reach out on [Linkedin](https://www.linkedin.com/in/prayag-shah/) if you have any questions."""

# Add the footer to the app
st.markdown(descript, unsafe_allow_html=True)

# Set the maximum number of words in the destination name
max_words= 3

# Get user input
destination_name = st.text_input("Enter your destination")

# Count the number of words in the input
num_words = len(destination_name.strip().split())

# Show a warning message if the number of words exceeds the limit
if num_words > max_words:
    st.warning("The destination name should be less than 3 words")
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