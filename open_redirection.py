#!/usr/bin/python
# -*- coding: UTF-8 -*-

import ninja
import argparse
import timeit
import multiprocessing as mp
from urlparse import urlparse
import sys

# save_data의 경우는 함수마다 공격의 결과값을 판단하는 패턴이 다르므로 개별로 정의
class open_redirection(ninja.web):

    def __init__(self, collection_saving_urls):

        # connect the collection
        self.collection_saving_urls = self.db[collection_saving_urls]


    def save_data(self, urls):

        self.collection_saving_results = self.db["report"]

        for url in urls:

            if urlparse(url)[4].find("http") != -1 or\
                urlparse(url)[4].find("jsp") != -1 or\
                urlparse(url)[4].find("php") != -1 or\
                urlparse(url)[4].find("asp") != -1:

                print url

                self.collection_saving_results.insert({"url" : url,
                                                "open redirection" : True
                                                })


if __name__ == "__main__":

    usage        = '''./open_redirection.py -t testfire '''

    parser = argparse.ArgumentParser(description = "open_redirection attack for pen testing",
                                     usage = usage)
    parser.add_argument("-t", "--table", required=True, help="collection that saved urls")
    parser.add_argument("-p", "--payload", required=False, help="payload characters to attack")
    parser.add_argument("-u", "--url", required=False, help="requests in origin_url")
    parser.add_argument("-c", "--cookie", required=False, help="filename that contains a cookie")
    parser.add_argument("-o", "--timeout", required=False, help="default timeout is 1 sec")
    parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.1 (05/05/2014)')

    args = parser.parse_args()

    collection_saving_urls = args.table

    timeout = args.timeout

    start_time = timeit.default_timer()

    os_version = sys.platform

    open_redirection = open_redirection(collection_saving_urls)

    processes = []

    # 공격에 필요한 url을 테이블에서 가져옴
    urls = open_redirection.search_urls()

    if os_version.find("win32") == -1:

        for url in urls:
            process = mp.Process(target = open_redirection.save_data, args=(url,))
            processes.append(process)
            process.start()

        for item in processes:
            item.join()

    else:
        for url in urls:
            process = mp.Process(target = open_redirection.save_data(url))


    end_time = timeit.default_timer()
    print "*" * 120
    print '\nattack is done: ', end_time - start_time
    print "*" * 120