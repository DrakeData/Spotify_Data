import config
import os
import requests
import json
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import spotipy.util as util
from tzlocal import get_localzone
import dateutil

pd.options.mode.chained_assignment = None  # default='warn'

name_of_user = 'Tim'

print(f"Hello {name_of_user}, Let's gather your spotify data!")



# Create the file name we will be exporting later
today = datetime.today().strftime('%Y%m%d')
file_name = f"Spotify_Export_{today}.xlsx"
main_writer = pd.ExcelWriter(file_name)

current_directory = os.path.abspath(os.getcwd())
export_file_path = os.path.join(current_directory, 'spotify_export_files', file_name)


username = config.username
client_id = config.client_id
client_secret = config.client_secret
redirect_uri = 'http://localhost:7777/callback'
scope = 'user-read-recently-played, user-top-read'

auth_token = util.prompt_for_user_token(username=username,
                                   scope=scope,
                                   client_id=client_id,
                                   client_secret=client_secret,
                                   redirect_uri=redirect_uri)



def recently_played_track(auth_token):
    '''
    Pulls back user's most recently played track data
    :param auth_token: authentication token needed to access Spotify's api
    :return: personal_data
    '''
    base_url = 'https://api.spotify.com/v1/me/player/recently-played?'

    # 2. Authentication
    # 3. Parameters -- would be stored with authentication
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    # 4. Create an empty list
    personal_data = []
    r = requests.get(base_url+"&limit=50", headers=headers)
    personal_data.append(json.loads(r.text))

    return personal_data


def recently_played_data():
    '''
    Parson json from personal_data and put it into a df
    :return: df1, personal_data
    '''
    print(f"Gathering {name_of_user}'s recently played tracks...")
    personal_data = recently_played_track(auth_token)

    track_ids = []
    album_ids = []
    artist_ids = []
    album_names = []
    artist_names = []
    track_names = []
    popularity_ls = []
    played_ats = []

    for i in tqdm(range(len(personal_data[0]['items']))):
        track_ids.append(personal_data[0]['items'][i]['track']['id']) # Track ID
        album_ids.append(personal_data[0]['items'][i]['track']['album']['id']) # Albumn ID
        artist_ids.append(personal_data[0]['items'][i]['track']['artists'][0]['id']) # Artist ID
        album_names.append(personal_data[0]['items'][i]['track']['album']['name']) # Album Name
        artist_names.append(personal_data[0]['items'][i]['track']['artists'][0]['name']) # Artist Name
        track_names.append(personal_data[0]['items'][i]['track']['name']) # Track Name
        popularity_ls.append(personal_data[0]['items'][i]['track']['popularity']) # Track Popularity
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
    print('Success!')
    return df1, personal_data


def recently_played_local_time(main_writer):
    '''
    Add local time to df1
    :param main_writer: excel writer
    :return: df1
    '''
    df1, personal_data = recently_played_data()
# Create empty column to append data to
    df1['local_time'] = ''

    for i in range(len(personal_data[0]['items'])):
        # Convert UTC to local time zone
        utc_time = dateutil.parser.parse(df1['time_palyed'].iloc[i]).astimezone(get_localzone())
        # Format date/time
        local_time = utc_time.strftime('%Y-%m-%d %H:%M:%S')
        local_time

        df1['local_time'].iloc[i] = local_time
        # Write to Excel

        df1.to_excel(main_writer, 'recently_played')
    df1.head()

    return df1

def user_top_played(auth_token):
    '''
    Gather user's top 50 played tracks for the past 6 months
    :param auth_token: authentication token needed to access Spotify's api
    :return: df1, top_track_data
    '''

    df1 = recently_played_local_time(main_writer)
    base_url = 'https://api.spotify.com/v1/me/top/tracks?'
    # track_id = '6y0igZArWVi6Iz0rj35c1Y'

    # 2. Authentication
    # 3. Parameters -- would be stored with authentication
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }

    # 4. Create an empty list
    top_track_data = []  # would be good explore how to capture data at different points in time
    r = requests.get(base_url + "time_range=medium_term" + "&&limit=50", headers=headers)
    top_track_data.append(json.loads(r.text))
    return df1, top_track_data


def user_top_played_clean(main_writer):
    '''
    Parse out user_top_played json and load into a df
    :param main_writer:
    :return: df1, df2
    '''

    df1, top_track_data = user_top_played(auth_token)

    track_idss = []
    album_idss = []
    artist_idss = []
    album_namess = []
    album_relase_datess = []
    artist_namess = []
    popularity_lss = []
    track_namess = []

    print(f"Okay {name_of_user}, let's now pull your top 50 tracks from the last 6 months...")

    for i in tqdm(range(len(top_track_data[0]['items']))):
        track_idss.append(top_track_data[0]['items'][i]['id'])  # Track ID
        album_idss.append(top_track_data[0]['items'][i]['album']['id'])  # Album ID
        artist_idss.append(top_track_data[0]['items'][i]['album']['artists'][0]['id'])
        album_namess.append(top_track_data[0]['items'][i]['album']['name'])  # Album Name
        album_relase_datess.append(top_track_data[0]['items'][i]['album']['release_date'])
        artist_namess.append(top_track_data[0]['items'][i]['album']['artists'][0]['name'])  # Artist Name
        popularity_lss.append(top_track_data[0]['items'][i]['popularity'])
        track_namess.append(top_track_data[0]['items'][i]['name'])  # Track Name

    list_dic2 = {'track_id': track_idss,
                 'album_id': album_idss,
                 'artist_id': artist_idss,
                 'track_name': track_namess,
                 'album_name': album_namess,
                 'artist_name': artist_namess,
                 'track_popularity': popularity_lss,
                 'album_relase_date': album_relase_datess,
                 }
    df2 = pd.DataFrame(list_dic2)
    df2.to_excel(main_writer, 'user_top_played')

    print('Success!')
    return df1, df2


def track_info(main_writer):
    '''
    Pull track data from df2
    :param main_writer: Excel writer
    :return: df1, df2, track_df
    '''

    df1, df2 = user_top_played_clean(main_writer)

    # Create list of track_ids
    track_id_ls = df2['track_id'].tolist()

    track_data = []

    print("Gathering track data...")
    for id in track_id_ls:
        base_url = f'https://api.spotify.com/v1/audio-features/{id}?'

        # 2. Authentication
        # 3. Parameters -- would be stored with authentication
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        r = requests.get(base_url, headers=headers)
        track_data.append(json.loads(r.text))

        track_df = pd.json_normalize(track_data)
        track_df.to_excel(main_writer, 'track_data')
    return df1, df2, track_df


def artist_info():
    '''
    Pull artist data from df2
    :return: df1, df2, track_df, artist_data
    '''

    df1, df2, track_df = track_info(main_writer)
    # Creating a uniqe list artist ids
    artist_id_ls = df2['artist_id'].tolist()
    artist_id_ls = list(dict.fromkeys(artist_id_ls))

    artist_data = []

    for a_id in artist_id_ls:
        base_url = f'https://api.spotify.com/v1/artists/{a_id}?'
        # example artist_id = '06HL4z0CvFAxyc27GXpf02'

        # 2. Authentication
        # 3. Parameters -- would be stored with authentication
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }

        # 4. Create an empty list
        r = requests.get(base_url, headers=headers)
        artist_data.append(json.loads(r.text))

    return df1, df2, track_df, artist_data


def artist_info_clean(main_writer):
    df1, df2, track_df, artist_data = artist_info()

    artist_id_ls = []
    artist_followers_ls = []
    artist_genres_ls = []
    artist_name_ls = []
    artist_popularity_ls = []

    print("Grabbing artist data...")
    for i in tqdm(range(len(artist_data))):
        artist_id_ls.append(artist_data[i]['id'])
        artist_followers_ls.append(artist_data[i]['followers']['total'])
        artist_name_ls.append(artist_data[i]['name'])
        artist_popularity_ls.append(artist_data[i]['popularity'])

        if len(artist_data[i]['genres']) > 0:
            artist_genres_ls.append(artist_data[i]['genres'][0])
        else:
            artist_genres_ls.append('not listed')

    list_dic3 = {'artist_id': artist_id_ls,
                 'artist_followers': artist_followers_ls,
                 'artist_genres': artist_genres_ls,
                 'artist_name': artist_name_ls,
                 'artist_popularity': artist_popularity_ls
                 }
    artist_df = pd.DataFrame(list_dic3)
    artist_df.to_excel(main_writer, 'artist_data')
    print("Success!")
    return df1, df2, track_df, artist_df


def data_to_excel(export_file_path):
    '''
    Pull all sheets together, format the cell width for each seet, and export into 1 excel file
    :param export_file_path: file path to excel file
    :return: N/A
    '''
    print("Writing data to Excel...")
    df1, df2, track_df, artist_df = artist_info_clean(main_writer)

    # list of sheet names
    sheet_lists = ['recently_played', 'user_top_played', 'track_data', 'artist_data']
    df_lists = [df1, df2, track_df, artist_df]

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer1 = pd.ExcelWriter(export_file_path, engine='xlsxwriter')

    for df_name, sheet_name in zip(df_lists, sheet_lists):

        # Convert the dataframe to an XlsxWriter Excel object.
        df_name.to_excel(writer1, sheet_name, index=False)

        # Get the xlsxwriter workbook and worksheet objects.
        workbook = writer1.book
        worksheet = writer1.sheets[sheet_name]

        for i, col in enumerate(df_name.columns):
            # find length of column i
            column_len = df_name[col].astype(str).str.len().max()
            # Setting the length if the column header is larger
            # than the max column value length
            column_len = max(column_len, len(col)) + 2

            # set the column length
            worksheet.set_column(i, i, column_len)

    writer1.save()
    print(f"Process complete; See {export_file_path} for details.")

data_to_excel(export_file_path)