from flask import Flask, jsonify, abort

app = Flask(__name__)

tasks = [
        {
          "description": "Milk, Cheese, Pizza, Fruit, Tylenol",
          "done": False,
          "id": 1,
          "title": "Buy groceries"
        },
        {
          "description": "Need to find a good Python tutorial on the web",
          "done": False,
          "id": 2,
          "title": "Learn Python"
        }
]

@app.route('/query/<int:task_id>', methods=['GET'])
def get_tasks(task_id):
    task = filter(lambda t: t['id'] == task_id, tasks)
    if len(task) == 0:
        abort(404)
    return jsonify({'tasks': task[0]})


if __name__ == '__main__':
    app.run(debug=True)
