# Archive Status
This repository has been moved to archive status as of 9 January 2022

# spdx-github
SPDX Github Integration Tools


These instructions were made on Ubuntu 14.04.  They assume that Python has already been installed.

## Main installation:

### Install the ScanCode scanner:

Download scancode from https://github.com/nexB/scancode-toolkit/archive/v2.0.0.rc2.zip

Unzip scancode with this terminal command: unzip scancode-toolkit-2.0.0.rc2.zip

Change directories into the new unzipped directory using this terminal command: cd scancode-toolkit-2.0.0.rc2

Configure scancode using the terminal command: ./scancode --help

### Start the ScanCode virtual environment:

Change back into the scancode directory with: cd scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate

### Get the SPDX-GitHub repo:

Download SPDX-GitHub from https://github.com/spdx/spdx-github/archive/master.zip

Unzip SPDX-GitHub with this terminal command: unzip spdx-github-master.zip

From the folder for SPDX-GitHub, run 'python setup.py install'

### Install dependencies:

Run the following commands to install spdx-github's dependencies:

pip install mock

pip install gitpython

pip install Flask

pip install requests[security]


### Create the environment.yml file

In the folder for spdx-github you will find the environment.example.yml file.  Copy this file and name the copy environment.yml.

Next, modify environment.yml to meet your needs.  The following are descriptions of each of the settings in environment.yml:

#### Settings related to pull request
SPDX-GitHub allows you to receive a pull request with the newly created SPDX document.  The pull request will be sent to the repository that was scanned.  In order to send the pull request, spdx-github will need you to have a GitHub account, ideally a dummy or bot account, whose username and password you will add to the environment file.  If you do not wish to provide an account or do not wish to receive pull requests, set the send_pull_request setting to False.  If this is set to False, you should not need to pay attention to the pull request related settings.  The new spdx document will be created on your local machine if you opted not to use a pull request.

send_pull_request

Set this to True if you want the scanned repository to receive a pull request with the new spdx document.  Set it to False if you do not want to receive a pull request.

github_username

This is the username for a dummy or bot github account.

github_password

This is the password to the dummy GitHub account for github_username.

github_pull_request_title

This is the title you would like for a pull request containing the new spdx document.

git_name

This is the name that will be associated with the commit for the new spdx document in the pull request.

git_email

This is the email address that will be associated with the commit for the new spdx document.

git_commit_message

This is the commit message you would like for the new spdx document's commit.

#### Settings related to email notification
SPDX-GitHub can send you a notification email when a scan has been completed.  If you want to receive an email, set send_notification_email to True.  If you do not want an email notification, set it to False.  The notification email will be sent from a gmail account whose email address and password are provided in this environment file.  If you set email notifications to False, you do not need to provide an account or password.

send_notification_email

Set this to True if you want to receive an email when a scan is complete.  Set it to False if you would not like to receive an email.

gmail_email

This is the gmail email address that the notification email will come from.

gmail_password

This is the password to the above email account

notification_email

This is the email address to which you would like the notification email to be sent.

notification_subject

This is the subject you would like for the notification email.

notification_message

This is the content you would like to appear in the notification email message.

#### Settings related to the local version of the spdx document
Although it can create a pull request, spdx-github also creates a local copy of the new spdx document.  This setting is the path to the directory in which you would like the new spdx document to be found.  This setting is necessary even if you have set pull requests to True, although you can leave it as a simple default value.

local_spdx_path

This is the path to the directory where you would like to find the new spdx document.

#### Settings related to scanners
SPDX-GitHub supports multiple scanners, and you can select which scanner to use in the configuration file that is stored with the repository you are trying to scan.  The scanner to use is selected using the configuration.yml file (described later in this document) that is stored with the repository to be scanned.  The environment file tells spdx-github whether the scanner is installed locally or on a remote machine.  The format is the following (with scannername replaced with the name of the scanner).  There can be more than one scanner in the environment file as long as each scanner name is unique:

scannername

This can be set to either 'local' if the scanner is installed on the same machine as spdx-github, or to a url if the scanner is installed on a remote machine.  If it is remote, an API server (described later in this document) will need to be running on the remote machine.

scannername_download

This is not necessary if the scanner is local.  If the scanner is remote, this is the url from which new spdx files will be served so that
spdx-github can download them.

### Set up the configuration.yml file

Create a file named configuration.yml and store it with the repository or repositories you are going to scan.  The configuration file includes the following options:

output_file_name

This is the name of the spdx file you would like to be created.

output_type

This specifies the spdx format you would like.  The possible options are rdf or tag-value.

scanner

This is the name of the scanner you would like to use.  For example, 'scancode'.  The name of the scanner in the configuration file should match exactly to the scanner name in the environment file.

### Set up SSH

SPDX-GitHub can create a pull request with the new SPDX document.  In order to do this, it needs to be able to access a GitHub account on which it can fork the repository.  It is intended that this account will be a second, bot account and not an account with any access or commit rights to the main repository.  The bot user will need SSH authentication for GitHub set up in order to work with its fork of the repository.  Instructions on setting up SSH:  https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/ 

## To use webhooks with spdx-github:

SPDX-GitHub can use webhooks to run its scans.  This means that whenever a repository is updated, a new scan can be automatically run.  If you do not want to set up webhooks, you can still run scans from the command line.

Firstly, in order to use webhooks, you must be an administrator of the repository you will be scanning.  Otherwise, you will not have permission to create a webhook.

Also, please note that these instructions and the current code do not yet include security for webhooks.  To see instructions for webhook security, go to this web page:  https://developer.github.com/webhooks/securing/

A server that will expose SPDX-GitHub to the internet is needed.  These instructions assume that the user will want to use a server of their choice and thus do not include instructions for setting up the web server.

Open a terminal window.

Start the ScanCode virtual environment:

Navigate to the scancode toolkit directory: scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate

Navigate to the spdx-github-master directory (where you unzipped SPDX-GitHub earlier).

Run the following terminal command: python src/github_webhooks.py.  This starts the code that will wait for a webhook.

Open a browser.

Navigate to the GitHub repository you will be creating a webhook for.  Log in if you are not already logged in.

Click the settings tab, then the Webhooks tab.

Click "Add webhook"

Copy the url of your server running github_webhooks.py, and paste it into the GitHub Webhooks page in the "Payload URL" field.

Directly underneath this is the content type field.  Select "application/json"

Right now push and release events are supported.  Select either only pushes, only releases, or both pushes and releases.

Click "Add webhook"

You are now set up to run a new scan whenever a new push or release is made to your repository.

## Using the web API:

A scanner may be stored on a different machine from the main spdx-github instance.  If this is the case, the scan will be performed through calls to the web API.  In order for this to happen, the configuration and environment files must be set up correctly.

configuration file:
The configuration file (stored with the repo to be scanned) has the 'scanner' field.  Enter the desired scanner here.  Current options are 'scancode' and 'dosocsv2'

environment file:
In the environment file, have an entry for the scanner.  This looks similar to the following:

scancode: local

An entry of 'local' tells spdx-github that you have scancode installed locally.  If you instead are using a remote instance of scancode, give the url of the exposed API server here.

If your scanner is remote, one more entry will be needed in the environment file.  It looks like this:

scancode_download: www.example.url

This tells spdx-github the exposed url where you will be serving the completed SPDX files from, which can be different from the API url.

### In order to set up the machines for remote communication:

#### For a remote machine that uses spdx-github:

Install spdx-github on both machines.

Install the scanner on the machine you would like.

run 'python web_api_server.py' for the API server on the remote machine.  Use a server to expose it to the internet.

run the file server using python -m SimpleHTTPServer 8000, or change the port if you desire.  SPDX files are served from the src/file_server folder.

#### For a remote machine that does not use spdx-github:

Install spdx-github on the client machine.

Install the scanner on the server machine.

Create and run a web server that follows the API request-repsonse protocol described [here](https://github.com/spdx/spdx-github/wiki/Architecture#example-requests-and-responses).  This should match the url you gave in the environment file for the API.

Have your server serve the .spdx files it creates and give them names like 'id.spdx' where id is the id you give as a response in the API JSON.  This should match the url you gave in the environment file for the file server.

If you would like other people to use your scanner's server with spdx-github, make the urls for the API and file server available to them.  They will be able to use it by making the changes to the environment and configuration file settings described above.

## Useage from the command line:

Start the ScanCode virtual environment:

Change into the scancode directory with: cd scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate

Navigate to the spdx-github-master directory

Run this terminal command (replacing the example url with a url for your repository's zip download): python src/repo_scan.py --url https://github.com/example/example/archive/master.zip

## (Optional) Installing DoSOCsv2:

If you choose DoSOCs as your scanner option, you will need to install it.  Follow the installation instructions found in the readme here: https://github.com/DoSOCSv2/DoSOCSv2

## (Optional) Add a new scanner:

Currently supported scanners are ScanCode and DoSOCSv2.  If you would like to use a scanner other than these with spdx-github, there are two options.  The first option is to make a minor change to the source code as well as additions to the environment file.  View full instructions on adding a new scanner this way here: https://github.com/spdx/spdx-github/wiki/Adding-a-New-Scanner-to-spdx-github.  The second option is to use the web API and create a server that can interface with spdx-github.  Instructions for creating a web API server are here: https://github.com/spdx/spdx-github/wiki/Creating-a-remote-API-scan-server
