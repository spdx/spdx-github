import subprocess
import json
from flask import jsonify
import requests
from time import sleep

def run_remote_scan(url, output_file):
    request_data = json.dumps({'url': url})

    r = requests.post('http://localhost:5000/', data = request_data)
    print(r)
    parsed_data = json.loads(r.text)
    status = 'in-progress'

    while(status != 'complete'):
        print('scan is in progress')
        sleep(300)
        r = requests.get('http://localhost:5000/TaskStatus/' + parsed_data['id'])
        print('r', r)
        status_response = json.loads(r.text)
        status = status_response['status']

    print('scan is complete')
    spdx_file = requests.get('http://localhost:8000/' + parsed_data['id'] + '.spdx')
    fo = open(output_file, "w+")
    fo.write(spdx_file.text)
    fo.close()
