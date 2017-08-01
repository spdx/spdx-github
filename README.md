# spdx-github
SPDX Github Integration Tools


These instructions were made on Ubuntu 14.04.  They assume that Python has already been installed.

## Main installation:

### Install the ScanCode scanner:

Download scancode from https://github.com/nexB/scancode-toolkit/archive/v2.0.0.rc2.zip

Unzip scancode with this terminal command: unzip scancode-toolkit-2.0.0.rc2.zip

Change directories into the new unzipped directory using this terminal command: cd scancode-toolkit-2.0.0.rc2

Configure scancode using the terminal command: ./scancode --help


### Get the SPDX-GitHub repo:

Download SPDX-GitHub from https://github.com/spdx/spdx-github/archive/master.zip

Unzip SPDX-GitHub with this terminal command: unzip spdx-github-master.zip


### Start the ScanCode virtual environment:

Change back into the scancode directory with: cd scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate


Install the requests security package with this terminal command: pip install requests[security]

Install the hub package with this terminal command: pip install hub


### Run the setup script

From the folder for SPDX-GitHub, run 'python setup.py install'

### Modify the environment.yml file

The environment.yml file contains options that are stored locally.  It is not intended to be placed on a remote repository.  The environment file includes the options to choose if you would like the SPDX document to be delivered to your repository through a pull request or stored locally, as well as the option to receive an email notification once the scan has been completed. If you would not like email notifications, change send_notification_email to False.  You can also set the send_pull_request option to False if you would not like a pull request.  In that case, you will want to set the local_spdx_path to the location you would like the new document to be stored locally.  If the email and pull request options are set to False, no usernames or passwords are needed and those options can be left as dummy values.

If you set these values to True, you will need some dummy accounts: a GitHub account for the pull request, and a Gmail account for the email notifications.  The pull request is made by a bot account without any access to the repository to be scanned.  Edit the values in environment.yml to match what you would like, for example, the title of the pull request and the username of the bot user.  If you would like to be sent an email notification when the SPDX document is ready, it also requires a gmail email and password to send a notification email from and an email on which you would like to receive notificaion of a new spdx document.

### Modify the configuration.yml file

The configuration.yml file is stored in the main repository.  It provides options on how the scan will be run, for example, the name of the output SPDX document.  Modify this file to match the options you would like.

### Set up SSH

SPDX-GitHub will create a pull request with the new SPDX document.  In order to do this, it needs to be able to access a GitHub account on which it can fork the repository.  It is intended that this account will be a second, bot account and not an account with any access or commit rights to the main repository.  The bot user will need SSH authentication for GitHub set up in order to work with its fork of the repository.  Instructions on setting up SSH:  https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/

The above should get a local instance working. 

## Further installation instructions if the user would like to use webhooks:

Firstly, in order to use webhooks, you must be an administrator of the repository you will be using webhooks for.  Otherwise, you will not have permission to create a webhook.

Also, please note that these instructions and the current code do not yet include security for webhooks.  To see instructions for webhook security, go to this web page:  https://developer.github.com/webhooks/securing/

A server that will expose SPDX-GitHub to the internet is needed.  These instructions assume that the user will want to use a server of their choice and thus do not include instructions for setting up the web server.

Open a terminal window.

Start the ScanCode virtual environment:

Navigate to the scancode toolkit directory: scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate

install Flask using this command: pip install Flask

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

In order to set up the machines for remote communication:

Install spdx-github on both machines.

Install the scanner on the machine you would like.

run 'python web_api_server.py' for the API server on the remote machine.  Use a server to expose it to the internet.

run the file server using python -m SimpleHTTPServer 8000, or change the port if you desire.  SPDX files are served from the src/file_server folder.


## Useage (without webhooks):

Start the ScanCode virtual environment:

Change back into the scancode directory with: cd scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate

Navigate to the spdx-github-master directory

Run this terminal command (replacing the example url with a url for your repository's zip download): python src/repo_scan.py --url https://github.com/example/example/archive/master.zip
