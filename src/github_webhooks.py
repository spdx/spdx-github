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

import json

from flask import Flask, request

import repo_scan

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def github_webhooks():
    if request.method == 'POST':
        data = request.data
        parsed_data = json.loads(data)
        zipball = 'https://api.github.com/repos/' +
                  parsed_data['repository']['full_name'] + '/zipball'
        repo_scan.repo_scan(zipball)
        return "Post"
    else:
        return "Get"

if __name__ == "__main__":
    app.run()
