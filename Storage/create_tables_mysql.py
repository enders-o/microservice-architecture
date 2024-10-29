import mysql.connector

db_conn = mysql.connector.connect(host=DB_HOST, user="user",password=DB_PASS)

db_cursor = db_conn.cursor()

db_cursor.execute('''
                  USE events 
                  ''')

db_cursor.execute('''
          CREATE TABLE join_queue
          (id INT NOT NULL AUTO_INCREMENT,
           trace_id VARCHAR(250) NOT NULL,
           user_id VARCHAR(250) NOT NULL,
           username VARCHAR(250) NOT NULL,
           game VARCHAR(250) NOT NULL,
           account_age_days INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT join_queue_pk PRIMARY KEY (id))
                  ''')

db_cursor.execute('''
          CREATE TABLE add_friend
          (id INT NOT NULL AUTO_INCREMENT,
           trace_id VARCHAR(250) NOT NULL,
           source_user_id VARCHAR(250) NOT NULL,
           source_number_of_friends INTEGER NOT NULL,
           friend_user_id VARCHAR(250) NOT NULL,
           friend_number_of_friends INTEGER NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT add_friend_pk PRIMARY KEY (id))
                  ''')

db_conn.commit()
db_conn.close()
