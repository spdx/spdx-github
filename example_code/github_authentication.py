import subprocess

print subprocess.check_output(['curl', '--user', 'abuhman', 'https://api.github.com/users/abuhman'])
