from openai import OpenAI
# Replace with your own API_key
api_key = ''

client = OpenAI(api_key=api_key)

client.files.create(
  file=open("GEF_2014_training.jsonl", "rb"),
  purpose="fine-tune"
)

# List files
files = client.files.list()


# Check for your file in the list
for file in files.data:
    if file.filename == "GEF_2014_training.jsonl.jsonl":
        print(f"File ID: {file.id} - Filename: {file.filename} has been uploaded successfully.")

print(client.fine_tuning.jobs.list(limit=10))


client.fine_tuning.jobs.create(
  training_file="",
  model="gpt-3.5-turbo",
    suffix="GEF_2014"
)