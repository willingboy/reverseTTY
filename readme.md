# 被动连接内网Linux脚本
## reverse_server.py
- 首先在远程目标主机可以访问的主机运行
- reverse_server.py [port]
## reverse_client.py
- 本机运行环境是Linux
- 在reverse_server.py启动端口监听后再启动
- reverse_client.py -ip [ip] -port [port]