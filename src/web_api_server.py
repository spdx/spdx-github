#!flask/bin/python

# Copyright (c) Anna Buhman.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from flask import Flask, request, jsonify
import json
from spdx_github import repo_scan
import SimpleHTTPServer
import SocketServer
from os import path
import threading

app = Flask(__name__)

#Threading portion of this code based on
#https://stackoverflow.com/questions/37141696/
    #how-to-send-asynchronous-request-using-
    #flask-to-an-endpoint-with-small-timeout-s

#This is for starting a new scan
@app.route('/StartScan', methods=['GET','POST'])
def start_scan():
    #Look at the last id used.  This will be incemented to keep the id
    #unique.
    fo = open('./last_id', "r+")
    task_id = fo.read()
    fo.close()

    #Get the posted API request
    data = request.data
    parsed_data = json.loads(data)

    #If it is not a valid url, respond with invalid url.
    if(repo_scan.check_valid_url(parsed_data['url']) == False):
        response = app.response_class(
            response=json.dumps({'id': task_id, 'status': 'invalid-url'}),
            status=200,
            mimetype='application/json'
        ) 
        return response

    #Start a new scan asynchronously so we can send back a response
    #quickly even if it's a long scan.
    async_task = run_new_scan(task_id=task_id, url=parsed_data['url'])
    async_task.start()
    #Respond that the scan is beginning
    response = app.response_class(
        response=json.dumps({'id': task_id, 'status': 'starting-scan'}),
        status=200,
        mimetype='application/json'
    )

    #Increment the id and write the the id file.
    task_id = int(task_id) + 1
    fo = open('./last_id', "w+")
    fo.write(str(task_id))
    fo.close()

    return response

#This is to give the task status.  It is intended
#to be a get request.  The id is the same id
#returned by the begin scan portion
@app.route('/TaskStatus/<int:task_id>')
def task_status(task_id):
    #If the spdx file has been created, the scan is complete.
    if(path.isfile('./file_server/{}.spdx'.format(str(task_id)))):
        response = app.response_class(
            response=json.dumps({'status': 'complete'}),
            status=200,
            mimetype='application/json'
        )
    #if id.fail file was created, the scan failed.
    elif(path.isfile('./file_server/{}.fail'.format(str(task_id)))):
        response = app.response_class(
            response=json.dumps({'status': 'scan-failed'}),
            status=200,
            mimetype='application/json'
        )
    else:
    #If we have neither succeeded nor failed, we must still be
    #In progress.
        response = app.response_class(
            response=json.dumps({'status': 'in-progress'}),
            status=200,
            mimetype='application/json'
        )
    return response

#Run an asynchronous scan.
class run_new_scan(threading.Thread):
    def __init__(self, task_id, url):
        threading.Thread.__init__(self)
        self.task_id = task_id
        self.url = url
    def run(self):
        result = repo_scan.repo_scan(self.url, True, self.task_id)
        #if we get back that the scan failed, create the .fail file.
        if(result == 'Scan Failed'):
            fo = open('{}.fail'.format(self.task_id), "w+")
            fo.write('Scan Failed')
            fo.close()

if __name__ == '__main__':
    app.run(debug=True)
