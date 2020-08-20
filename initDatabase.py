import mysql.connector
import re

files = ('name','animal','color','country','job')
            
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd=""
)
mycursor = mydb.cursor()
mycursor.execute('DROP DATABASE IF EXISTS panstwamiasta')
mycursor.execute('CREATE DATABASE panstwamiasta')
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="panstwamiasta"
)
mycursor = mydb.cursor()
for file in files:
    with open(file+'.txt',"r") as f:
        mycursor.execute(f"CREATE TABLE {file} (value VARCHAR({len(max(f, key=len).strip())}))")
    mycursor.execute(f"LOAD DATA LOCAL INFILE '{file}.txt' INTO TABLE {file}")
    #with open(file+'.txt',"r") as f:
    #    mycursor.executemany("INSERT INTO %s VALUES "%file + "(%s)", [(line.strip(),) for line in f])
 
mydb.commit()
