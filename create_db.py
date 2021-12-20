import mysql.connector

DB_NAME='smart_seats'

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="aiotlab208",
    auth_plugin='mysql_native_password')

my_cursor = mydb.cursor()

try:
    my_cursor.execute(f"CREATE DATABASE {DB_NAME}")
except:
    print(f"database {DB_NAME} exist!")

my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
    print(db[0])