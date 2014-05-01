#!/usr/bin/python
# -*- coding: UTF-8 -*-

import ninja
import argparse
import timeit
import multiprocessing as mp
from urlparse import urlparse

# save_data의 경우는 함수마다 공격의 결과값을 판단하는 패턴이 다르므로 개별로 정의
class open_redirection(ninja.web):

    def __init__(self, collection_saving_urls):

        # connect the collection
        self.collection_saving_urls = self.db[collection_saving_urls]


    def save_data(self, urls):

        self.collection_saving_results = self.db["report"]

        intereting_strings = ["http", "jsp", "php", "asp"]

        for intereting_string in intereting_strings:

            for url in urls:
                if urlparse(url)[4].find(intereting_string) != -1:

                    print url




if __name__ == "__main__":

    usage        = '''./open_redirection.py -t '''

    parser = argparse.ArgumentParser(description = "open_redirection attack based on error message for pen testing", \
                                     usage = usage)
    parser.add_argument("-t", "--table", required=True, help="collection that saved urls")
    parser.add_argument("-p", "--payload", required=False, help="payload characters to attack")
    parser.add_argument("-u", "--url", required=False, help="requests in origin_url")
    parser.add_argument("-c", "--cookie", required=False, help="filename that contains a cookie")
    parser.add_argument("-o", "--timeout", required=False, help="default timeout is 1 sec")
    parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.1 (05/05/2014)')

    args = parser.parse_args()

    collection_saving_urls = args.table

    attack_strings_filename = args.payload
    attack_strings_filename = ""

    origin_url = args.url
    origin_url = ""

    cookie_filename = args.cookie
    timeout = args.timeout

    start_time = timeit.default_timer()

    open_redirection = open_redirection(collection_saving_urls)


    processes = []

    # 공격에 필요한 url을 테이블에서 가져옴
    urls = open_redirection.search_urls()

    for url in urls:

        # 윈도우 계열의 경우 아래의 명령어를 실행
        # process = mp.Process(target = open_redirection.save_data(url))

        process = mp.Process(target = open_redirection.save_data, args=(url,))
        processes.append(process)
        process.start()

    for item in processes:
        item.join()


    end_time = timeit.default_timer()
    print "*" * 120
    print '\nattack is done: ', end_time - start_time
    print "*" * 120