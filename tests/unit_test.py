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

import unittest
import sys
from os import path, remove
import shutil
import re
import subprocess
import mock

from git import Repo
from git import test

from spdx_github import repo_scan


#Test that when given a valid zip file url,
#the download_github_zip will result in the creation
#of a local file at the returned location
class DownloadFileTestCase(unittest.TestCase):
    file_location = ''
    url = 'https://github.com/abuhman/test_webhooks/archive/master.zip'

    def setUp(self):
        self.file_location = repo_scan.download_github_zip(self.url)

    def tearDown(self):
        remove(self.file_location)

    def testDownload(self):
        assert path.isfile(self.file_location)


#Test that we can unzip a zip file.
class UnzipFileTestCase(unittest.TestCase):
    file_location = 'test.zip'
    extracted_directory = ''
    def setUp(self):
        self.extracted_directory = repo_scan.unzip_file(self.file_location)

    def tearDown(self):
        #Remove the unzipped directory
        shutil.rmtree(self.extracted_directory)

    def testUnzip(self):
        assert path.isdir(self.extracted_directory)


#This tests whether a file output is produced from calling the scan method.
class ScanTestCase(unittest.TestCase):
    directory = 'test2/'
    spdx_file_name = ''

    def setUp(self):
        #Set output file name to the directory name .SPDX.
        self.spdx_file_name = '{}.SPDX'.format(self.directory[:-1])

        #scan the extracted directory and put results in a named file
        repo_scan.scan(self.directory, self.spdx_file_name,
                                    'scancode', 'tag-value')

    def tearDown(self):
        #Remove the scan results file
        remove(self.spdx_file_name)

    def testScan(self):
        assert path.isfile(self.spdx_file_name)

#Test trying to scan with a scanner that isn't implemented
class ScannerDoesntExistTestCase(unittest.TestCase):
    directory = 'test2/'
    spdx_file_name = ''
    
    #result should be false because it is a fake scanner
    result = repo_scan.scan(directory, spdx_file_name, 'fake_scanner', 
	                        'tag-value')
    
    def testScannerDoesntExist(self):
        assert self.result == False

#This checks whether the check_valid_url method correctly determines
#whether a url results in an error (400 or 500 code).
#or whether it is not a real url (does not start with http://
#or https:// )
class CheckURLTestCase(unittest.TestCase):
    good_url = 'https://www.google.com/'
    bad_url = 'https://www.google.com/fail'
    not_url = 'abcdefg'

    def testGoodURL(self):
        assert repo_scan.check_valid_url(self.good_url) == True

    def testBadURL(self):
        assert repo_scan.check_valid_url(self.bad_url) == False

    def testNotURL(self):
        assert repo_scan.check_valid_url(self.not_url) == False

#Check that the YAML configuration/environment method is working.
#It should return a dictionary with the contents of the config
#or environment file.
class GetConfigTestCase(unittest.TestCase):
    from spdx_github import repo_scan
    configExisting = repo_scan.get_config_yml('./', 'test.yml')
    configNotExisting = repo_scan.get_config_yml('test/', 'configuration.yml')
    environNotExisting = repo_scan.get_config_yml('test/', 'environment.yml')

    #A configuration file that exists should yield values that match
    #the testing file
    def testExistingConfig(self):
        assert self.configExisting['output_file_name'] == 'file_name.SPDX'
        assert self.configExisting['output_type'] == 'rdf'

    #A configuration file that does not exist should yield default
    #values
    def testNotExistingConfig(self):
        assert self.configNotExisting['output_file_name'] == 'test.SPDX'
        assert self.configNotExisting['output_type'] == 'tag-value'

    #An environment file that does not exist should yield an empty
    #dictionary
    def testNotExistingEnviron(self):
        assert type(self.environNotExisting) is dict
        assert not self.environNotExisting

#Test the method that syncs a repo to its remote
class SyncRepoTestCase(unittest.TestCase):
    #Set up a local repo
    repo_path = './test_repo'
    main_repo_user = 'abuhman'
    repo_name = 'test_webhooks'
    repo = Repo.init(repo_path)
    #Call the sync_main_repo method to sync it with the remote
    repo_scan.sync_main_repo(repo_path, main_repo_user, repo_name, repo)

    #Get the remote origin and fetch any changes
    main_repo_url = ('https://www.github.com/{}/{}.git'.format(main_repo_user,
                     repo_name))
    origin = repo.create_remote('origin', main_repo_url)
    repo.git.fetch()
    #Check the diff between the remote version and the local version
    output_string = repo.git.diff('origin/master')
    repo.delete_remote(origin)

    def tearDown(self):
        shutil.rmtree(self.repo_path)

    def testRepoSynced(self):
        #Output of git diff should be empty if they are synced
        assert self.output_string == ""

#Test the commit_file method which adds a file and makes a
#commit
class MakeCommitTestCase(unittest.TestCase):
    #Get everything ready for the commit
    file_name = 'test.yml'
    subprocess.check_output(['cp', file_name, './test_repo'])
    repo = Repo.init('./test_repo')
    environment = {}
    environment['git_name'] = 'TEST_NAME'
    environment['git_email'] = 'TEST_EMAIL'
    environment['git_commit_message'] = 'TEST_MSG'
    #Call the commit method in order to make the commit
    repo_scan.commit_file(file_name, repo, environment)
    #Get the head commit.
    headcommit = repo.head.commit

    #To tear down, reset to origin master, which deletes the test commit
    def tearDown(self):
        main_repo_user = 'abuhman'
        repo_name = 'test_webhooks'
        main_repo_url = ('https://www.github.com/{}/{}.git'.format(
		                 main_repo_user, repo_name))

        origin = self.repo.create_remote('origin', main_repo_url)
        origin.fetch()
        self.repo.git.reset('--hard','origin/master')

    #The head commit name should match the test commit name
    #because the test commit should be the most recent commit.
    def testCommitMade(self):
        assert self.headcommit.author.name == 'TEST_NAME'

#Get scan info should get us the contents of both the environment
#and configuration files.
#This test will fail if the environment and configuration files
#are set up wrong
class GetScanInfoTestCase(unittest.TestCase):
    url = 'https://github.com/abuhman/test_webhooks/archive/master.zip'
    scanner_info = repo_scan.get_scan_info(url)

    #Test that we have gotten keys from both environment.yml
    #and configuration.yml 
    def testGetScanInfo(self):
        #'scanner' is in the configuration file
        assert 'scanner' in self.scanner_info
        #The value of 'scanner' is in the environment file
        assert self.scanner_info['scanner'] in self.scanner_info

#Test the repo_scan method, which handles the process of a
#local scan.
class repoScanTestCase(unittest.TestCase):
    repo_zip_url = 'https://github.com/abuhman/test_webhooks/archive/master.zip'
    spdx_file_path = repo_scan.repo_scan(repo_zip_url, remote = False, 
	                                     task_id = 0)

    def tearDown(self):
        remove(self.spdx_file_path)
    
    def testRepoScan(self):
        assert path.isfile(self.spdx_file_path), self.spdx_file_path

#Tests the pull_request_to_github method, which makes a pull request
#to github.  This test does not actually make a pull request
#due to using a mock in place of the API call.
class pullRequestToGithubTestCase(unittest.TestCase):
    environment = {}
    environment['github_username'] = 'test_username'
    environment['github_password'] = 'test_password'
    environment['github_pull_request_title'] = 'test_title'
    repo_name = 'test_repo_name'
    main_repo_user = 'test_username_main'

    auth_string = '{}:{}'.format(environment['github_username'], 
	                             environment['github_password'])
    url = 'https://api.github.com/repos/{}/{}/pulls'.format(main_repo_user, 
	                                                        repo_name)
    pull_request_data = ('{{"title": "{}", "head": "{}:master",'
	                     ' "base": "master"}}'.format(
                         environment['github_pull_request_title'],
                         environment['github_username']))

    def mock_pull_request(arguments_list):
        return arguments_list

    @mock.patch('subprocess.check_output', side_effect = mock_pull_request)
    def testPullRequestToGithub(self, mock_subprocess):
        result = repo_scan.pull_request_to_github(self.main_repo_user, 
		                                          self.repo_name, 
												  self.environment)
        assert result == ['curl', '--user', self.auth_string, self.url, 
		                  '-d', self.pull_request_data], self.result

#Tests the create_fork method, which creates a fork
#of a remote repository.  This test does not actually
#create a fork and replaces the call with a mock.
class createForkTestCase(unittest.TestCase):
    environment = {}
    environment['github_username'] = 'test_username'
    main_repo_user = 'test_username_main'
    repo_name = 'test_repo_name'

    fork_string = '{}/{}'.format(main_repo_user, repo_name)
    fork_command = ['git', 'hub', 'fork', fork_string]

    def mock_fork(arguments_list):
        return arguments_list

    @mock.patch('subprocess.check_output', side_effect = mock_fork)
    def testFork(self, mock_subprocess):
        result = repo_scan.create_fork(self.repo_name, self.main_repo_user, 
		                               self.environment)
        assert result == self.fork_command

#This tests the check_fork_exists method, which determines
#if a fork of a remote repository exists.
class checkForkExistsTestCase(unittest.TestCase):
    fork_exists = ('https://api.github.com/repos/abuhmantest/test_webhooks')
    fork_not_exists = 'https://api.github.com/repos/test_user/test_fork'

    def testForkExists(self):
        assert repo_scan.check_fork_exists(self.fork_exists)
    def testForkNotExists(self):
        assert not repo_scan.check_fork_exists(self.fork_not_exists)

#Tests the find_file_location method that dynamically
#finds a file in a directory.
class findFileLocationTestCase(unittest.TestCase):
    directory = './'
    file_name = 'configuration.YAML'

    location = repo_scan.find_file_location(directory, file_name)

    def testFileLocation(self):
         assert self.location == './test2/', self.location

if __name__ == "__main__":
    unittest.main()
