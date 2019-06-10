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

def login_to_vpn(forticlient):
    forticlient.expect('Password for VPN:')
    forticlient.sendline(vpnpassword)
    forticlient.expect('Would you like to connect to this server')
    forticlient.sendline('Y')
    forticlient.expect('An email message containing a Token Code')
    print 'Login successful. Waiting for email...'

def wait_for_auth_code_email():
    time.sleep(10)

def connect_to_pop_server():
    connection = poplib.POP3_SSL(popserver)
    connection.user(email)
    connection.pass_(emailpassword)
    return connection

def extract_auth_code(pop_connection):
    lines = pop_connection.retr(len(pop_connection.list()[1]))[1] # last message
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    msg = Parser().parsestr(msg_content)
    return msg.get_payload(decode=True)[34:40] # extract 6 digit code

def enter_auth_code(forticlient, code):
    forticlient.sendline(code)
    forticlient.expect('STATUS::Login succeed')
    forticlient.logfile = sys.stdout
    forticlient.expect('STATUS::Tunnel running')

def setup_static_route(route):
    print route
    pexpect.run(route)


forticlient = pexpect.spawn('./forticlientsslvpn_cli --server {} --vpnuser {}'.format(server, vpnuser))

login_to_vpn(forticlient)

wait_for_auth_code_email()
code = extract_auth_code(connect_to_pop_server())
enter_auth_code(forticlient, code)

setup_static_route(route)

forticlient.interact()
