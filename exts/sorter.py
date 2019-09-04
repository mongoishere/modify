import json
from collections import Counter

class Sorter(object):

    def __init__(self):
        
        # These are playlists that are to be edited, this can be changed
        from configparser import ConfigParser; config = ConfigParser(); \
            config.read('config.ini'); \
            self.target_playlists = config.get('Settings', 'TargetPlaylists')

        self.target_playlists = self.target_playlists.split(',')
        self.target_playlists = [x.strip() for x in self.target_playlists]

    def findtargetPlaylists(self, playlist_json):

        found_playlists = {}

        if(isinstance(playlist_json, (str, bytes))): playlist_json = json.loads(playlist_json)

        for item in playlist_json['items']:
            if item['name'] in self.target_playlists: found_playlists[item['name']] = item['id']
        
        return(found_playlists)

    def findSongs(self, recent_json):

        recent_songs = []
        if(isinstance(recent_json, (str, bytes))): recent_json = json.loads(recent_json)
        for item in recent_json['items']: recent_songs.append(f"{item['track']['name']}:{item['track']['id']}")
        return(recent_songs)

    def findtopSongs(self, songs_list):

        listened_songs = []
        for vector in songs_list: listened_songs.append(vector)
        song_counter = Counter(listened_songs)
        top_songs = sorted(song_counter, key=lambda x: -song_counter[x])
        songs_counted = song_counter.most_common()
        return(songs_counted)

    def findtimeAdded(self, playlist_json):
        
        if(isinstance(playlist_json, (str, bytes))): playlist_json = json.loads(playlist_json)
        elif(isinstance(playlist_json, dict)): pass
        else: return

        timestamp_list = [item['added_at'] for item in playlist_json['items']]
        return(timestamp_list)

    def compare_recent(self, recent_json, new_json):

        new_songs = self.findSongs(new_json)
        recent_songs = self.findSongs(recent_json)
        return not(new_songs == recent_songs)
