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

def loginToVPN(forticlient):
    forticlient.expect('Password for VPN:')
    forticlient.sendline(vpnpassword)
    forticlient.expect('Would you like to connect to this server')
    forticlient.sendline('Y')
    forticlient.expect('An email message containing a Token Code')
    print 'Login successful. Waiting for email...'

def waitForAuthCodeEmail():
    time.sleep(10)

def connectToPOPServer():
    connection = poplib.POP3_SSL(popserver)
    connection.user(email)
    connection.pass_(emailpassword)
    return connection

def extractAuthCode(popConnection):
    lines = popConnection.retr(len(M.list()[1]))[1] # last message
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    msg = Parser().parsestr(msg_content)
    code = msg.get_payload(decode=True)[34:40] # extract 6 digit code

def enterAuthCode(forticlient, code):
    forticlient.sendline(code)
    forticlient.expect('STATUS::Login succeed')
    forticlient.logfile = sys.stdout
    forticlient.expect('STATUS::Tunnel running')

def setupStaticRoute():
    print route
    pexpect.run(route)


forticlient = pexpect.spawn('./forticlientsslvpn_cli --server {} --vpnuser {}'.format(server, vpnuser))

loginToVPN(forticlient)

waitForAuthCodeEmail()
code = extractAuthCode(connectToPOPServer())
enterAuthCode(forticlient, code)

setupStaticRoute()

forticlient.interact()
