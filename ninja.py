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
import os
import multiprocessing as mp
import time
import chardet
from pymongo import MongoClient

class web:

    user_agents = [
        "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)"
    ]

    connection = MongoClient()
    db = connection.crwaler  # crwaler is database name
    ncores = mp.cpu_count()

    def __init__(self, collection_saving_urls, cookie_filename, attack_strings_filename, timeout, origin_url):

        # connect the collection
        self.collection_saving_urls = self.db[collection_saving_urls]

        # initialize values
        self.cookie = self.read_cookie_from_file(cookie_filename)
        self.attack_commands = self.read_attack_strings_from_file(attack_strings_filename)
        self.timeout = self.set_timeout(timeout)
        self.origin_url = self.make_origin_url(origin_url)


    def __del__(self):
        self.connection.close()
        print "connection close gracefully"


    def make_origin_url(self, origin_url):

        if origin_url.find("http") != -1:
            return urlparse(origin_url)[1]

        else:
            origin_url = "http://" + origin_url
            return urlparse(origin_url)[1]

    def read_cookie_from_file(self, cookie_filename):

        try:
            f = open(cookie_filename).read()
            return str(f).strip()
        except:
            return None

    def read_attack_strings_from_file(self, attack_strings_filename):

        try:
            attack_commands = file(attack_strings_filename).read()
            return attack_commands.split("\n")

        except:
            print "[+] there is no attack string file"
            print "[+] connection is closing"
            self.connection.close()
            print "[+] Bye Bye ~"
            sys.exit(0)

    def set_timeout(self, timeout):

        if timeout:
            return int(timeout)
        #dafault timeout is 1
        return 1

    def predict_attack_time(self):

        attack_command_len = len(self.attack_commands)
        urls = []
        cnt = 0

        for url in self.collection_saving_urls.find({"res_code": "200"}, {"url": 1}).sort("url", 1):
            urls.append(url["url"])

        for url in urls:
            payloads = parse_qs(urlparse(url).query)
            payloads_number = len(payloads.keys())
            cnt += payloads_number

        all_count = cnt * attack_command_len * 3
        all_count_str = str(all_count)
        estimate_time = str((all_count * attack_command_len * 0.005))
        print "*" * 120
        print "total attack request will be " + all_count_str
        print "attack estimate time will be " + estimate_time + " minutes"
        print "*" * 120


    def partition(self, lst, n):
        return [lst[i::n] for i in xrange(n)]


    def search_urls(self):

        urls = []
        for url in self.collection_saving_urls.find({"res_code": {"$ne" : 200}}, {"url": 1}).sort("url", 1):
            urls.append(url["url"])
        return self.partition(urls, self.ncores)


    def attack(self, payloads, method, action, case):

        for name in payloads.keys():

            if type(payloads[name]) == list:
                payloads[name] = payloads[name].pop()

            # change to unicode
            if type(payloads[name]) == str:
                payloads[name] = payloads[name].decode('utf-8')
            tmp_value = payloads[name]

            for attack_command in self.attack_commands:
                # change to unicode
                attack_command = attack_command.decode('utf-8')
                payloads[name] += attack_command

                # attack in origin_url
                # form에서 받아오는 action의 경우 전혀 관계없는 경우가 있었음
                if urlparse(action)[1].find(self.origin_url) != -1:
                    self.web_request(payloads, method, action, case)

                payloads[name] = tmp_value


    def make_baseurl(self, url):
        url_tmp = urlparse(url)
        url_1 = url_tmp[0]
        url_2 = url_tmp[1]
        url_3 = url_tmp[2]
        return urlunsplit((url_1, url_2, url_3, '', ''))


    # make parameters from html form
    def make_parameters(self, url):

        br = mechanize.Browser()

        if self.cookie is None:
            br.addheaders = [('User-agent', random.choice(self.user_agents))]

        else:
            br.addheaders = [('User-agent', random.choice(self.user_agents)),\
                             ("Cookie", self.cookie)]

        br.set_handle_equiv(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)

        try:
            br.open(url)

        except Exception as e:
            return False

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


    def attack_case1(self, urls):

        links_to_visit_params = []
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
                    self.attack(payloads, "GET", self.make_baseurl(url), "case1")
                    links_to_visit_params.append(url_with_params)

    # form test
    # two types of action
    # action : https://www.xxx.co.kr/13.sh
    # action : https://www.xxx.co.kr/13.sh?action=loginCheck
    def attack_case2(self, urls):

        links_to_visit_params = []
        # links_to_visit_params later to queue

        for url in urls:
            results = self.make_parameters(url)
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

                        # action : https://www.xxx.co.kr/13.sh?action=loginCheck

                        if len(urlparse(action)[4]) != 0:

                            # merge payload to action=loginCheck
                            payloads = dict(parse_qs(urlparse(action).query), **payloads)
                            url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys()))

                            # to reduce duplicate urls
                            if url_with_params not in links_to_visit_params:

                                # action : https://www.xxx.co.kr/13.sh?action=loginCheck -> action : https://www.xxx.co.kr/13.sh
                                self.attack(payloads, "GET", self.make_baseurl(action), "case2")
                                links_to_visit_params.append(url_with_params)

                        # action : https://www.xxx.co.kr/13.sh
                        else:

                            url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys()))

                            # to reduce duplicate urls
                            if url_with_params not in links_to_visit_params:
                                self.attack(payloads, "GET", action, "case2")
                                links_to_visit_params.append(url_with_params)

                    elif method == "POST":

                        # action : https://www.xxx.co.kr/13.sh?action=loginCheck
                        if len(urlparse(action)[4]) != 0:

                            # merge payload to action=loginCheck
                            payloads = dict(parse_qs(urlparse(action).query), **payloads)
                            url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys()))

                            # to reduce duplicate urls
                            if url_with_params not in links_to_visit_params:

                                # action : https://www.xxx.co.kr/13.sh?action=loginCheck -> action : https://www.xxx.co.kr/13.sh
                                self.attack(payloads, "POST", self.make_baseurl(action), "case3")
                                links_to_visit_params.append(url_with_params)

                        else:

                            # action : https://www.xxx.co.kr/13.sh
                            url_with_params = str(urlparse(action)[2]) + str(sorted(payloads.keys()))
                            # to reduce duplicate urls
                            if url_with_params not in links_to_visit_params:
                                self.attack(payloads, "POST", action, "case3")
                                links_to_visit_params.append(url_with_params)


    def web_request(self, payloads, method, action, case):

        url_scheme = urlparse(action)[0]
        url_location = urlparse(action)[1]
        url_area = urlparse(action)[2]
        action = urlunsplit((url_scheme, url_location, url_area, "", ""))

        if method == "GET" and case == "case1":
            try:
                if self.cookie is None:
                    try:
                        res = requests.get(action, timeout=self.timeout,
                                           headers={"User-Agent": random.choice(self.user_agents)},
                                           verify=False,
                                           params=payloads)

                        self.save_data(method, case, str(url_location), None, res)

                    except (KeyboardInterrupt, SystemExit):
                        self.connection.close()
                        sys.exit(0)

                    except Exception as e:
                        pass

                    else:
                        pass

                else:

                    try:
                        res = requests.get(action, timeout=self.timeout,
                                           headers={"User-Agent": random.choice(self.user_agents),
                                                    "Cookie": self.cookie},
                                           verify=False,
                                           params=payloads)

                        self.save_data(method, case, str(url_location), None, res)

                    except (KeyboardInterrupt, SystemExit):
                        self.connection.close()
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

                if self.cookie is None:

                    try:
                        res = requests.get(action, timeout=self.timeout,
                                           headers={"User-Agent": random.choice(self.user_agents)},
                                           params=payloads,
                                           verify=False)

                        self.save_data(method, case, str(url_location), None, res)

                    except (KeyboardInterrupt, SystemExit):
                        self.connection.close()
                        sys.exit(0)

                    except Exception as e:
                        pass

                    else:
                        pass

                else:

                    try:

                        res = requests.get(action, timeout=self.timeout,
                                           headers={"User-Agent": random.choice(self.user_agents),
                                                    "Cookie": self.cookie},
                                           verify=False,
                                           params=payloads)

                        self.save_data(method, case, str(url_location), None, res)

                    except (KeyboardInterrupt, SystemExit):
                        self.connection.close()
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
                if self.cookie is None:

                    try:

                        res = requests.post(action, timeout=self.timeout,
                                            headers={"User-Agent": random.choice(self.user_agents)},
                                            data=payloads,
                                            verify=False)

                        self.save_data(method, case, str(url_location), payloads, res)

                    except (KeyboardInterrupt, SystemExit):
                        self.connection.close()
                        sys.exit(0)

                    except Exception as e:
                        pass

                    else:
                        pass

                else:

                    try:

                        res = requests.post(action, timeout=self.timeout,
                                            headers={"User-Agent": random.choice(self.user_agents),
                                                     "Cookie": self.cookie},
                                            verify=False,
                                            data=payloads)

                        self.save_data(method, case, str(url_location), payloads, res)

                    except (KeyboardInterrupt, SystemExit):

                        self.connection.close()
                        sys.exit(0)

                    except Exception as e:
                        pass

                    else:
                        pass

            except Exception as e:
                print action
                print e