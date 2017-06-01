#This is an example of downloading a repo zip file, 
#unzipping it and running a scan on it.
#The example uses scancode, but dosocsv2 could also be used.
#Future updates:
#1. Display help information if user didn't supply correct arguments
#2. Handle if user did not give url to a zip file download

import subprocess
from subprocess import call
import requests
import os
from os import path, remove
import shutil
import zipfile
import sys

def main():
	#Argument is the url of the GitHub zip file
	repo_zip_url = sys.argv[1]
	#Download the zip and get its path
	file_location = download_github_zip(repo_zip_url)
	#extract the zip and get path of extracted directory
	extracted_directory = unzip_file(file_location)

	#Set output file name to the directory name .SPDX
	spdx_file_name = extracted_directory[:-1] + '.SPDX'

	#scan the extracted directory and put results in a named file
	scan(extracted_directory, spdx_file_name)

	#Remove the zip file
	remove(file_location)
	#Remove the unzipped directory
	shutil.rmtree(extracted_directory)

def scan(directory_to_scan, spdx_file_name):
	#Scan the unzipped directory
	print subprocess.check_output(['scancode','--format','spdx-tv',directory_to_scan,spdx_file_name])


#Unzip a zip file and return the path to the extracted directory
def unzip_file(file_location):
	#Unzip the zip file
	zip_file = zipfile.ZipFile(file_location, 'r')
	zip_file.extractall()
	#Get the directory that results from unzipping
	#(Assume there is only one)
	extracted_directory = (zip_file.namelist())[0]
	zip_file.close()
	#return the path to the extracted directory
	return extracted_directory


#Download a zip file and return the path of the downloaded file
def download_github_zip(repo_zip_url):
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
	#return path to the downloaded file
	return file_location	

if __name__ == "__main__": main()
