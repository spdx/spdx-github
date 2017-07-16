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

The environment.yml file contains information that will be used to make a pull request.  The pull request is made by a second, bot account without any access to the repository to be scanned.  Edit the values in environment.yml to match what you would like, for example, the title of the pull request and the username of the bot user.  It also requires a gmail email and password to send a notification email from and an email on which you would like to receive notificaion of a new spdx document.  The environment file is intended only for local use, not to be placed on the main repository.

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


## Useage (without webhooks):

Start the ScanCode virtual environment:

Change back into the scancode directory with: cd scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate

Navigate to the spdx-github-master directory

Run this terminal command (replacing the example url with a url for your repository's zip download): python src/repo_scan.py --url https://github.com/example/example/archive/master.zip