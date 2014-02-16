#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import ast
import argparse

parser = argparse.ArgumentParser(description="sorting by ip address")
parser.add_argument("-f", "--file", required=False, default="fast_scaning_reports", help="input file")
parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.0 (02/16/2014)')

args = parser.parse_args()

input_file = args.file

f1 = open(input_file).read()
hosts = ast.literal_eval(f1)
for host in hosts.keys():
    if hosts[host]["ports"] != []:
        tmp = []
        filename = host + ".txt"
        report = file(str(filename), 'w')
        tmp = hosts[host]["ports"]
        tmp_len = len(hosts[host]["ports"])
        for i in range(tmp_len):
            port = tmp.pop()
            report.write(str(port) + "\n")
        report.close()
print "sorting by ip is finished"
        