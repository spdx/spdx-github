import unittest
from os import path, remove
import subprocess

class scanRDFOutput(unittest.TestCase):
	input_file_name = 'test.py'
	output_file_name = 'test.SPDX'
	def setUp(self):
		#scan the file and put results in output file
		print subprocess.check_output(['scancode','--format', 'spdx-rdf',self.input_file_name,self.output_file_name])

	def tearDown(self):
		#Remove the scan results file
		remove(self.output_file_name)

	def testScan(self):
		assert path.isfile(self.output_file_name)

if __name__ == "__main__":
	unittest.main()
