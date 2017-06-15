import subprocess
print subprocess.check_output(['scancode',
                               'scancode-toolkit-2.0.0.rc2/src/commoncode',
                               '--format','spdx-tv'])
