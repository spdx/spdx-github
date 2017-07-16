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

from git import Repo

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
        self.spdx_file_name = self.directory[:-1] + '.SPDX'

        #scan the extracted directory and put results in a named file
        repo_scan.scan(self.directory, self.spdx_file_name,
                                    'scancode', 'tag-value')

    def tearDown(self):
        #Remove the scan results file
        remove(self.spdx_file_name)

    def testScan(self):
        assert path.isfile(self.spdx_file_name)


#This checks whether the check_valid_url method correctly determines
#whether a url results in an error (400 or 500 code).
class CheckURLTestCase(unittest.TestCase):
    good_url = 'https://www.google.com/'
    bad_url = 'https://www.google.com/fail'

    def testGoodURL(self):
        assert repo_scan.check_valid_url(self.good_url) == True

    def testBadURL(self):
        assert repo_scan.check_valid_url(self.bad_url) == False

class GetConfigTestCase(unittest.TestCase):
    from spdx_github import repo_scan
    configExisting = repo_scan.get_config_yml('./', 'test.yml')
    configNotExisting = repo_scan.get_config_yml('test/', 'test.yml')

    def testExistingConfig(self):
        assert self.configExisting['output_file_name'] == 'file_name.SPDX'
        assert self.configExisting['output_type'] == 'rdf'

    def testNotExistingConfig(self):
        assert self.configNotExisting['output_file_name'] == 'test.SPDX'
        assert self.configNotExisting['output_type'] == 'tag-value'

class SyncRepoTestCase(unittest.TestCase):
    repo_path = './test_repo'
    main_repo_user = 'abuhman'
    repo_name = 'test_webhooks'
    repo = Repo.init(repo_path)
    repo_scan.sync_main_repo(repo_path, main_repo_user, repo_name, repo)

    main_repo_url = ('https://www.github.com/' + main_repo_user + '/'
                     + repo_name + '.git')
    origin = repo.create_remote('origin', main_repo_url)
    repo.git.fetch()
    output_string = repo.git.diff('origin/master')
    repo.delete_remote(origin)

    def testRepoSynced(self):
        assert self.output_string == ""

class MakeCommitTestCase(unittest.TestCase):
    file_name = 'test.yml'
    subprocess.check_output(['cp', file_name, './test_repo'])
    repo = Repo.init('./test_repo')
    environment = {}
    environment['name'] = 'TEST_NAME'
    environment['email'] = 'TEST_EMAIL'
    environment['commit_message'] = 'TEST_MSG'
    repo_scan.commit_file(file_name, repo, environment)

    headcommit = repo.head.commit

    def tearDown(self):
        main_repo_user = 'abuhman'
        repo_name = 'test_webhooks'
        main_repo_url = ('https://www.github.com/' + main_repo_user + '/'
                         + repo_name + '.git')

        origin = self.repo.create_remote('origin', main_repo_url)
        origin.fetch()
        self.repo.git.reset('--hard','origin/master')

    def testCommitMade(self):
        assert self.headcommit.author.name == 'TEST_NAME'



if __name__ == "__main__":
    unittest.main()
