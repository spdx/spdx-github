import subprocess
import json
from flask import jsonify
import requests

def run_remote_scan(url, output_file):
    data3 = json.dumps({'url': url})

    r = requests.post('http://localhost:5000/', data = data3)

    parsed_data = json.loads(r.text)
    spdx_file = requests.get('http://localhost:8000/' + parsed_data['filename'])
    fo = open(output_file, "w+")
    fo.write(spdx_file.text)
    fo.close()
