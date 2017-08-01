#!flask/bin/python
from flask import Flask, request, jsonify
import json
from spdx_github import repo_scan
import SimpleHTTPServer
import SocketServer
from os import path
import threading

app = Flask(__name__)

#Threading part of this code based on
#https://stackoverflow.com/questions/37141696/how-to-send-asynchronous-request-using-flask-to-an-endpoint-with-small-timeout-s

@app.route('/StartScan', methods=['GET','POST'])
def start_scan():
    fo = open('./last_id', "r+")
    task_id = fo.read()
    fo.close()

    data = request.data
    parsed_data = json.loads(data)
    
    if(repo_scan.check_valid_url(parsed_data['url']) == False):
        response = app.response_class(
            response=json.dumps({'id': task_id, 'status': 'invalid-url'}),
            status=200,
            mimetype='application/json'
        ) 
        return response       

    async_task = run_new_scan(task_id=task_id, url=parsed_data['url'])
    async_task.start()
    response = app.response_class(
        response=json.dumps({'id': task_id, 'status': 'starting-scan'}),
        status=200,
        mimetype='application/json'
    )

    task_id = int(task_id) + 1
    fo = open('./last_id', "w+")
    fo.write(str(task_id))
    fo.close()
    return response

@app.route('/TaskStatus/<int:task_id>')
def task_status(task_id):
    if(path.isfile('./file_server/' + str(task_id) + '.spdx')):
        response = app.response_class(
            response=json.dumps({'status': 'complete'}),
            status=200,
            mimetype='application/json'
        )
    elif(path.isfile('./file_server/' + str(task_id) + '.fail')):
        response = app.response_class(
            response=json.dumps({'status': 'scan-failed'}),
            status=200,
            mimetype='application/json'
        )        
    else:
        response = app.response_class(
            response=json.dumps({'status': 'in-progress'}),
            status=200,
            mimetype='application/json'
        )            
    return response       

class run_new_scan(threading.Thread):
    def __init__(self, task_id, url):
        threading.Thread.__init__(self)
        self.task_id = task_id
        self.url = url
    def run(self):
        result = repo_scan.repo_scan(self.url, True, self.task_id)
        if(result == 'Scan Failed'):
            fo = open(self.task_id + '.fail', "w+")
            fo.write('Scan Failed')
            fo.close()            

if __name__ == '__main__':
    app.run(debug=True)
