import sqlite3
import os

class Database(object):

	def __init__(self, fname='./data/music_data.db'):

		self.dbfname = fname
		self.sDatabase = sqlite3.connect(self.dbfname)
		self.makeDBPublic()
		self.dbcursor = self.sDatabase.cursor()

		self.sDatabase.commit()
		self.sDatabase.close()


	def list_all_records(self, table_name='api_pulls'):

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute(f'SELECT * FROM {table_name}')
		records = self.dbcursor.fetchall()
		self.dbcursor.close()
		return records

	def delete_record(self, id, table_name):

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute(f'DELETE FROM {table_name} WHERE id=?', (id, ))
		self.sDatabase.commit()
		self.dbcursor.close()

	def fetch_row_from_id(self, value):

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		try:
			self.dbcursor.execute(
				"SELECT * FROM api_pulls WHERE id=?",\
				(value, )
				)

			fetchedRow = self.dbcursor.fetchone()
			self.dbcursor.close()
			return fetchedRow

		except:

			print('Unable to fetch row')

	def fetch_last_row(self, table_name):
		 
		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		try:
			self.dbcursor.execute(
				f"SELECT * FROM {table_name} ORDER BY id DESC"
			)

			fetchedRow = self.dbcursor.fetchone()
			fetchedRow = self.dbcursor.fetchone()
			self.dbcursor.close()
			return fetchedRow

		except:

			print('Unable to fetch row')

	def makeDBPublic(self):

		os.popen("chmod -R 777 %s" % (self.dbfname))

class Modify_Database(Database):

	def __init__(self):
		super(Modify_Database, self).__init__()

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute(
			"CREATE TABLE IF NOT EXISTS api_pulls\
			( id INTEGER PRIMARY KEY,\
			  json_content JSON,\
			  time_pulled TIMESTAMP\
			)"
		)

		self.dbcursor.execute(
			"CREATE TABLE IF NOT EXISTS track_playback\
			(\
				id INTEGER PRIMARY KEY,\
				track_id VARCHAR(22),\
				track_name TEXT,\
				artist_id VARCHAR(22),\
				artist_name TEXT,\
				genre TEXT,\
				album_id VARCHAR(22),\
				album_name TEXT,\
				album_release DATE,\
				played_at DATE\
			)"
		)

		self.dbcursor.execute(
			"CREATE TABLE IF NOT EXISTS playback_counts\
			( id INTEGER PRIMARY KEY,\
			  track_id VARCHAR(22),\
			  track_name TEXT,\
			  playbacks INTEGER\
			)"
		)

		self.dbcursor.execute(
			"CREATE TABLE IF NOT EXISTS playback_counts_sorted\
			( id INTEGER PRIMARY KEY,\
			  track_id VARCHAR(22),\
			  track_name TEXT,\
			  playbacks INTEGER\
			)"
		)

		self.dbcursor.execute(
			"CREATE TABLE IF NOT EXISTS favorite_tracks\
			(\
				id INTEGER PRIMARY KEY,\
				track_id VARCHAR(22),\
				track_name TEXT,\
				date_added DATE\
			)"
		)
		
		self.sDatabase.commit()
		self.sDatabase.close()

	def add_music_data(self, music_data='', time_pulled=''):

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute(
			"INSERT INTO api_pulls(json_content, time_pulled)\
			 VALUES (?, ?)"\
			,(music_data, time_pulled)
		)

		self.sDatabase.commit()
		self.sDatabase.close()

	def sort_table(self, table_name, target_name):

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute(f'DELETE FROM {target_name}')

		self.dbcursor.execute(
			f"INSERT INTO `{target_name}`(`track_id`, `track_name`, `playbacks`)\
			SELECT `track_id`, `track_name`, `playbacks` FROM `{table_name}` ORDER BY `playbacks` DESC"
		)


		self.sDatabase.commit()
		self.sDatabase.close()

	def add_song_data(self, song_name, times_played, song_id):

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute(
			"SELECT * from playback_counts WHERE track_name=?", (song_name, )
		)

		if len(self.dbcursor.fetchall()) < 1:
			
			self.dbcursor.execute(
				"INSERT INTO playback_counts(track_id, track_name, playbacks)\
				 VALUES (?, ?, ?)"\
				 ,(song_id, song_name, times_played)
			)

		else:
			self.dbcursor.execute('UPDATE playback_counts set playbacks=playbacks+?\
							WHERE track_name=?',\
							(times_played, song_name))

		self.sDatabase.commit()
		self.dbcursor.close()

	def list_all_json(self):
		
		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute("SELECT json_content FROM api_pulls")
		records = self.dbcursor.fetchall()

		return records

	def update_json_record(self, songID, song_data='', time_pulled=''):

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute('UPDATE api_pulls set json_content=?, time_pulled=?\
							WHERE id=?',\
							(song_data, time_pulled, songID))

		self.sDatabase.commit()
		self.dbcursor.close()

	def find_track(self, timestamp):

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute("SELECT * FROM track_playback WHERE played_at=?", (timestamp, ))

		records = self.dbcursor.fetchall()

		return records
	
	def add_track(self, t_name, t_id, ar_name, ar_id, genre, al_name, al_id, al_date, played_at):
		
		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()
		
		self.dbcursor.execute(
				"INSERT INTO track_playback(track_id, track_name, artist_id, artist_name, genre, album_id, album_name, album_release, played_at)\
				 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"\
				 ,(t_id, t_name, ar_id, ar_name, genre, al_id, al_name, al_date, played_at)
			)

		self.sDatabase.commit()
		self.dbcursor.close()

	def add_favorite_data(self, t_id, t_name, date_added):

		self.sDatabase = sqlite3.connect(self.dbfname)
		self.dbcursor = self.sDatabase.cursor()

		self.dbcursor.execute(
			"INSERT INTO favorite_tracks(track_id, track_name, date_added)\
			 VALUES (?, ?, ?)"\
			,(t_id, t_name, date_added)
		)

		self.sDatabase.commit()
		self.dbcursor.close()