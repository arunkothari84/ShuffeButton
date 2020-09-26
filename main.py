import requests
import json
import random
import flask

# Initialization of flask app
app = flask.Flask(__name__)


client_id = ''  # Client id from spotify
client_secret = ''  # Client secret from spotify
base_64_encoded = "" # client id:client secret


# To redirect the home page to authorization page of spotify
@app.route('/', methods=['GET'])
def home():
    return flask.redirect(f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fsuccess&scope=user-library-read%20user-read-currently-playing%20user-modify-playback-state")


# To get authorization code from the spotify redirected URI if the user authorizes
@app.route('/success', methods=['GET'])
def code():
    if 'code' in flask.request.args:
        token = str(flask.request.args['code'])
        token = str(token.split(' ')[0])
        access_token(token)


# To get the access token from the authorization code got from previous function
def access_token(token):
    url = F'https://accounts.spotify.com/api/token'
    data = {
        "grant_type": "authorization_code",
        "code": token,
        "redirect_uri": "http://127.0.0.1:5000/success"
    }
    header={
         "Authorization": F"Basic {base_64_encoded}"
    }
    responses = requests.request("POST", url, data=data, headers=header)
    print(responses.status_code)
    responses_dict = json.loads(responses.text)
    print(responses.text)
    access = responses_dict['access_token']
    headers = {
        'Accept': 'application / json',
        'Content-Type': 'application/json',
        'Authorization': F'Bearer {access}'
    }
    main(headers)

# To get the saved tracks from the user library
def get_saved_tracks(headers):

    url = F"https://api.spotify.com/v1/me/tracks?market=IN&limit=40&offset={random.randrange(0, 100)}"
    response = requests.request("GET", url, headers=headers)
    response_dict = json.loads(response.text)
    ran_num = random.randrange(0, 9)
    print(response_dict['items'][ran_num]['track']['name'])
    print(response_dict['items'][ran_num]['track']['id'])
    print(f"{response_dict['items'][ran_num]['track']['duration_ms']}ms")
    return response_dict['items'][ran_num]['track']['id']


# To get the recommendation based on the track got from the library
def get_recommendations(saved_track_id, headers):

    url = F"https://api.spotify.com/v1/recommendations?limit=20&market=IN&seed_tracks={saved_track_id}&min_popularity=50"
    response = requests.request("GET", url, headers=headers)
    response_dict = json.loads(response.text)
    ran_num = random.randrange(0, 9)
    try:
        print(response_dict['tracks'][ran_num]['name'])
        print(response_dict['tracks'][ran_num]['id'])
        return response_dict['tracks'][ran_num]['id']

    except IndexError:
        get_recommendations(saved_track_id. headers)


# To add the recommended song to the queue
def add_to_queue(recommendations_id, headers):
    url = F"https://api.spotify.com/v1/me/player/queue?uri=spotify%3Atrack%3A{recommendations_id}"
    requests.request("POST", url, headers=headers)
    print("done")


# To get the new song if user continues to play the recommended songs
def currently_playing_song(headers):
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    response = requests.request("GET", url, headers=headers)
    response_dict = json.loads(response.text)
    try:
        return response_dict['item']['id']
    except TypeError:
        main(headers)


# Main functions to call other functions
def main(headers):
    saved_track_id = get_saved_tracks(headers)
    recommendations_id = get_recommendations(saved_track_id, headers)
    add_to_queue(recommendations_id, headers)

    while True:
        if recommendations_id == currently_playing_song(headers):
            saved_track_id = get_saved_tracks(headers)
            recommendations_id = get_recommendations(saved_track_id, headers)
            add_to_queue(recommendations_id, headers)

# To run the flask app
app.run()
