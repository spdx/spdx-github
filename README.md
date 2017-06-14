# spdx-github
SPDX Github Integration Tools


These instructions were made on Ubuntu 14.04.  They assume that Python has already been installed.

# Main installation:

## Install the ScanCode scanner:

Download scancode from https://github.com/nexB/scancode-toolkit/archive/v2.0.0.rc2.zip

Unzip scancode with this terminal command: unzip scancode-toolkit-2.0.0.rc2.zip

Change directories into the new unzipped directory using this terminal command: cd scancode-toolkit-2.0.0.rc2

Configure scancode using the terminal command: ./scancode --help


## Get the SPDX-GitHub repo:

Download SPDX-GitHub from https://github.com/spdx/spdx-github/archive/master.zip

Unzip SPDX-GitHub with this terminal command: unzip spdx-github-master.zip


## Start the ScanCode virtual environment:

Change back into the scancode directory with: cd scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate


Install the requests security package with this terminal command: pip install requests[security]


The above should get a local instance working.  


# Further installation instructions if the user would like to use webhooks:

Firstly, in order to use webhooks, you must be an administrator of the repository you will be using webhooks for.  Otherwise, you will not have permission to create a webhook.

Also, please note that these instructions and the current code do not yet include security for webhooks.  To see instructions for webhook security, go to this web page:  https://developer.github.com/webhooks/securing/

Any server that can expose SPDX-GitHub to the internet will work, but these instructions will use ngrok.

Download ngrok from this link https://ngrok.com/download

Unzip ngrok.  Example terminal command: unzip ngrok-stable-linux-amd64.zip

From the directory containing ngrok, run this terminal command: ./ngrok http 5000

Open a second terminal window.

Start the ScanCode virtual environment:

Navigate to the scancode toolkit directory: scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate

install Flask using this command: pip install Flask

Navigate to the spdx-github-master directory (where you unzipped SPDX-GitHub earlier).

Run the following terminal command: python run_scan/github_webhooks.py

Open a browser.

Navigate to the GitHub repository you will be creating a webhook for.  Log in if you are not already logged in.

Click the settings tab, then the Webhooks tab.

Click "Add webhook"

Navigate to the terminal window in which you earlier started ngrok.
You will see a line that looks like this, with a slightly different url:
https://12345a6b.ngrok.io -> localhost:5000

Copy the url, and paste it into the GitHub Webhooks page in the "Payload URL" field.

Directly underneath this is the content type field.  Select "application/json"

Right now only push events are supported.  Leave the event selection on "Just the push event"

Click "Add webhook"

You are now set up to run a new scan whenever a new push is made to your repository.


# Useage (without webhooks):

Start the ScanCode virtual environment:

Change back into the scancode directory with: cd scancode-toolkit-2.0.0.rc2

Start the virtual environment with this terminal command: source bin/activate

Navigate to the spdx-github-master directory

Run this terminal command (replacing the example url with a url for your repository's zip download): python run_scan/download_repo_run_scan.py --url https://github.com/example/example/archive/master.zip
