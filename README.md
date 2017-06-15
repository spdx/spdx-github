# spdx-github
SPDX Github Integration Tools

Currently this repo contains example code for scanning a repo using license scanners.

dosocs_run_scan.py : example of scanning a repo using DoSOCSv2 (requires DoSOCSv2 to be installed)

scancode_run_scan.py : example of scanning a repo using ScanCode (requires ScanCode to be installed)

scancode_library_run_scan.py : example of scanning a repo programmatically using ScanCode (other examples use subprocess and command line)

inside run_scan directory:

   download_repo_run_scan.py : example of downloading a repo from GitHub using a command line argument url to the zip file, unzipping the file, and scanning it.
  
   unit_test.py : unit tests for download_repo_run_scan.py

   github_webhooks.py : This receives a POST request from a GitHub webhook configured for push requests and scans the repository that the webhook is associated with.  To use this, it will need to be running on a server and exposed to the internet.  It was tested using ngrok as explained here: https://developer.github.com/webhooks/configuring/. When following the tutorial, github_webhooks.py replaces the Ruby file used in the tutorial and port 5000 is used instead of 4567 to match the Flask port.  A webhook on a GitHub repository also needs to be created in order to use this, which is described in more detail here: https://developer.github.com/webhooks/creating/.  A webhook configured for something other than a push request may post different JSON, so github_webhooks.py may not work with such a webhook.
