#!/usr/bin/env python3

import sys, os, socket, datetime, time
from shared import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', TCPPORT))
sock.listen(1)

print('Ready to receive commands.')

while True:
    controller, client_address = sock.accept()
    print('Connection from {}.'.format(client_address))
    while True:
        data = read(controller)
        if data == 'test':
            print('Received connection test at ' + time.ctime())

        elif data == MSG_GETNAME:
            send(controller, socket.gethostname())

        elif data == MSG_BYE:
            print('Disconnected.')
            break

        elif data == MSG_SETALGO:
            algo = read(controller)
            os.system('sysctl net.ipv4.tcp_congestion_control=' + algo)

        elif data == MSG_SETTIME:
            recvtime = read(controller)
            if os.name == 'nt':
                t = datetime.fromtimestamp(float(recvtime))
                recvtime = t.strftime('%H:%I:%S') + recvtime.split('.')[1][:3]
                os.system('echo ' + recvtime + ' | recvtime')
            else:
                os.system('date -s @' + recvtime)

            print('Set the time to ' + recvtime)

            send(controller, time.time())

        elif data == MSG_SEND:
            dst = read(controller)
            duration = int(read(controller))
            when = int(read(controller))

            ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ds.connect((dst, TCPPORT + 1))

            while time.time() < when:
                pass

            until = when + duration
            data = b'A' * MTU
            while time.time() < until:
                ds.send(data)

            ds.close()

        elif data == MSG_LISTEN:
            ds = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ds.bind(('0.0.0.0', TCPPORT + 1))
            ds.listen(1)
            print('Listening on data socket, awaiting client.')

            t = int(time.time())
            timings = {}
            for i in range(t, t+MAXTESTDURATION):
                timings[i] = 0

            client, addr = ds.accept()
            print('Client {} connected.'.format(addr))
            while True:
                l = len(client.recv(MTU))
                if l == 0:
                    break
                timings[int(time.time())] += l

            client.close() # Should already be closed, since received_data.length==0 earlier, but just to be sure that the listsock doesn't remain in time-wait
            ds.close()

            first = float('inf')
            for t in timings:
                count = timings[t]
                if count > 0 and t < first:
                    first = t

            results = ''
            for t in range(first + 1, first + 9):
                count = timings[t]
                results += str(count) + ' '
            results = results.strip()

        elif data == MSG_GETRESULTS:
            print('Sending results.')
            send(controller, results)

        else:
            print('Unrecognized command')

