from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import random

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_playlists(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result_playlists = json.loads(result.content)
    return json_result_playlists

def extract_playlist_info(json_result_playlists):
    playlists_info = []
    for playlist in json_result_playlists["items"]:
        playlist_name = playlist["name"]
        playlist_id = playlist["id"]
        playlists_info.append({"name": playlist_name, "id": playlist_id})
    return playlists_info

def get_playlist_tracks(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    params = {
        "fields": "items(track(name,artists(name,id)))"
    }
    result = get(url, headers=headers, params=params)
    json_result_tracks = json.loads(result.content)
    return json_result_tracks

def get_albums_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = get_auth_header(token)
    params = {
        "limit": 50,
        # "include_groups": "album",  # This ensures that only albums are returned, not singles or compilations
        "market": "US",  # You can specify the market to get albums available in a specific region
        "fields": "items(name,id)"  # Specify the fields you want to include
    }
    result = get(url, headers=headers, params=params)
    json_result_albums = json.loads(result.content)
    return json_result_albums

def get_tracks_by_album(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result_tracks = json.loads(result.content)
    return json_result_tracks

token = get_token()
user_id = "315s4hcu5bbbm7qi4m3a6ev3g54a"
result = get_playlists(token, user_id)
playlist_info = extract_playlist_info(result)
for index, playlist in enumerate(playlist_info):
    print(f"{index + 1}. Playlist Name: {playlist['name']}")
    print(f"   Playlist ID: {playlist['id']}")
    print()

# Prompt the user to select a playlist
selected_index = int(input("Enter the number of the playlist you want to retrieve tracks from: ")) - 1
selected_playlist_id = playlist_info[selected_index]["id"]

playlist_tracks = get_playlist_tracks(token, selected_playlist_id)
# print(playlist_tracks)

# artist_id = "6sKGpXFS8bI6lKbRfhl52T"
# artist_albums = get_albums_by_artist(token, artist_id)

# print("Artist's Albums:")
# for album in artist_albums["items"]:
#     print("Album Name:", album["name"])
#     print("Album ID:", album["id"])
#     print()

# album_id = "5BZhw2W7PHHcYxQXX5B2VS"
# album_tracks = get_tracks_by_album(token, album_id)
# print("Album Tracks: ")
# for track in album_tracks['items']:
#     print("Track Name:", track["name"])
#     print("Track ID:", track["id"])
#     print()

final_tracks = []

for item in playlist_tracks['items']:
    track_name = item['track']['name']
    artist_id = item['track']['artists'][0]['id']  # Assuming only one artist per track
    artist_albums = get_albums_by_artist(token, artist_id)
    all_album_tracks = []

    for album in artist_albums['items']:
        album_id = album['id']
        album_tracks = get_tracks_by_album(token, album_id)
        all_album_tracks.extend(album_tracks['items'])

    if all_album_tracks:
        # Randomly select a track from all the tracks by the artist
        selected_track = random.choice(all_album_tracks)
        final_tracks.append(selected_track)

# Print the final list of tracks
print("New Playlist")
for track in final_tracks:
    print("Track Name:", track["name"])
    print("Track ID:", track["id"])
    print()