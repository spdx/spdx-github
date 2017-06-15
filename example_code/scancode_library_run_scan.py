import scancode
from scancode import api

print('Hello World')
ordered_dictionary = api.get_licenses('../scancode-toolkit-2.0.0.rc2/'
                                      'src/commoncode/command.py')
for i in ordered_dictionary:
    print(i)
    print('Printing')
print('Goodbye')
