import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE join_queue
          (id INTEGER PRIMARY KEY ASC,
           trace_id VARCHAR(250) NOT NULL,
           user_id VARCHAR(250) NOT NULL,
           username VARCHAR(250) NOT NULL,
           game VARCHAR(250) NOT NULL,
           account_age_days INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL)
         ''') 

c.execute('''
          CREATE TABLE add_friend
          (id INTEGER PRIMARY KEY ASC,
           trace_id VARCHAR(250) NOT NULL,
           source_user_id VARCHAR(250) NOT NULL,
           source_number_of_friends INTEGER NOT NULL,
           friend_user_id VARCHAR(250) NOT NULL,
           friend_number_of_friends INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL)
         ''') 

conn.commit()
conn.close()
