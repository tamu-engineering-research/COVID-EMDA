import openai
import requests


# Set your API key here
api_key = ''
from openai import OpenAI

client = OpenAI(api_key=api_key)
text_file = 'GEF_2014_training.txt'
with open (text_file,'r') as file:
    for line in file:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "You are an electrical engineer who predict electricity load based on provided information. Provide me the 24 hour prediction directly. Here is information for previous day \nLoads_p: 58424.33, 55446.46, 53076.05, 51437.19, 50811.79, 51124.94, 51688.38, 52458.71, 55212.39, 59357.15, 63723.66, 68131.01, 72384.50, 76200.73, 78821.42, 79397.05, 79748.25, 79526.82, 78622.83, 76606.11, 73845.04, 71433.59, 67564.37, 63310.65\nTemp_p: 36.00, 33.80, 31.40, 30.00, 29.00, 28.40, 27.90, 27.50, 27.30, 27.10, 27.00, 26.80, 26.70, 28.20, 30.40, 32.50, 34.50, 36.30, 37.70, 38.60, 39.10, 38.90, 38.20, 36.90\nAnd here is information for today\nTemp_t: 35.20, 33.20, 31.20, 30.00, 29.20, 28.60, 28.10, 27.70, 27.40, 27.20, 27.10, 27.00, 27.00, 28.50, 30.60, 32.80, 34.90, 36.80, 38.20, 39.20, 39.60, 39.40, 38.70, 37.40"
                }
            ],
            temperature=1,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

print(response)

