#!flask/bin/python
from flask import Flask, request, jsonify
import json
from spdx_github import repo_scan
import SimpleHTTPServer
import SocketServer

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    data = request.data
    parsed_data = json.loads(data)
    file_name = repo_scan.repo_scan(parsed_data['url'], True)
    response = app.response_class(
        response=json.dumps({'filename': file_name}),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    app.run(debug=True)
