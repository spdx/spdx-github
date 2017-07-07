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

#This is an example of downloading a repo zip file,
#unzipping it and running a scan on it.
#The example uses scancode, but dosocsv2 could also be used.

import subprocess
from subprocess import call
import requests
import os
from os import path, remove
import shutil
import zipfile
import sys
import click
import json
import re
from yaml import safe_load, dump
from git import Repo, Actor

@click.command()
@click.option('--url', prompt='The url of the GitHub repo zip file to scan',
              help='The url of the GitHub repo zip file to scan.')

def main(url):
    #The argument is the url of the GitHub zip file
    repo_zip_url = url
    #If the url gives an error, exit
    if(check_valid_url(repo_zip_url) == False):
        sys.exit()
    repo_scan(repo_zip_url)

#This method goes throught the overall process of downloading and scanning a repo.
def repo_scan(repo_zip_url):
    #Download the zip and get its path.
    file_location = download_github_zip(repo_zip_url)
    #Extract the zip and get the path of the extracted directory.
    repo_path = unzip_file(file_location)

    configuration = get_config(repo_path, 'configuration.yml')
    suffix = configuration['output_file_name'][-5:]
    if(suffix != '.SPDX' and suffix != '.spdx'):
        spdx_file_name = configuration['output_file_name'] + '.SPDX'
    else:
        spdx_file_name = configuration['output_file_name']

    environment = get_config('./', 'environment.yml')
    m = re.match(r"https://github.com/(\w+)/(\w+)/",  repo_zip_url)
    if(m):
        main_repo_user = m.group(1)
        repo_name = m.group(2)
    else:
        m = re.match(r"https://api.github.com/repos/(\w+)/(\w+)/zipball", repo_zip_url)
        main_repo_user = m.group(1)
        repo_name = m.group(2)

    repo = Repo.init(repo_path)
    sync_main_repo(repo_path, main_repo_user, repo_name, repo)

    spdx_file_path = repo_path + spdx_file_name

    #Scan the extracted directory and put results in a named file.
    #TODO: check does existing SPDX file affect the scan? it is in the repository.
    scan(repo_path, spdx_file_path, 'scancode',
         configuration['output_type'])

    pull_request_to_github(spdx_file_name, repo_path, configuration, main_repo_user, repo_name, environment, repo)

    #Remove the zip file.
    remove(file_location)
    #Remove the unzipped directory.
    #shutil.rmtree(extracted_directory)

    return spdx_file_name

def scan(directory_to_scan, output_file_name, scanner, output_type):
    if(output_type == 'tag-value'):
        output_format = 'spdx-tv'
    elif(output_type == 'rdf'):
        output_format = 'spdx-rdf'
    #Scan the unzipped directory.
    print subprocess.check_output(['scancode','--format', 
                                  output_format,directory_to_scan,
                                  output_file_name])

#Unzip a zip file and return the path to the extracted directory.
def unzip_file(file_location):
    #Unzip the zip file.
    zip_file = zipfile.ZipFile(file_location, 'r')
    zip_file.extractall()
    #Get the directory that results from unzipping the file
    #(Assume there is only one directory).
    extracted_directory = (zip_file.namelist())[0]
    zip_file.close()
    #Return the path to the extracted directory.
    return extracted_directory

#Download a zip file and return the path of the downloaded file.
def download_github_zip(repo_zip_url):
    #Get a zip file to download.
    to_scan = requests.get(repo_zip_url, stream=True)

    #Get the path to where the zip file will be stored.
    #This is the name of the zip file.
    zip_file_name = repo_zip_url[repo_zip_url.rfind('/')+1:]
    #This is the path to the directory containing the zip file.
    directory_path = os.path.dirname(os.path.realpath(__file__))
    #Concatenate the file name with the path.
    file_location = directory_path + zip_file_name

    #Write the zip file in chunks.
    with open(file_location, 'wb') as fd:
        for chunk in to_scan.iter_content(chunk_size=1024):
            fd.write(chunk)
    #Return the path to the downloaded file.
    return file_location

def get_config(directory, file_name):
    config_file = directory + file_name
    if(path.isfile(config_file)):
        stream = file(config_file, 'r')
        configuration = safe_load(stream)
    else:
        configuration = {}
        configuration['output_file_name'] = directory[:-1] + '.SPDX'
	configuration['output_type'] = 'tag-value'
    return configuration

def sync_main_repo(repo_path, main_repo_user, repo_name, repo):
    main_repo_url = 'https://www.github.com/' + main_repo_user + '/' + repo_name + '.git'
    origin = repo.create_remote('origin', main_repo_url)
    origin.fetch()
    repo.git.reset('--hard','origin/master')

def pull_request_to_github(file_name, repo_path, configuration, main_repo_user, repo_name, environment, repo):
  
    bot_user = environment['username']
    check_exists_url = 'https://api.github.com/repos/' + bot_user + '/' + repo_name
    fork_string = main_repo_user + '/' + repo_name
    ssh_remote = 'git@github.com:' + bot_user + '/' + repo_name
    pull_request_url = 'https://api.github.com/repos/' + main_repo_user + '/' + repo_name + '/pulls'
    auth_string = bot_user + ':' + environment['password']
    pull_request_data = '{"title": "' + environment['pull_request_title'] + '", "head": "' + bot_user + ':master", "base": "master"}'

    index = repo.index
    path = repo_path + file_name

    index.add([file_name])
    repo.git.add(file_name) 
    author = Actor(environment['name'], environment['email'])
    committer = Actor(environment['name'], environment['email'])
    commit_message = environment['commit_message']
    head_commit = str(repo.head.commit)
    index.commit(commit_message, author=author, committer=committer)

    response = requests.get(check_exists_url)
    data = response.json()
    if('message' in data and data['message'] == 'Not Found'):
        print('Creating fork')
        print subprocess.check_output(['git', 'hub', 'fork', fork_string])
    else:
        print('fork already created')

    repo2 = Repo.init(repo_name + '2')
    origin = repo2.create_remote('origin', ssh_remote)
    origin.fetch()
    origin.pull(origin.refs[0].remote_head)
    git2 = repo2.git
    git2.reset('--hard', 'HEAD~2')
    repo2.git.push('origin', 'HEAD:master', '--force')

    repo.delete_remote(origin)
    origin = repo.create_remote('origin', ssh_remote)
    repo.git.push("origin", "HEAD:master")

    print subprocess.check_output(['curl', '--user', auth_string, pull_request_url, '-d', pull_request_data])


#Check that the url for the zip file can be reached.
def check_valid_url(repo_zip_url):
    #Get just the head.
    request = requests.head(repo_zip_url)
    #It should be either success (200's) or redirect(300's).
    #Otherwise, inform the user of failure.
    if (request.status_code >= 400 or request.status_code < 200):
        print('Could not reach URL provided.\n')
        print('Provided url was ' + repo_zip_url 
              + ' and resulted in status code ' + str(request.status_code))
        return False
    else:
        return True

if __name__ == "__main__": main()
