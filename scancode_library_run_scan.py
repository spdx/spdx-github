import scancode
from scancode import api

print("Hello World")
ordered_dictionary = api.get_licenses("../scancode-toolkit-2.0.0.rc2/src/commoncode")
for i in ordered_dictionary:
	print(i + "Printing\n")
print("Goodbye")
