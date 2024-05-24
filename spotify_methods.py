from dotenv import load_dotenv
import pandas as pd
import os
import base64
from requests import post, get
import json
import tekore
import numpy as np


def get_client_info():

    load_dotenv()
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    return client_id, client_secret

# Gets the access token
def get_token():
    client_id, client_secret = get_client_info()
    auth_str = client_id + ":" + client_secret
    auth_bytes = auth_str.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded", 
    }

    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)

    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token

# Gets the header that will be used in requests
def get_auth_headers(token):
    return {"Authorization": "Bearer " + token,
            "Retry-After": "10"}

# Search for artists - Deprecated method
def search_for_artists(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_headers(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query

    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)


# Method that will get a playlist and create a df based on it
def get_playlists(token, playlist_id):

    url = "https://api.spotify.com/v1/playlists"
    query_url = url + "/" + playlist_id + "/tracks"
    headers = get_auth_headers(token)

    song_dict = {}
    
    count = 0
    while True:

        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)

        for item in json_result['items']:
            song_dict[count] = item
            count+=1

        query_url = json_result['next']

        if not query_url:
            break

    # Creating a DF with the tracks in then playlist
    df = pd.DataFrame.from_dict(song_dict, orient='index')
    
    track_dict = df['track'].values

    track_information = []

    # count = 0
    for i in track_dict:
        track_information.append([i['preview_url'], i['external_urls'], i['href'], i['name'], i['id'], i['artists']])

    df['preview_url'] = [array[0] for array in track_information]
    df['external_urls'] = [array[1] for array in track_information] 
    df['href'] = [array[2] for array in track_information] 
    df['name'] = [array[3] for array in track_information] 
    df['id'] = [array[4] for array in track_information] 
    df['artists'] = [array[5] for array in track_information]

    df = df.drop(['preview_url', 'track', 'primary_color', 'video_thumbnail', 'is_local', 'added_by', 'added_at'], axis=1)

    return df

def get_track_audio_features(token, df, csv):

    track_ids = df['id'][:]
    url = "https://api.spotify.com/v1/audio-features?ids="
    headers = get_auth_headers(token)
    track_audio_features = []
    data = []

    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100].values
        id_str = ""
        for id in batch:
            id_str += id + ","
        id_str = id_str[:-2]

        query_url = url + id_str
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)

        track_audio_features.append(json_result['audio_features'])

    test_df = pd.concat([pd.DataFrame(track_audio_features[i][:-1]) for i in range(len(track_audio_features))], ignore_index=True)
    df = pd.concat([df, test_df], axis=1)
    df.to_csv(csv)
    return df
   
# Gets track audio for one song (test method)        
def get_track_audio(id, token):
    url = "https://api.spotify.com/v1/audio-features/"
    headers = get_auth_headers(token)
    query_url = url + id
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)