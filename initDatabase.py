import mysql.connector
import re
regex = re.compile('[^a-zA-Z ]')
files = ('name','animal','color','country','job')

for file in files:
    with open(file+'.txt',"r") as f:
        mySet = sorted({regex.sub('', line).lower() for line in f})
    with open(file+'.txt',"w") as f:
        for line in mySet:
            f.write(line+"\n")
            
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
        mycursor.execute(f"CREATE TABLE {file} (value VARCHAR({len(max(f,key=len).strip())}))")
    mycursor.execute(f"LOAD DATA LOCAL INFILE '{file}.txt' INTO TABLE {file}")
    ''' 
    with open(file+'.txt',"r") as f:
        mycursor.execute("CREATE TABLE %s (value VARCHAR(%d))"%(file, len(max(f,key=len).strip())))
    with open(file+'.txt',"r") as f:
        mycursor.executemany("INSERT INTO %s VALUES "%file + "(%s)", [(line.strip(),) for line in f])
    ''' 
mydb.commit()
