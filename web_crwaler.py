#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import requests 
from bs4 import BeautifulSoup 
import re 
from urlparse import urlparse 
from urlparse import urljoin 
from urlparse import urlunsplit
from urlparse import parse_qs
import os, sys 
import timeit 
import hashlib 
import random 
import sqlite3 
import base64
import argparse


# drop table
def drop_table(table_name): 
    try: 
        query = "DROP table IF EXISTS %s" %(table_name) 
        cur.execute(query) 
        conn.commit() 
        print "drop %s table" %(table_name) 
    except Exception as e: 
        print e 
        print "can't drop %s table" %(table_name) 


# create table   
def create_table(table_name): 
    try: 
        query = "CREATE TABLE IF NOT EXISTS " + table_name + \
                "(id INTEGER PRIMARY KEY NOT NULL,"\
                "url text unique,"\
                "res_code text,"\
                "res_content text,"\
                "verb text,"\
                "admin text,"\
                "integer_overflow text,"\
                "buffer_overflow text,"\
                "sqli text,"\
                "xss text,"\
                "lfi text,"\
                "rfi text)"
        cur.execute(query) 
        conn.commit() 
        print "created %s table" %(table_name) 
    except Exception as e: 
        print e 
        print "can't create %s table" %(table_name) 


# insert the url, response code, and response content
# if you save response content, the size will grow up
def insert_data(url, res_code, res_content): 
    try:
        cur.execute("select url from " + table_name + " where url == (?)", [url]) 

        if cur.fetchone() is None: 
            res_content = base64.b64encode(res_content) 
            cur.execute("insert into " + table_name + " (url, res_code) values(?, ?)", [url, res_code]) 
#             cur.execute("insert into " + table_name + " (url, res_code, res_content) values(?, ?, ?)", [url, res_code, res_content]) 
            conn.commit()
            print "insert the %s" %(url) 
        else: 
            print "you already visited the %s" %(url) 

    except Exception as e: 
        print e 


# after finish scanning, it will show the summary
def result_sumarize(table_name): 
    try:
        cur.execute("select count(url) from " + table_name) 
        url_number = cur.fetchone()[0] 

        cur.execute("select count(url) from " + table_name + " where res_code == '200'") 
        res_code_200 = cur.fetchone()[0] 

        cur.execute("select count(url) from " + table_name + " where res_code == '404'") 
        res_code_404 = cur.fetchone()[0] 

        cur.execute("select count(url) from " + table_name + " where res_code == '500'") 
        res_code_500 = cur.fetchone()[0] 

        cur.execute("select url from " + table_name) 

        urls = [] 

        for row in cur: 
            urls.append(row[0]) 

        return urls, url_number, res_code_200, res_code_404, res_code_500 

    except Exception as e: 
        print e 
        pass 


# extract url from form_tag
def scoop_forms_beautiful_soup(html_page_contents, url): 
    action = "" 

    url_scheme = urlparse(url)[0] 
    url_location = urlparse(url)[1] 

    # res_content = base64.b64decode(html_page_contents) 
    # html_page_contents = unicode(res_content, 'euc-kr').encode('utf-8') 
    b = BeautifulSoup(html_page_contents) 

    result = set([]) 

    for tag in b.findAll('form'): 

        try: 
            if tag["action"]: 
                action = urlunsplit((url_scheme, url_location, tag["action"], "", "")) 
                result.add(action) 

        except Exception as e:
            pass 

    return result 


# extract url from a tag
def scoop_hrefs_beautiful_soup(html_page_contents):
    links = []
    try :
        b = BeautifulSoup(html_page_contents)
    except :
        pass
    else: 
        for tag in b.findAll('a', href=True):
            links.append(tag['href'])
    return links

 

href_regexp = re.compile('<a\s+href\s*?="\s*?(.*?)"', \
        re.IGNORECASE | re.MULTILINE)


# extract href tag
def scoop_hrefs_regexp(html_page_contents):
    return href_regexp.findall(html_page_contents)

 
# union tags from scoop_forms_beautiful_soup and scoop_hrefs_beautiful_soup
def scoop_hrefs(html_page_contents, url):
    return set.union(set(scoop_hrefs_beautiful_soup(html_page_contents)), \
                     set(scoop_hrefs_regexp(html_page_contents)))
#                      scoop_forms_beautiful_soup(html_page_contents, url))

   
# extract the domain name
def domain_name(url):
    return urlparse(url)[1]


# a.jsp -> http://test.com/a.jsp
def href2url(originating_page, href):
    
    # if href starts with http
    if href.find("http") != -1:
        href = href.strip()
        return href

    else:
        
        href = href.strip()
        
        try:
            pieces = urlparse(urljoin(originating_page, href))
            
        except Exception as e: 
            print e 
            return ""
        url_scheme = pieces[0]
        url_location = pieces[1]
        url_path = pieces[2]
        url_parameter = pieces[3]
        url_query = pieces[4]
        
        # don't follw http://www.google.com/q=test
        return  urlunsplit((url_scheme, url_location, url_path, "", ""))
    
        # follw http://www.google.com/q=test
#         return  urlunsplit((url_scheme, url_location, url_path, url_query, url_parameter))


def extract_all_href_links(page_contents, url_matching_pattern):
    base_pattern = urlparse(url_matching_pattern)[1]
    links_on_page = scoop_hrefs(page_contents, url_matching_pattern)
    universal_links = set([])
    for link in links_on_page:
        u = href2url(url_matching_pattern, link)
        # urlparse(u)[1].find(base_pattern) != -1 to get rid of http://www.facebook.com/sharer/sharer.php?s=100&p[url]=http%3A%2F%2Fwww.test.com%2Fbbs%2Fboard.php
        if (u.startswith('http')) and urlparse(u)[1].find(base_pattern) != -1:
            universal_links.add(u)
    return universal_links


def file_extension(filename) :
    (base, ext) = os.path.splitext(filename)
    if (ext == '.' or ext == ''):
      return ''
    else :
      return ext[1:]

 

terminal_extensions = set([ \

  # text file extensions
  'doc', 'docx', 'log', 'msg', 'pages','rtf', 'tt', 'wpd', 'wps', 'css', \

  # data file extensions
  'accdb', 'blg', 'dat', 'db', 'efx','mdb', 'pdb', 'pps', 'ppt', \
  'pptx', 'sdb', 'sdf', 'sql', 'vcf', 'wks','xls', 'xlsx', \

  # image  file extensions
  'bmp', 'gif', 'jpg', 'png', 'psd', 'psp','thm', 'tif', 'tiff' ,\
  'ai', 'drw', 'eps', 'ps', 'svg', \
  '3dm', 'dwg', 'dxf', 'pln', \
  'indd', 'pct', 'pdf', 'qxd', 'qxp','rels',  \

  # audio file extensions
  'aac', 'aif', 'iff', 'm3u', 'mid', 'mp3','mpa', 'ra', 'wav', 'wma' , \

  # video file extensions
  '3g2', '3gp', 'asf', 'asx', 'avi', 'flv','mov', 'mp4', 'mpg', \
  'rm', 'swf', 'vob', 'wmv', \

  # executable file extensions
  'sys', 'dmp', 'app', 'bat', 'cgi', 'exe','pif', 'vb', 'ws', \

  # compressed file extensions
  'deb', 'gz', 'pkg', 'rar', 'sit', 'sitx','tar', 'gz', 'zip', 'zipx' , \

  # programming file extensions
  'c', 'cc', 'cpp', 'h', 'hpp', 'java', 'pl','f', 'for' , \

  # misc file extensions
  'dbx', 'msi', 'part', 'torrent', 'yps','dmg', 'iso', 'vcd' , \

  # more_audio_file_extensions
   '4mp', 'aa3', 'aac', 'abc', 'adg', 'aif','aifc', 'aiiff', \
   'awb', 'cda', 'cdib', 'dcm', 'dct','dfc', 'efa', 'f64', 'flac', \
   'flp', 'g726', 'gnt', 'imy', 'kfn', 'm3u','m4a', 'm4p', 'm4r', \
   'mid', 'midi', 'mio', 'mmf', 'mp3','mpa', 'mpu', 'msv', 'mt2', \
   'mte', 'mtp', 'mzp', 'oga', 'ogg','omg', 'pvc', 'ra', 'ram', \
   'rif', 'ul', 'usm', 'vox', 'wav', 'wma', \

   # data_backup_file_extensions
   'abbu', 'alub', 'asd', 'bac', 'bak','bbb', 'bks', 'bup', 'dkb', \
   'dov', 'bk', 'nbf', 'qbb', 'qbk', 'tmp','xlf', \
 
   # video_file_extensions
   'aaf', 'asf', 'avi', 'cvc', 'ddat', 'divx','dmb', 'dv',  \
   'evo', 'f4v', 'flc', 'fli', 'flv', 'giv','m1pg', 'm21' \
   'mj2', 'mjp', 'mp4', 'mp4v', 'mpeg','mpeg4', 'mpg2', \
   'mts', 'svi', 'tivo', 'vob', 'wmv','wmmp', \
   
  ])


def has_http_in_path(url):
    c = urlparse(url)
    if (c[2].find('http') >= 0) or(c[3].find('http') >= 0):
        return True
    else:
        return False


def decide_which_links_to_follow(terminal_extensions, page_links):
    links_to_follow = set([])

    for link in page_links:
         if ( (link.find(cononical_url) != -1 )and \
              (file_extension(link).lower()not in terminal_extensions) and
              (not has_http_in_path(link))):
             links_to_follow.add(link)
    return links_to_follow

    
def add_links_to_frontier_1(page_links, links_to_visit):
    links_to_visit.add(page_links)
    return links_to_visit


def add_links_to_frontier_2(page_links, url_matching_pattern):
    links_not_to_visit = {}
    links_not_to_visit[url_matching_pattern] = []
    if len(page_links) > 0:
        for page_link in page_links:
            links_not_to_visit[url_matching_pattern].append(page_link)
    return links_not_to_visit


def add_links_to_frontier_3(page_contents_enc, links_to_visit_enc):
    if type(page_contents_enc) == str:
        links_to_visit_enc.add(page_contents_enc)
        return links_to_visit_enc
    return links_to_visit_enc


def add_links_to_frontier_4(page_links, links_to_visit_params):
    links_to_visit_params.add(page_links)
    return links_to_visit_params


def add_404_pages(page_links, page_code_404):
    page_code_404.add(page_links)
    return page_code_404


def add_500_pages(page_links, page_code_500):
    page_code_500.add(page_links)
    return page_code_500

def make_baseurl(url):
    url_tmp = urlparse(url)
    url_1 = url_tmp[0]
    url_2 = url_tmp[1]
    url_3_start = url_tmp[2].rfind("/")
    url_3 = url_tmp[2][:url_3_start + 1]
    return urlunsplit((url_1, url_2, url_3,'', ''))


def done_check(links_not_to_visit, links_to_visit):
    for link_key in links_not_to_visit.keys():
        for link in links_not_to_visit[link_key]:
            if link not in links_to_visit:
                return False
    return True


def array_to_string(arrays):
    if arrays:
        strings = ','.join(arrays)
        return strings.replace(",", "\r\n")
    return ""


def get_all_links(url, url_matching_pattern, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params):
     
    user_agents = ["Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36", \
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36", \
                   "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36", \
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2", \
                   "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0", \
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0", \
                   "Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))", \
                   "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)"
                   ]

    try:
        
        payloads = parse_qs(urlparse(url).query)
        
        # from {u'action': [u'M01']} to {u'action': u'M01'} 
        for name in payloads.keys(): 
            payloads[name] = payloads[name][0]
        
        # test.com/goods_list.php?Index=291 -> /goods_list.php['Index']
        url_with_params = str(urlparse(url)[2]) + str(sorted(payloads.keys()))
        
        links_to_visit_params = add_links_to_frontier_4(url_with_params, links_to_visit_params)
        
        links_to_visit = add_links_to_frontier_1(url, links_to_visit)

        res = requests.get(url, timeout = 0.8, headers = {"User-Agent" : random.choice(user_agents)},
                           verify = False)
        
        res_contents = res.content 
        res_code = res.status_code 
    
        insert_data(url, str(res_code), res_contents)
        
        if (res_code == 200):

            page_contents_enc = hashlib.sha1(res_contents).digest().encode("hex")
            
            if page_contents_enc not in links_to_visit_enc:

                links_to_visit_enc = add_links_to_frontier_3(page_contents_enc, links_to_visit_enc)
                url_base = make_baseurl(url_matching_pattern)
                
                page_links = extract_all_href_links(res_contents, url_base)
                
                follow_links = decide_which_links_to_follow(terminal_extensions, page_links)
                
                links_not_to_visit = add_links_to_frontier_2(follow_links, url)

                return links_not_to_visit, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params
            
            else:
                return {}, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params

        elif res_code == 404:
            page_code_404 = add_404_pages(url, page_code_404)
            return {}, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params
        
        elif res_code == 500:
            page_code_500 = add_500_pages(url, page_code_500)
            return {}, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params
        
        else:
            return {}, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params

    except (KeyboardInterrupt, SystemExit):
        
        urls, url_number, res_code_200, res_code_404, res_code_500 = result_sumarize(table_name)

        cur.close()
            
        end_time = timeit.default_timer() 
            
        print "*" * 50 
        for url in urls: 
            print url 
        print "*" * 50 
            
        print "the number of all url is %s" % (url_number) 
        print "the number of url with code 200 is %s" % (res_code_200) 
        print "the number of url with code 404 is %s" % (res_code_404) 
        print "the number of url with code 500 is %s" % (res_code_500) 
        print '\nwebcrwal is done: ', end_time - start_time
        
        sys.exit(0) 
    
    except Exception as e:
        return {}, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params
    
    else:
        return {}, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params


def not_to_visit_urls(links_not_to_visit, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params):

    if links_not_to_visit == {}:
        return links_not_to_visit, links_to_visit, links_to_visit_enc

    links_not_to_visit_new = {}

    for link_key in links_not_to_visit.keys():
        for link in links_not_to_visit[link_key]:
            if link not in links_to_visit:
                
                url = link
                payloads = parse_qs(urlparse(url).query)
                
                # from {u'action': [u'M01']} to {u'action': u'M01'} 
                for name in payloads.keys(): 
                    payloads[name] = payloads[name][0]
        
                # test.com/goods_list.php?Index=291 -> /goods_list.php['Index']
                url_with_params = str(urlparse(url)[2]) + str(sorted(payloads.keys()))                
                
                if url_with_params not in links_to_visit_params:
                    # ex) index.do?m=A01 and index.do?m=A01 are totally different
                    # change it to "if url_with_params not in {}:"
                    
                    url = link
                    url_matching_pattern = make_baseurl(url)
                    results = get_all_links(url, url_matching_pattern, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params) 
                      
                    links_not_to_visit_new = dict(results[0], **links_not_to_visit_new)
    
                    links_to_visit = results[1]
                    links_to_visit_enc = results[2]
                    page_code_404 = results[3]
                    page_code_500 = results[4]
                    links_to_visit_params = results[5]
                
    return links_not_to_visit_new, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params


def main():

    usage        = '''./web_crwaler.py -u http://www.google.com -p google.com -t google'''
    
    parser = argparse.ArgumentParser(description = "url crwaler for pen testing", \
                                     usage = usage)
    
    parser.add_argument("-u", "--url", required=True, help="target domain")
    parser.add_argument("-p", "--pattern", required=True, help="string to find target domain")
    parser.add_argument("-t", "--table", required=True, help="table name")
    parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.0 (04/19/2014)')

    args = parser.parse_args()

    global cononical_url
#     cononical_url = "192.168.10.9"

    global table_name 
#     table_name = "wavsep"

    url_to_start = args.url
    cononical_url = args.pattern
    table_name = args.table

    global start_time
    start_time = timeit.default_timer()    
#     url_to_start ="http://192.168.10.9:8080/active/"
    
    url_matching_pattern = url_to_start

    links_not_to_visit = {}
    links_to_visit = set([])
    links_to_visit_enc = set([])
    links_to_visit_params = set([])


    page_code_404 = set([])
    page_code_500 = set([])
    
    global conn
    conn = sqlite3.connect("crawler.db")
    
    global cur
    cur = conn.cursor()
    
    drop_table(table_name) 
    create_table(table_name) 
    
    results = get_all_links(url_to_start,\
                            url_matching_pattern,\
                            links_to_visit,\
                            links_to_visit_enc,\
                            page_code_404,\
                            page_code_500,\
                            links_to_visit_params
                            )
    links_not_to_visit, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params = results

    while True:
        
        links_not_to_visit, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params = not_to_visit_urls(links_not_to_visit, links_to_visit, links_to_visit_enc, page_code_404, page_code_500, links_to_visit_params)
        
#         except (KeyboardInterrupt, SystemExit):
#     sys.exit()
  
        if done_check(links_not_to_visit, links_to_visit):

            urls, url_number, res_code_200, res_code_404, res_code_500 = result_sumarize(table_name) 
      
            cur.close()
            
            end_time = timeit.default_timer() 
            
            print "*" * 50 
            for url in urls: 
                print url 
            print "*" * 50 
            
            print "the number of all url is %s" % (url_number) 
            print "the number of url with code 200 is %s" % (res_code_200) 
            print "the number of url with code 404 is %s" % (res_code_404) 
            print "the number of url with code 500 is %s" % (res_code_500) 
            print '\nwebcrwal is done: ', end_time - start_time
            
            sys.exit() 

if __name__ == "__main__":
    main()