import asyncio
import json
import random

from mysql.connector import connect
import websockets

letter = chr(random.randint(65, 90))
response = {'responses': '', 'letter': letter}
responses = {}
valid = {}
logins = {}
mydb = connect(
    host='localhost',
    user='root',
    passwd='root',
    database='panstwamiasta'
)
mycursor = mydb.cursor()
fieldNames = ('country', 'animal', 'job', 'name', 'color')


def cheat_move(user):
    global letter
    global response
    mycursor.execute('SELECT ' + ', '.join(
        [f'(SELECT value '
         f'FROM {key} '
         f'WHERE value LIKE "{letter}%" '
         f'ORDER BY RAND() '
         f'LIMIT 1)'
         for key in fieldNames]))
    response['example'] = dict(
        zip(fieldNames, mycursor.fetchone())
    )
    return user.send(json.dumps(response))

def changeLetter():
    global letter
    letter = chr(random.randint(65, 90))

async def counter(websocket, _):
    global letter
    global response
    global logins
    try:
        async for message in websocket:
            data = json.loads(message)
            if 'login' in data:
                logins[websocket] = data['login']
                if len(logins) > 0: # Enough players, start the game
                    await asyncio.wait(
                        map(cheat_move, logins.keys())
                    )
            else:
                login = logins[websocket]
                responses[login] = data
                mycursor.execute('SELECT ' + ', '.join([
                    f'(SELECT value '
                    f'FROM {key} '
                    f'WHERE value="{value}")'
                    for key, value in data.items()
                ]))
                valid[login] = dict(
                    zip(
                        data.keys(),
                        map(bool, mycursor.fetchone())
                    )
                )

                if len(responses) > 0: # Enough responses, end this round and start new one
                    letter = chr(random.randint(65, 90))
                    response = {'responses': '', 'letter': letter}
                    for actualKey, actualFields in responses.items():
                        others = [fields for key, fields in responses.items() if key != actualKey]

                        points = {name:
                                      0 if not valid[actualKey][name] else (
                                          10 if value in (other[name] for other in others)
                                              else 15)
                                  for name, value in
                                  actualFields.items()}
                        response['responses'] += f'<tr><td>{actualKey}</td><td' + \
                                                 '</td><td'.join(
                                                     [f' name="{name}" class="c{val}">{actualFields[name]}'
                                                      for name, val in points.items()]) + \
                                                 '</td></tr>'
                    responses.clear()
                    valid.clear()

                    await asyncio.wait([cheat_move(user) for user in logins.keys()])
                    # await asyncio.wait(list(map(cheat_move, logins.keys())))
    finally:
        del logins[websocket]


asyncio.get_event_loop().run_until_complete(
    websockets.serve(counter, 'localhost', 6789))
asyncio.get_event_loop().run_forever()
