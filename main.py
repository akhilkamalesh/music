import spotify_methods as sm
import pandas as pd
import time


if __name__ == "__main__":

    token = sm.get_token()

    df = sm.get_playlists(token, "0E3pYi2fqyFS63EDt7uSMm")
    print(df.head())

    print('done with creation of df')

    time.sleep(10)
    print('starting audio analysis\n')

    sm.get_track_audio_features(token, df, './data/spotify_data_smaller.csv')