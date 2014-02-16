#!/usr/bin/python
# -*- coding: UTF-8 -*- 

from ftplib import FTP

servers = file("21_ports_FTP.txt").readlines()

for server in servers:
    server = server.strip()
    try:
        print server
        ftp = FTP(server)   # connect to host, default port
        ftp.login()               # user anonymous, passwd anonymous@
        ftp.retrlines('LIST')     # list directory contents
    except Exception, e:
        print e
        pass