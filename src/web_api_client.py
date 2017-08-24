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

import subprocess
import json
from flask import jsonify
import requests
from time import sleep

#This client interfaces with the web api to run a
#scan remotely using spdx-github
def run_remote_scan(url, output_file, scanner):
    from spdx_github import repo_scan
    #Get the url location of the web API using the environment file.
    env_path = repo_scan.find_file_location('../', 'environment.yml')
    environment = repo_scan.get_config_yml(env_path, 'environment.yml')

    api_url = environment[scanner]
    download_url = environment['{}_download'.format(scanner)]

    #Prepare the post data to request beginning the scan
    request_data = json.dumps({'url': url})

    #request a scan to begin and record the status returned
    r = requests.post('{}StartScan'.format(api_url), data = request_data)
    print(r)
    parsed_data = json.loads(r.text)
    status = parsed_data['status']

    #If we got back invalid url, we cannot scan
    if(status == 'invalid-url'):
        print('url was invalid!  Cannot begin scan.')
    else:
        #While the scan is not complete, request a status update
        #every 5 minutes.
        while(status != 'complete'):
            print('scan is in progress')
            sleep(60)
            print('{}TaskStatus/{}'.format(api_url, parsed_data['id']))
            r = requests.get('{}TaskStatus/{}'.format(api_url,
                                                      parsed_data['id']))
            print('r', r)
            status_response = json.loads(r.text)
            status = status_response['status']
            if(status == 'scan-failed'):
                break

        if(status != 'scan-failed'):
            #once the scan is complete, download the file and write it to the
            #correct file name.
            print('scan is complete')
            spdx_file = requests.get('{}{}.spdx'.format(download_url,
                                     parsed_data['id']))
            fo = open(output_file, 'w+')
            fo.write(spdx_file.text)
            fo.close()
        else:
            print('scan failed')
