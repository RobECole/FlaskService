from flask import Flask
import json
import psycopg2
app = Flask(__name__)

tasks = [
    {
        "description": "Milk, Cheese, Pizza, Fruit, Tylenol",
        "done": False,
        "id": 1,
        "title": "Buy groceries"
    },
    {
        'id': 2,
        'title': 'Learn Python',
        'description': 'Need to find a good Python tutorial on the web',
        'done': False
    }
]
@app.route('/api/test', methods=['GET'])
def test():
    return json.dumps(tasks)

@app.route('/api/freeChamps', methods=['GET'])
def freechamps():
    connect.cursor.execute("SELECT CN.Name FROM LEAGUE.CHAMPION AS C RIGHT JOIN LEAGUE.CHAMPNAME AS CN ON CN.ID = C.Champ_id WHERE Free_to_play = 'true'")
    record = connect.cursor.fetchall()
    print record
    return json.dumps(record)


class connect():

    conn_string = "host='localhost' dbname='LEAGUE_CIRCUIT' user='postgres' password='testdb'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

if __name__ == '__main__':
    app.run(port=5001, debug=True)
