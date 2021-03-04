# AnyDesk IP resolver
# by github.com/dropsql

import argparse
import ctypes
import socket
import struct
import time

from rich.console import Console

banner = '''
[magenta]
╔═╗╔╗╔╦ ╦ [red]╔ [cyan]╦╔═╗[/cyan] ╗[/red] ╔╦╗╔═╗╔═╗╦╔═
╠═╣║║║╚╦╝ [red]╣ [cyan]║╠═╝[/cyan] ╠[/red]  ║║╠╣ ╚═╗╠╩╗
╩ ╩╝╚╝ ╩  [red]╚ [cyan]╩╩  [/cyan] ╝[/red] ═╩╝╚═╝╚═╝╩ ╩
[white]AnyDesk resolver (windows only!)
author: github.com/dropsql[/white]
[/magenta]
'''

console = Console()
console.print(banner)

parser = argparse.ArgumentParser(usage='%(prog)s [option(s)]')

parser.add_argument('-p', '--port', help='set anydesk port (default: 7070)', default=7070, required=False, metavar='', type=int, dest='port')
parser.add_argument('-t', '--timeout', help='anydesk port timeout (ms, default: 30000)', default=30000, required=False, metavar='', type=int, dest='timeout')

args = parser.parse_args()

ANYDESK_PORT = args.port

DWORD = ctypes.c_ulong

dwSize = DWORD(0)

ctypes.windll.iphlpapi.GetTcpTable('', ctypes.byref(dwSize), 0)

ANY_SIZE = dwSize.value

class TCPROW(ctypes.Structure):
    _fields_ = [('dwState', DWORD),
                ('dwLocalAddr', DWORD),
                ('dwLocalPort', DWORD),
                ('dwRemoteAddr', DWORD),
                ('dwRemotePort', DWORD)]

class TCPTABLE(ctypes.Structure):
    _fields_ = [('dwNumEntries', DWORD),
                ('table', TCPROW * ANY_SIZE)]

tcpTable = TCPTABLE()
tcpTable.dwNumEntries = 0

secs = time.time() + (args.timeout / 1000)

console.log(f'waiting for connection...')

while secs >= time.time():
    if (ctypes.windll.iphlpapi.GetTcpTable(ctypes.byref(tcpTable), ctypes.byref(dwSize), 0) == 0):
        maxNum = tcpTable.dwNumEntries
        placeHolder = -1
        
        while (placeHolder := placeHolder + 1) < maxNum:

            item = tcpTable.table[placeHolder]
            
            RADDR = socket.inet_ntoa(struct.pack('L', item.dwRemoteAddr))
            RPORT = socket.ntohs(item.dwRemotePort)
            LADDR = socket.inet_ntoa(struct.pack('L', item.dwLocalAddr))
            
            portState = item.dwState
            if LADDR != '127.0.0.1' and portState == 5 and RPORT == ANYDESK_PORT:
                console.log(f'remote addr found on port {ANYDESK_PORT}: {RADDR}')
                exit()

console.log('timeout exceeded.')