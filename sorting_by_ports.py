#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import ast
import argparse

parser = argparse.ArgumentParser(description="sorting by port number")
parser.add_argument("-f", "--file", required=False, default="fast_scaning_reports", help="input file")
parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.0 (02/16/2014)')

args = parser.parse_args()

input_file = args.file

def find_open_ports(filename, port, service_name):
    f1 = open(filename).read()
    hosts = ast.literal_eval(f1)
    tmp = []
    for host in hosts.keys():
        if str(hosts[host]["ports"]).count(port) == 1:
            tmp.append(host)
        
    if len(tmp) != 0:
        new_file = file(port + "_ports_" + service_name + ".txt", "a")
        for item in tmp:
            new_file.write("%s\n" % item)
        new_file.close()

portmaps = open("ports_map.txt").read()
ports = ast.literal_eval(portmaps)

for port in ports.keys():
    find_open_ports(input_file, port, ports[port])
print "sorting by ports is finished"