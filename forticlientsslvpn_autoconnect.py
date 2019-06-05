import poplib
import pexpect
import time
import sys
import json
from email.parser import Parser

with open('config.json') as config_file:
    config = json.load(config_file)

server = config.get('server')
vpnuser = config.get('vpnuser')
vpnpassword = config.get('vpnpassword')
email = config.get('email')
emailpassword = config.get('emailpassword')
popserver = config.get('popserver')
port = config.get('port')
route = config.get('route')

child = pexpect.spawn('./forticlientsslvpn_cli --server {} --vpnuser {}'.format(server, vpnuser))
child.expect('Password for VPN:')
child.sendline(vpnpassword)
child.expect('Would you like to connect to this server')
child.sendline('Y')
child.expect('An email message containing a Token Code')

print 'Login successful. Waiting for email...'
time.sleep(10)

M = poplib.POP3_SSL(popserver)
M.user(email)
M.pass_(emailpassword)
lines = M.retr(len(M.list()[1]))[1] # last message
msg_content = b'\r\n'.join(lines).decode('utf-8')
msg = Parser().parsestr(msg_content)
code = msg.get_payload(decode=True)[34:40] # extract 6 digit code

child.sendline(code)
child.expect('STATUS::Login succeed')
child.logfile = sys.stdout
child.expect('STATUS::Tunnel running')

print route
pexpect.run(route)

child.interact()
