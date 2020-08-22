import asyncio
import json
import random

from mysql.connector import connect
import websockets

it = 0
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
data2 = {'country': '', 'animal': '', 'job': '', 'name': '', 'color': ''}


def foo(user):
    global letter
    global response
    mycursor.execute('SELECT ' + ', '.join(
        [f'(SELECT value FROM {key} WHERE value LIKE "{letter}%" ORDER BY RAND() LIMIT 1)' for key in data2.keys()]))
    response['example'] = dict(zip(data2.keys(), mycursor.fetchone()))
    return user.send(json.dumps(response))


async def counter(websocket, _):
    global letter
    global it
    global response
    try:
        async for message in websocket:
            data = json.loads(message)
            if 'login' in data:
                logins[websocket] = data['login']
                it += 1
                if it > 0:
                    it = 0
                    await asyncio.wait([foo(user) for user in logins.keys()])
            else:
                login = logins[websocket]
                responses[login] = data
                mycursor.execute('SELECT ' + ', '.join(
                    [f'(SELECT value FROM {key} WHERE value="{value}")' for key, value in data.items()]))
                valid[login] = dict(zip(data.keys(), [i is not None for i in mycursor.fetchone()]))

                it += 1
                if it > 0:
                    it = 0
                    score = ''
                    letter = chr(random.randint(65, 90))
                    response = {'responses': '', 'letter': letter}
                    for actualKey, actualFields in responses.items():
                        others = [fields for key, fields in responses.items() if key != actualKey]
                        points = {name: 0 if not valid[actualKey][name] else (
                            10 if value in [other[name] for other in others] else 15) for name, value in
                                  actualFields.items()}
                        response['responses'] += f'<tr><td>{actualKey}</td><td' + \
                                                 '</td><td'.join(
                                                     [f' name="{name}" class="c{val}">{actualFields[name]}'
                                                      for name, val in points.items()]) + \
                                                 '</td></tr>'
                    responses.clear()
                    valid.clear()

                    await asyncio.wait([foo(user) for user in logins.keys()])
    finally:
        del logins[websocket]


asyncio.get_event_loop().run_until_complete(
    websockets.serve(counter, 'localhost', 6789))
asyncio.get_event_loop().run_forever()
