import subprocess

#This curl command from the command line works:
#curl --user "abuhman" https://api.github.com/users/abuhman

#This subprocess call to the same curl command returns "Bad credentials"
print subprocess.check_output(['curl', '--user', '"abuhman"', 'https://api.github.com/users/abuhman'])
