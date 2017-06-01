#This is an example of downloading a repo zip file, 
#unzipping it and running a scan on it.
#The example uses scancode, but dosocsv2 could also be used.
#Future updates:
#1. Display help information if user didn't supply correct arguments
#2. Handle if user did not give url to a zip file download
#3. Save SPDX to document instead of stdout
#4. Clearer methods (currently scan method also downloads and unzips as well as scans)

import subprocess
from subprocess import call
import requests
import os
from os import path, remove
import shutil
import zipfile
import sys

def main():
	scan(sys.argv[1])

def scan(repo_zip_url):
	#Getting a zip file to download
	to_scan = requests.get(repo_zip_url, stream=True)

	#Get path to where zip file will be stored
	#Name of the zip file
	zip_file_name = repo_zip_url[repo_zip_url.rfind('/')+1:]
	#Path to the directory containing the zip file
	directory_path = os.path.dirname(os.path.realpath(__file__))
	#Concatenate file name with path
	file_location = directory_path + zip_file_name

	#write zip file in chunks
	with open(file_location, 'wb') as fd:
		for chunk in to_scan.iter_content(chunk_size=1024):
			fd.write(chunk)

	#Unzip the zip file
	zip_file = zipfile.ZipFile(file_location, 'r')
	zip_file.extractall()
	#Get the directory that results from unzipping
	#(Assume there is only one)
	extracted_directory = (zip_file.namelist())[0]
	zip_file.close()
	#Remove the zip file
	remove(file_location)

	#Scan the unzipped directory
	print subprocess.check_output(['scancode',extracted_directory,'--format','spdx-tv'])

	#Remove the unzipped directory
	shutil.rmtree(extracted_directory)


if __name__ == "__main__": main()
