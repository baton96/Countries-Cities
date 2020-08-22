from mysql.connector import connect

files = ('name', 'animal', 'color', 'country', 'job')
conOptions = {'host': 'localhost', 'user': 'root', 'passwd': 'root'}

mydb = connect(**conOptions)
mycursor = mydb.cursor()
mycursor.execute('DROP DATABASE IF EXISTS panstwamiasta')
mycursor.execute('CREATE DATABASE panstwamiasta')

mydb = connect(**conOptions, database='panstwamiasta')
mycursor = mydb.cursor()
for file in files:
    mycursor.execute(f'CREATE TABLE {file} (value VARCHAR(25))')
    with open(file + '.txt', 'r') as f:
        mycursor.executemany(
            f'INSERT INTO {file} VALUES (%s)', [(line.strip(),) for line in f]
        )

mydb.commit()
