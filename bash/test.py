from subprocess import Popen, PIPE, STDOUT

cmd = 'wineconsole 2>&1'
p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
output = p.stdout.read()
print output
