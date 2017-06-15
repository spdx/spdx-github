from flask import Flask, request
import download_repo_run_scan
import json

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def github_webhooks():
    if request.method == 'POST':
        data = request.data
        parsed_data = json.loads(data)
        zipball = 'https://api.github.com/repos/' + 
                  parsed_data['repository']['full_name'] + '/zipball'
        download_repo_run_scan.download_repo_run_scan(zipball)
        return "Post"
    else:
        return "Get"

if __name__ == "__main__":
    app.run()
