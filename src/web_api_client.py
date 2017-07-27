import subprocess
import json
from flask import jsonify
import requests
from time import sleep

def run_remote_scan(url, output_file, scanner):
    from spdx_github import repo_scan
    env_path = repo_scan.find_file_location('../', 'environment.yml')
    environment = repo_scan.get_config_yml(env_path, 'environment.yml')

    api_url = environment[scanner]
    download_url = environment[scanner + '_download']

    request_data = json.dumps({'url': url})

    r = requests.post(api_url + 'StartScan', data = request_data)
    print(r)
    parsed_data = json.loads(r.text)
    status = 'in-progress'

    while(status != 'complete'):
        print('scan is in progress')
        sleep(60)
        print(api_url + 'TaskStatus/' + parsed_data['id'])
        r = requests.get(api_url + 'TaskStatus/' + parsed_data['id'])
        print('r', r)
        status_response = json.loads(r.text)
        status = status_response['status']

    print('scan is complete')
    spdx_file = requests.get(download_url + parsed_data['id'] + '.spdx')
    fo = open(output_file, "w+")
    fo.write(spdx_file.text)
    fo.close()
