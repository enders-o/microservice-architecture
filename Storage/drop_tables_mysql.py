import mysql.connector

db_conn = mysql.connector.connect(host=DB_HOST, user="user", password=DB_PASS, database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
                  DROP TABLE join_queue, add_friend
                  ''')
db_cursor.execute('''
                  DROP DATABASE events 
                  ''')
db_conn.commit()
db_conn.close()
