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

@click.command()
@click.option('--url', prompt='The url of the GitHub repo zip file to scan', help='The url of the GitHub repo zip file to scan.')

def main(url):
	#Argument is the url of the GitHub zip file
	repo_zip_url = url
	download_repo_run_scan(repo_zip_url)

#The overall process of downloading and scanning a repo
def download_repo_run_scan(repo_zip_url):
	#If url gives error, exit
	if(check_valid_url(repo_zip_url) == False):
		sys.exit()
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

#Check that the url for the zip file can be reached
def check_valid_url(repo_zip_url):
	#get just the head
	request = requests.head(repo_zip_url)
	#It should be success (200's) or redirect(300's)
	#Otherwise, inform user of failure
	if (request.status_code >= 400 or request.status_code < 200):
		print("Could not reach URL provided.\n")
		print("Provided url was " + repo_zip_url + " and resulted in status code " + str(request.status_code))
		return False
	else:
		return True

if __name__ == "__main__": main()
