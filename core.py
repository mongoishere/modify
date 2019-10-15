import sys
from exts.database import Modify_Database
from exts.logger import Logger
from exts.sorter import Sorter
from exts.caller import Caller, json
from datetime import datetime

class Modify(object):

    def __init__(self):  
        
        self.modify_caller = Caller() # For making calls to the Spotify API
        self.modify_database = Modify_Database() # For interfacing with the Modify SQL Database
        self.modify_sorter = Sorter() # For sorting...will elaborate later
        self.modify_logger = Logger("modify") # For logging modify information
        self.modify_logger.debug("Refreshing Access Token...")
        self.access_token = self.modify_caller.refreshToken() # For accessing Spotify endpoints
        self.modify_logger.debug("Importing modify_data.json...")
        with open('data/modify_data.json') as f:
            self.modify_data = json.load(f)
            self.modify_logger.debug("Successfully imported modify_data.json")

    def retrieve_recent_songs(self):

        self.modify_logger.debug("Retrieving Recent Songs")
        newest_songs = self.modify_caller.makeCall("https://api.spotify.com/v1/me/player/recently-played", self.access_token)
        
        # Adds exception in case database is empty

        if(self.modify_database.fetch_last_row('./data/music_data')):
            recent_songs = self.modify_database.fetch_last_row('./data/music_data')[-2]
            new_song = self.modify_sorter.compare_recent(recent_songs, newest_songs)
        else: new_song = True

        if not(new_song): return None
        self.modify_logger.debug("Adding Music Data")
        self.modify_database.add_music_data(newest_songs, datetime.now())

        return True
    
    def modify_playlist(self):

        # If no new_songs have been added then exit function

        playlist_ext = False
        playlist_offset = 0
        
        if not(self.retrieve_recent_songs()): self.modify_logger.debug("Songs lists match, exiting..."); return None

        user_playlists = self.modify_caller.makeCall("https://api.spotify.com/v1/me/playlists", self.access_token)
        
        target_playlists, playlist_ext = self.modify_sorter.findtargetPlaylists(user_playlists, True)

        while not(self.modify_sorter.target_playlists == [*target_playlists]) and (playlist_ext):
            playlist_offset += 1
            print('Extending playlist search')
            #import pdb; pdb.set_trace(header='Retrying')
            user_playlists = self.modify_caller.makeCall(f'https://api.spotify.com/v1/me/playlists?offset={playlist_offset*20}', self.access_token)
            targets_found, playlist_ext = self.modify_sorter.findtargetPlaylists(user_playlists, True)
            target_playlists.update(targets_found)

        all_records = self.modify_database.list_all_records()
        
        record_songs = self.modify_sorter.findSongs(all_records[-1][1])

        #import pdb; pdb.set_trace()

        record_songs = self.modify_sorter.findtopSongs(record_songs)


        self.modify_logger.debug('Adding Song Playback Data')
        for song in record_songs:
            self.modify_logger.debug(f"Adding {song}...")
            #import pdb; pdb.set_trace()
            self.modify_database.add_song_data(
                " ".join(song[0].split(":")[:-1]),
                song[1], song[0].split(":")[-1]
            )

        self.modify_database.sort_table('playback_counts', 'playback_counts_sorted')

        all_records = self.modify_database.list_all_records('playback_counts_sorted')

        playlist_edits = {}
        playlist_tracks = {}

        for k in target_playlists: playlist_edits[k] = 0

        for playlist_name, playlist_id in target_playlists.items():
            deductable, iterable = 2, 0
            playlist_tracks[playlist_name] = []
            temp_string, track_info = [], []
            while True:       
                tracks_json = self.modify_caller.makeCall(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={iterable*100}", self.access_token)
                track_info.append(self.modify_sorter.findSongs(tracks_json))
                temp_string += self.modify_sorter.findSongs(tracks_json)
                if len(temp_string) == (iterable+1)*100: iterable += 1
                else: break
            temp_string = None

            for track_list in (track_info):
                playlist_tracks[playlist_name] += track_list
                
        #import pdb; pdb.set_trace()

        for song in all_records:
            for playlist_name, playlist_id in target_playlists.items():
                
                track_target = f"{song[2]}:{song[1]}"
                
                if (track_target in playlist_tracks[playlist_name]):
                    
                    songTarget_index = playlist_tracks[playlist_name].index(f"{song[2]}:{song[1]}")
                    reorder_data = {
                        'range_start': songTarget_index,
                        'insert_before': playlist_edits[playlist_name]
                    }
                    playlist_edits[playlist_name]+=1
                    self.modify_logger.debug(f"{playlist_edits[playlist_name]} change(s) to {playlist_name} for {song}")
                    
                    call_response = self.modify_caller.makeCall(
                        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
                        self.access_token,
                        data=reorder_data,
                        method='PUT'
                    )
        self.modify_logger.debug("Finished Modifying Playlists")

    def create_track_data(self, dbname='./data/music_data.db'):

        json_bundle = self.modify_database.list_all_json()

        for json_log in json_bundle:

            songs_json = json.loads(json_log[0])
            for item in songs_json['items']:
                track_name = item['track']['name']
                track_uri = item['track']['uri'].split(':')[-1]
                track_artist, artist_uri = [], []
                album_name = item['track']['album']['name']
                album_uri = item['track']['album']['uri'].split(':')[-1]
                album_release = item['track']['album']['release_date']
                played_at = item['played_at']

                for artist in item['track']['artists']:
                    track_artist.append(artist['name'])
                    artist_uri.append(artist['uri'].split(':')[-1])
                    

                track_artist = ', '.join(track_artist)
                artist_uri = ', '.join(artist_uri)


                if not self.modify_database.find_track(played_at):
                    self.modify_database.add_track(
                        track_name,
                        track_uri,
                        track_artist,
                        artist_uri,
                        self.find_genre(track_uri),
                        album_name,
                        album_uri,
                        album_release,
                        played_at
                    )
                #print(track_uri)
                #import pdb; pdb.set_trace()

    def get_favorites(self):

        self.modify_logger.debug('Retrieving favorite songs list...')
        
        favorite_songs = self.modify_sorter.findSongs(self.modify_caller.makeCall("https://api.spotify.com/v1/me/tracks", self.access_token))
        times_added = self.modify_sorter.findtimeAdded(self.modify_caller.makeCall("https://api.spotify.com/v1/me/tracks", self.access_token))

        for i in range(50):

            self.modify_logger.debug(f'Retrieving favorites list (iteration: {i+1})')
            favorite_raw = self.modify_caller.makeCall(f"https://api.spotify.com/v1/me/tracks?offset={(i+1)*20}", self.access_token)
            
            favorite_json = json.loads(favorite_raw)
            if len(favorite_json['items']) <= 0: print('breaking'); break

            favorite_songs += self.modify_sorter.findSongs(favorite_json)
            times_added += self.modify_sorter.findtimeAdded(favorite_json)

        for i in range(len(favorite_songs)):

            self.modify_database.add_favorite_data(
                favorite_songs[i].split(':')[-1],
                favorite_songs[i].split(':')[0],
                times_added[i]
            )
            #import pdb; pdb.set_trace(header='Database Break')

        #import pdb; pdb.set_trace()

    def find_genre(self, track_id):

        genre_seeds = self.modify_data['genres']

        track_info = self.modify_caller.makeCall(f"https://api.spotify.com/v1/tracks/{track_id}", self.access_token)
        track_info = json.loads(track_info)

        artist_id = track_info['album']['artists'][0]['id']

        artist_info = self.modify_caller.makeCall(f"https://api.spotify.com/v1/artists/{artist_id}", self.access_token)
        artist_info = json.loads(artist_info)

        artist_genres = artist_info['genres']
        
        matched_genres = [genre for genre in genre_seeds if genre in artist_genres]
        
        matched_genres = ', '.join(matched_genres)

        #import pdb; pdb.set_trace()

        return matched_genres

    def pull_playlists(self):

        # Populate playlist_pulls table
        playlist_json = self.modify_caller.makeCall('https://api.spotify.com/v1/me/playlists', self.access_token)
        #self.modify_sorter.findPlaylists(playlist_json, self.modify_data['playlists'])

        
        import pdb; pdb.set_trace()


if __name__ == '__main__':
    
    app = Modify()
    #app.pull_playlists()
    app.get_favorites
    app.modify_playlist()
    app.create_track_data()
    #app.get_favorites()