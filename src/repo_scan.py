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
import smtplib
from email.mime.text import MIMEText
import fnmatch
from spdx_github import web_api_client
from shutil import copyfile

@click.command()
@click.option('--url', prompt='The url of the GitHub repo zip file to scan',
              help='The url of the GitHub repo zip file to scan.')

def main(url):
    #The argument is the url of the GitHub zip file
    repo_zip_url = url
    #If the url gives an error, exit
    if(check_valid_url(repo_zip_url) == False):
        sys.exit()
    scan_successful = begin_scan(repo_zip_url)

    if(not scan_successful):
        print("Scan failed")

def begin_scan(url):
    scan_info= get_scan_info(url)

    scanner = scan_info['scanner']
    if(scanner not in scan_info):
        return False

    scanner_location = scan_info[scanner]
    output_file = scan_info['output_file_name']

    if(scanner_location == 'local'):
        repo_scan(url)
    else:
        web_api_client.run_remote_scan(url, output_file, scanner)

    return True

def get_scan_info(url):
    #Download the zip and get its path.
    file_location = download_github_zip(url)
    #Extract the zip and get the path of the extracted directory.
    repo_path = unzip_file(file_location)

    #The configuration.yml file is stored with the repo.
    #get_config returns us a dictionary based on this file
    #with the configuration options.
    config_path = find_file_location(repo_path, 'configuration.yml')
    configuration = get_config_yml(config_path, 'configuration.yml')

    scanner = configuration['scanner']

    #Remove the zip file.
    remove(file_location)
    #Remove the unzipped directory.
    shutil.rmtree(repo_path)

    env_path = find_file_location('../', 'environment.yml')
    environment = get_config_yml(env_path, 'environment.yml')

    scanner_info = environment.copy()
    scanner_info.update(configuration)

    #scanner_info = environment + configuration

    return scanner_info

#This method goes throught the overall process 
#of downloading and scanning a repo.
def repo_scan(repo_zip_url, remote = False, task_id = 0):

    #Download the zip and get its path.
    file_location = download_github_zip(repo_zip_url)
    #Extract the zip and get the path of the extracted directory.
    repo_path = unzip_file(file_location)

    #The configuration.yml file is stored with the repo.
    #get_config returns us a dictionary based on this file
    #with the configuration options.
    config_path = find_file_location(repo_path, 'configuration.yml')
    configuration = get_config_yml(config_path, 'configuration.yml')
    #Check that the configuration file's output file name ends
    #with the spdx extension. If not, add it.
    if(remote):
        spdx_file_name = task_id + '.spdx'
    else:
        suffix = configuration['output_file_name'][-5:]
        if(suffix != '.SPDX' and suffix != '.spdx'):
            spdx_file_name = configuration['output_file_name'] + '.spdx'
        else:
            spdx_file_name = configuration['output_file_name']

    #The environment.yml file is stored locally because it includes
    #authentication information.  get_config gets us a
    #dictionary with the options.
    env_path = find_file_location('../', 'environment.yml')
    environment = get_config_yml(env_path, 'environment.yml')

    #exit()
    #We have the zip file url.  We will need other urls related to
    #the repo in order to make a pull request.  To do this, we first
    #get the username and repo name from the zip url using a regex.
    #The zip url could be formatted in multiple ways, so we handle
    #multiple url formats.
    m = re.match(r"https://github.com/(\w+)/(\w+)/", repo_zip_url)
    if(m):
        main_repo_user = m.group(1)
        repo_name = m.group(2)
    else:
        m = re.match(r"https://api.github.com/repos/(\w+)/(\w+)/zipball", repo_zip_url)
        main_repo_user = m.group(1)
        repo_name = m.group(2)

    #Our local copy of the repository is just a directory.
    #Initialize it as a local repo and sync it up with the remote repository.
    repo = Repo.init(repo_path)
    sync_main_repo(repo_path, main_repo_user, repo_name, repo)

    if(remote):
        spdx_file_path = './file_server/' + spdx_file_name
    elif(environment['send_pull_request']):
        #This is the path to the spdx file stored locally
        spdx_file_path = repo_path + spdx_file_name
    else:
        spdx_file_path = environment['local_spdx_path'] + spdx_file_name

    #Scan the extracted directory and put results in a named file.
    scan_successful = scan(repo_path, spdx_file_path, 'scancode',
                          configuration['output_type'])

    if(not scan_successful):
        return 'Scan Failed'

    if(environment['send_pull_request']):
        if(remote):
            copyfile(spdx_file_path, repo_path + configuration['output_file_name'])
            spdx_file_name = configuration['output_file_name']
        make_pull_request(spdx_file_name, repo, environment, repo_name, main_repo_user)

    #Remove the zip file.
    remove(file_location)
    #Remove the unzipped directory.
    shutil.rmtree(repo_path)

    if(environment['send_notification_email']):
        send_email(environment)

    return spdx_file_name

#Run a scan for a repository and output the spdx file.
#Also handles configuration options for the scan
def scan(directory_to_scan, output_file_name, scanner, output_type):
    #Use the configuration file's options for output format
    if(output_type == 'tag-value'):
        output_format = 'spdx-tv'
    elif(output_type == 'rdf'):
        output_format = 'spdx-rdf'
    #Scan the unzipped directory.
    if(scanner == 'scancode'):
        scan_output = subprocess.check_output(['scancode','--format',
                                               output_format,directory_to_scan,
                                               output_file_name])
        return True
    else:
        #This should be reached if a scanner that is not yet implemented
        #has been specified
        return False

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

#A YAML configuration file is contained in directory.
#Its name is file_name.  Convert it to a dictionary
#and return it.  If the file is not found, create
#some default options for it.
def get_config_yml(directory, file_name):
    config_file = directory + file_name
    if(path.isfile(config_file)):
        stream = file(config_file, 'r')
        configuration = safe_load(stream)
    elif(file_name == 'configuration.yml'):
        configuration = {}
        configuration['output_file_name'] = directory[:-1] + '.SPDX'
	configuration['output_type'] = 'tag-value'
    else:
        configuration = {}
    return configuration

#Sync up a local repo with its remote repository.
def sync_main_repo(repo_path, main_repo_user, repo_name, repo):
    main_repo_url = ('https://www.github.com/' + main_repo_user + '/'
                     + repo_name + '.git')
    origin = repo.create_remote('origin', main_repo_url)
    origin.fetch()
    repo.git.reset('--hard','origin/master')
    repo.delete_remote(origin)

#All steps of a pull request including
#Making the comit, forking, preventing conflicts
#Pushing changes, and finally making the request
def make_pull_request(spdx_file_name, repo, environment, repo_name, main_repo_user):
    commit_file(spdx_file_name, repo, environment)
    create_fork(repo_name, main_repo_user, environment)
    undo_recent_commits(repo_name, environment)
    push_to_remote(repo, repo_name, environment)
    pull_request_to_github(main_repo_user, repo_name, environment)

#Make a pull request to GitHub with the new SPDX file.
def pull_request_to_github(main_repo_user, repo_name, environment):

    #Creating strings, mainly URLs, that will be needed for the
    #pull request process.

    #This is the API URL to make a pull request
    pull_request_url = ('https://api.github.com/repos/' + main_repo_user + '/'
                        + repo_name + '/pulls')
    #This has the username and password from the environment file.
    #It is used to log in for API calls.
    auth_string = environment['github_username'] + ':' + environment['github_password']
    #This is the data that will be posted for the pull request.
    #It tells the API what the pull request will be like.
    pull_request_data = ('{"title": "' + environment['github_pull_request_title']
                         + '", "head": "' + environment['github_username']
                         + ':master", "base": "master"}')

    #Make the pull request to the main repository
    print subprocess.check_output(['curl', '--user', auth_string,
                                  pull_request_url, '-d', pull_request_data])

def commit_file(file_name, repo, environment):
    #The index of the repo is used to add the spdx file to be committed.
    index = repo.index
    #Add the SPDX file to be committed
    index.add([file_name])
    repo.git.add(file_name)
    #Set the author, committer, and commit message.
    author = Actor(environment['git_name'], environment['git_email'])
    committer = Actor(environment['git_name'], environment['git_email'])
    commit_message = environment['git_commit_message']
    #Get the head commit
    head_commit = str(repo.head.commit)
    #Make the commit locally of the new SPDX file
    index.commit(commit_message, author=author, committer=committer)

def create_fork(repo_name, main_repo_user, environment):
    #The bot user will create a fork of the repository, but first we
    #must check if the bot user already has a fork of the repository.
    #This URL is used for that.
    check_exists_url = ('https://api.github.com/repos/' + environment['github_username']
                        + '/' + repo_name)
    #This is the username/repo for the main repo we will be forking
    fork_string = main_repo_user + '/' + repo_name
    #Check whether the remote fork of this repository exists.
    #If it doesn't exist, create a new fork for the bot user.
    response = requests.get(check_exists_url)
    data = response.json()
    if('message' in data and data['message'] == 'Not Found'):
        print('Creating fork')
        print subprocess.check_output(['git', 'hub', 'fork', fork_string])
    else:
        print('fork already created')

def undo_recent_commits(repo_name, environment):
    #This is to access the bot user's forked repo using SSH
    ssh_remote = ('git@github.com:' + environment['github_username'] 
                  + '/' + repo_name)

    #The remote fork may already have an SPDX document that was
    #not pulled yet by the main repository.  
    #To avoid merge conflicts, we first
    #remove the latest commits from the fork.
    #This is because merge conflicts would require human intervention.
    #This comes into play, for example, when more than one push was
    #made on the main repository, meaning we ran the scan again
    #without the first update being accepted into the main repository
    #The only data that is lost is our own scanner-generated spdx
    #document from the most recent scan prior to this one.
    repo2 = Repo.init(repo_name + '2')
    origin = repo2.create_remote('origin', ssh_remote)
    origin.fetch()
    origin.pull(origin.refs[0].remote_head)
    git2 = repo2.git
    git2.reset('--hard', 'HEAD~2')
    repo2.git.push('origin', 'HEAD:master', '--force')
    shutil.rmtree(repo_name + '2')

def push_to_remote(repo, repo_name, environment):
    #This is to access the bot user's forked repo using SSH
    ssh_remote = ('git@github.com:' + environment['github_username'] 
                  + '/' + repo_name)

    #The local repository's remote is the main repository.
    #Change its remote to the fork of the main repository,
    #and then push the new SPDX commit
    origin = repo.create_remote('origin', ssh_remote)
    repo.git.push("origin", "HEAD:master")

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

def send_email(environment):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(environment['gmail_email'], environment['gmail_password'])
 
    msg = msg = MIMEText(environment['notification_message'])
    msg['Subject'] = environment['notification_subject']
    msg['From'] = environment['gmail_email']
    msg['To'] = environment['notification_email']
    server.sendmail(environment['gmail_email'], environment['notification_email'], msg.as_string())
    server.quit()

def find_file_location(directory, file_name):
    file_directory = directory
    #https://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, file_name):
            file_directory = root
    if(file_directory[-1:] != '/'):
        file_directory = file_directory + '/'
    return file_directory

if __name__ == "__main__": main()
