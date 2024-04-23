import csv
import json

# Open the CSV file for reading
with open('../Datasets/GEFCom2014-E.csv', 'r') as csv_file:

# with open('lmp_load_temp_2022_hourly.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    # Convert CSV reader object to list for easier processing
    rows = list(csv_reader)

# Initialize an empty list to hold our JSON objects
json_objects = []

# Process each chunk of 48 rows at a time (24 for previous day, 24 for today)
for i in range(70128, 78912, 24):
    # Ensure there's enough rows for the last chunk
    if i + 47 < len(rows):
        json_data = {"messages": []}

        system_message = {
            "role": "system",
            "content": "You are an electrical engineer who predict electricity price based on provided information"
        }
        json_data["messages"].append(system_message)
                # Creating JSON object for the previous day
        prev_day = {
            "role": "user",
            "content": f"Information for previous day \nLoads_p: {', '.join([row[2] for row in rows[i:i + 24]])}\nTemp_p: {', '.join([row[3] for row in rows[i:i + 24]])}\nAnd here is information for today\nTemp_t: {', '.join([row[3] for row in rows[i + 24:i + 48]])}"

                       # "content": f"You are an electrical engineer who predict electricity load based on provided information. Provide me the 24 hour prediction directly. Here is information for previous day \nLoads_p: {', '.join([row[1] for row in rows[i:i + 24]])}\nTemp_p: {', '.join([row[2] for row in rows[i:i + 24]])}\nAnd here is information for today\nTemp_t: {', '.join([row[2] for row in rows[i + 24:i + 48]])}"
        }

        # Creating JSON object for today's forecast
        today_forecast = {
            "role": "assistant",
            "content": f"The load for today is: {', '.join([row[2] for row in rows[i + 24:i + 48]])}"
        }

        # Append the created objects to our list
        json_data["messages"].append(prev_day)
        json_data["messages"].append(today_forecast)

        json_objects.append(json_data)
# Write the JSON objects to a file
with open('GEF_2014_training.jsonl', 'w') as jsonl_file:
    for day_data in json_objects:
        jsonl_file.write(json.dumps(day_data) + '\n')

print("JSON file has been created.")