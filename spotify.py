from dotenv import load_dotenv, find_dotenv
import os

print(find_dotenv())
load_dotenv()

client_id = os.getenv("CLIENT_ID")
print(client_id)
client_secret = os.getenv("CLIENT_SECRET")

print(client_id , client_secret)