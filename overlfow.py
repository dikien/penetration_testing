#!/usr/bin/python
# -*- coding: UTF-8 -*-

import ninja
import argparse
import timeit
import multiprocessing as mp
import sys

# save_data의 경우는 함수마다 공격의 결과값을 판단하는 패턴이 다르므로 개별로 정의
class overflow(ninja.web):

    # timeout난 것들만 모아서 아래의 함수를 다시 작성
    def save_data(self, method, case, url, payloads, res):

        self.collection_saving_results = self.db["report"]
        print res.url

        res_content = res.content

        intereting_strings = ["sqlerror", "mssql", "oracle"]

        for intereting_string in intereting_strings:

            if res_content.find(intereting_string) != -1:

                # case2 and post
                if payloads:
                    self.collection_saving_results.insert({"url" : url,
                                                "attack name" : "overflow",
                                                "method" : method,
                                                "case" : case,
                                                "payload" : str(res.url) + str(payloads),
                                                "res_code" : res.status_code,
                                                "res_length" : len(str(res.content)),
                                                "res_headers" : str(res.headers),
                                                "res_content" : str(res.content),
                                                "res_time" : res.elapsed.total_seconds()
                                                })
                    print "[+] [%s][%s] %s?%s" %(case, method, url, payloads)
                # case1 and get, case2 and get

                else:
                    self.collection_saving_results.insert({"url" : url,
                                                "attack name" : "overflow",
                                                "method" : method,
                                                "case" : case,
                                                "payload" : res.url,
                                                "res_code" : res.status_code,
                                                "res_length" : len(str(res.content)),
                                                "res_headers" : str(res.headers),
                                                "res_content" : str(res.content),
                                                "res_time" : res.elapsed.total_seconds()
                                                })
                    print "[+] [%s][%s] %s" %(case, method, res.url)


if __name__ == "__main__":

    usage        = '''./overlfow.py -t testfire -p payload/overflow_strings -u demo.testfire.net -c cookie'''

    parser = argparse.ArgumentParser(description = "overlfow attack for pen testing", \
                                     usage = usage)
    parser.add_argument("-t", "--table", required=True, help="collection that saved urls")
    parser.add_argument("-p", "--payload", required=True, help="payload characters to attack")
    parser.add_argument("-u", "--url", required=True, help="requests in origin_url")
    parser.add_argument("-c", "--cookie", required=False, help="filename that contains a cookie")
    parser.add_argument("-o", "--timeout", required=False, help="default timeout is 1 sec")
    parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.1 (05/05/2014)')

    args = parser.parse_args()

    collection_saving_urls = args.table
    attack_strings_filename = args.payload
    origin_url = args.url
    cookie_filename = args.cookie
    timeout = args.timeout
    start_time = timeit.default_timer()

    os_version = sys.platform

    overflow = overflow(collection_saving_urls, cookie_filename, attack_strings_filename, timeout, origin_url)

    # 공격의 예상시간을 출력
    overflow.predict_attack_time()

    processes = []

    # 공격에 필요한 url을 테이블에서 가져옴
    urls = overflow.search_urls()

    if os_version.find("win32") == -1:

        for url in urls:
            process = mp.Process(target = overflow.attack_case1, args=(url,))
            processes.append(process)
            process.start()

        for item in processes:
            item.join()

    else:
        for url in urls:
            process = mp.Process(target = overflow.attack_case1(url))

    processes = []

# case 2,3
    if os_version.find("win32") == -1:

        for url in urls:
            process = mp.Process(target = overflow.attack_case2, args=(url,))
            processes.append(process)
            process.start()

        for item in processes:
            item.join()

    else:
        for url in urls:
            process = mp.Process(target = overflow.attack_case2(url))

    end_time = timeit.default_timer()
    print "*" * 120
    print '\nattack is done: ', end_time - start_time
    print "*" * 120