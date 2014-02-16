#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import smtplib

fromaddr = 'test@test.com'
toaddrs  = 'test@test.com'

servers = file("25_ports_SMTP.txt").readlines()
msg = 'This is for test'

for server in servers:
    try:
        server = server.strip()
        print "SMTP Relay Test started on " + server
        server = smtplib.SMTP(server)
        server.sendmail(fromaddr, toaddrs, msg)
        print "SMTP Relay is allowed on " + server + "!!!"
        server.close()
    except Exception, e:
        print e
        pass



    
    
# Gmail Login

# fromaddr = 'fromuser@gmail.com'
# toaddrs  = 'touser@gmail.com'
# msg = 'Enter you message here'

# server = smtplib.SMTP("smtp.gmail.com:587")
# username = 'enter your email'
# password = 'password'
# server.starttls()
# server.login(username,password)
# server.sendmail(fromaddr, toaddrs, msg)

