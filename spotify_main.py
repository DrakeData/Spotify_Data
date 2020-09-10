import config
import requests
import json
import pandas as pd
from datetime import datetime
import spotipy.util as util
from tzlocal import get_localzone
import dateutil
import pandas_gbq
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    r'/Users/Nicholas/Desktop/GCP/GCP_Keys/spotify-project-287802-e5e6c43e8ecb.json'
)

# Create the file name we will be exporting later
today = datetime.today().strftime('%Y%m%d')

destinatoin_table = 'spotify_api.recently_played_tracks'
project_id = 'spotify-project-287802'


def spotify_access_token():
    '''
    Script generates access token to access spotify's api endpoitn.
    :return: auth_token
    '''

    username = config.username
    client_id = config.client_id
    client_secret = config.client_secret
    redirect_uri = 'http://localhost:7777/callback'
    scope = 'user-read-recently-played'

    auth_token = util.prompt_for_user_token(username=username,
                                            scope=scope,
                                            client_id=client_id,
                                            client_secret=client_secret,
                                            redirect_uri=redirect_uri
                                            )
    return auth_token


def recently_played():
    '''
    Pulls recently played tracks from spotify's endpoint
    :return: df1
    '''

    auth_token = spotify_access_token()

    base_url = 'https://api.spotify.com/v1/me/player/recently-played?'
    # track_id = '6y0igZArWVi6Iz0rj35c1Y'

    # 2. Authentication
    # 3. Parameters -- would be stored with authentication
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    # 4. Create an empty list
    personal_data = []  # would be good explore how to capture data at different points in time
    r = requests.get(base_url + "&limit=50", headers=headers)
    personal_data.append(json.loads(r.text))

    track_ids = []
    album_ids = []
    artist_ids = []
    album_names = []
    artist_names = []
    track_names = []
    popularity_ls = []
    played_ats = []

    for i in range(len(personal_data[0]['items'])):
        track_ids.append(personal_data[0]['items'][i]['track']['id'])  # Track ID
        album_ids.append(personal_data[0]['items'][i]['track']['album']['id'])  # Albumn ID
        artist_ids.append(personal_data[0]['items'][i]['track']['artists'][0]['id'])  # Artist ID
        album_names.append(personal_data[0]['items'][i]['track']['album']['name'])  # Album Name
        artist_names.append(personal_data[0]['items'][i]['track']['artists'][0]['name'])  # Artist Name
        track_names.append(personal_data[0]['items'][i]['track']['name'])  # Track Name
        popularity_ls.append(personal_data[0]['items'][i]['track']['popularity'])  # Track Popularity
        played_ats.append(personal_data[0]['items'][i]['played_at'])

    list_dic = {'track_id': track_ids,
                'album_id': album_ids,
                'artist_id': artist_ids,
                'track_name': track_names,
                'artist_name': artist_names,
                'album_name': album_names,
                'track_popularity': popularity_ls,
                'time_palyed': played_ats
                }

    df1 = pd.DataFrame(list_dic)

    # Create empty column to append data to
    df1['local_time'] = ''

    for i in range(len(personal_data[0]['items'])):
        # Convert UTC to local time zone
        utc_time = dateutil.parser.parse(df1['time_palyed'].iloc[i]).astimezone(get_localzone())
        # Format date/time
        local_time = utc_time.strftime('%Y-%m-%d %H:%M:%S')

        df1['local_time'].iloc[i] = local_time

    return df1


def bq_dup_check():
    '''
    Pulls last 100 tracks from spotify_api.recently_played_tracks and drops any duplicates from df1
    :return: df1_clean
    '''

    df1 = recently_played()

    # Query the BQ table for case_ids
    project_id = "spotify-project-287802"

    sql = """
    SELECT time_palyed
    FROM `spotify-project-287802.spotify_api.recently_played_tracks`
    ORDER BY time_palyed DESC
    LIMIT 100
    """

    # Load table into df
    bq_df = pandas_gbq.read_gbq(sql, project_id=project_id, credentials=credentials)

    # Create list of dq_df case_ids
    case_to_drop = bq_df['time_palyed'].tolist()
    # Compare case_ids from df1 if already in case_to_drop list
    df1_clean = df1[~df1['time_palyed'].str.contains('|'.join(case_to_drop))]
    print('After duplicate check, there are now {} new Case IDs from the API.'.format(len(df1_clean['time_palyed'])))

    return df1_clean


def bq_load_data(destinatoin_table, project_id):
    '''
    Loads df_clean to potify_api.recently_played_tracks
    :return:
    '''

    df1_clean = bq_dup_check()
    print('Loading data into GCP BigQuery')
    # Load into GCP BigQuery
    # Connect to Google Cloud API and upload dataframe


    pandas_gbq.to_gbq(df1_clean, destinatoin_table, project_id, if_exists='append',
                      credentials=credentials)
    print('Script is complete; check table for details.')

bq_load_data(destinatoin_table, project_id)