#This is an example of downloading a repo zip file, 
#unzipping it and running a scan on it.
#The example uses scancode, but dosocsv2 could also be used.
#In the future, urls and paths will not be hardcoded.

import subprocess
from subprocess import call
import requests
from os import remove
import shutil

to_scan = requests.get('https://github.com/OSSHealth/ghdata/archive/master.zip', stream=True)

file_location = '/home/anna/Desktop/scancode/ghdata.zip'

with open(file_location, 'wb') as fd:
	for chunk in to_scan.iter_content(chunk_size=1024):
		fd.write(chunk)

call(['unzip', file_location])
remove(file_location)

print subprocess.check_output(['scancode','/home/anna/Desktop/scancode/ghdata-master','--format','spdx-tv'])

shutil.rmtree('/home/anna/Desktop/scancode/ghdata-master')
