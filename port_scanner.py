#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import timeit
import netaddr
import multiprocessing
import threading
import Queue
import socket
import sys
import os
import glob
import ast
import argparse

lock = threading.Lock()
scan_result = {}        

# merge dictionary1 and dictionary1.
def combineDicts(dictionary1, dictionary2):
    output = {}
    for item, value in dictionary1.iteritems():
        output[item] = {"ports" : dictionary1[item]["ports"] + dictionary2[item]["ports"]}
    return output

# merge each of files to one result file.
def merge_pieces(files, ip):
    ip = ip.replace("/","_")
    merge = {}
    if len(files) > 1:
        for index in range(len(files)):
            if index == len(files) - 1:
                filename = "fast_scaning_reports_"+ str(ip)
                report = file(filename, 'w')
                report.write(str(merge))
                report.close()
                return merge
            if index == 0:  
                input_1 = file(files[index]).read()
                os.remove(files[index])
                input_2 = file(files[index + 1]).read()
                os.remove(files[index + 1])
                input_1_dict = ast.literal_eval(input_1)
                input_2_dict = ast.literal_eval(input_2)
                merge = combineDicts(input_1_dict, input_2_dict)
            if index > 0:
                input_2 = file(files[index + 1]).read()
                os.remove(files[index + 1])
                input_2_dict= ast.literal_eval(input_2)
                merge = combineDicts(merge, input_2_dict)
    if len(files) == 1:
        os.rename(files[0], 'fast_scaning_reports_' + str(ip))

# not used
def save_file(scan_result, ident):
#     time_stamp = time.strftime("%Y-%m-%d-%H-%M")
    filename = 'jongwon\'s_fast_scaning_' + str(ident)
    report = file(filename, 'w')
    report.write(str(scan_result))
    report.close()
#     json.dump(scan_result, report, ensure_ascii=False)
#     report.write(unicode(json.dumps(scan_result, ensure_ascii=False)))


def syn_scan(ident, victims, ports):
    port_queue = Queue.Queue()
    
    for victim in victims:
        threads = []
        for port in ports:
            port_queue.put(port)

        for i in range(1,7):
            thread = threading.Thread(target=portscan, args=(i, victim, port_queue))
            threads.append(thread)
            thread.setDaemon(True)
            thread.start()
    
        for thread in threads: thread.join()
    save_file(scan_result, ident) 

    
def portscan(ident,ip, port_queue):
    global lock
    while True:
        port = 0
        try:
            port = port_queue.get(block=False)
        except:
            return(0)

        # Begining port scanning
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        response = s.connect_ex((str(ip), int(port)))
        if not response:
            lock.acquire()
            print 'IP %s, port: %d open' %(str(ip),int(port))
            scan_result[str(ip)]["ports"].append(str(port))
            lock.release()
    
def main():
    description = "multi-process port scanner"
    usage        = '''./port_scanner.py -ip 192.168.10.0/24 -p 50
       ./port_scanner.py -ip 192.168.10.0/24 -port 80-443 -p 50
       ./port_scanner.py -ip 192.168.10.1,192.168.10.2,192.168.10.3 -port 80-443 -p 50'''
    
    parser = argparse.ArgumentParser(description = "multi-process port scanner", \
                                     usage = usage)
    
    parser.add_argument("-ip", "--target", required=True, help="target IP for your scan")
    parser.add_argument("-port", "--ports", required=False, 
                        default=ast.literal_eval(open("ports_map.txt").read()),
                        help="target ports for your scan")
    parser.add_argument("-p", "--process", required=False, default="1", help="the number of process for your scan")
    parser.add_argument("-v", "--version", action='version', version = 'JongWon Kim (dikien2012@gmail.com)\n%(prog)s - v.1.0 (02/16/2014)')

    args = parser.parse_args()

    ip = args.target
    threads = int(args.process)
    port = args.ports

#sorting port numbers    
    if type(port) == dict:
        ports = []
        for port_number in port.keys():
            ports.append(port_number)
    
    elif port.find(",") != -1 and type(port) != dict:
        tmp = []
        tmp1 = []
        tmp = port.split(",")
        for i in range(int(tmp[0]), int(tmp[1]) + 1):
            tmp1.append(i)
        ports =  tmp1
    
    elif port.find("-") != -1 and type(port) != dict:
        tmp = []
        tmp1 = []
        tmp = port.split("-")
        print tmp[0], tmp[1]
        for i in range(int(tmp[0]), int(tmp[1]) + 1):
            tmp1.append(i)
        ports =  tmp1
    
    elif type(port) != dict:
        tmp1 = []
        tmp1.append(port)
        ports =  tmp1
        
# sorting ip address
    if ip.find("/") != -1:
        victims = netaddr.IPNetwork(ip)
    else:
        if ip.find(",") != -1:
            victims = ip.split(",")
            print victims
        else:
            victims = [ip]

    if type(victims) == list:
        if len(victims) != 1:
            if threads > len(victims) or len(victims) / threads == 1:
                print "the number of thread problem!!!"
                sys.exit()
        initial = 0
        chunk   = len(victims) / threads #chuck가 1이되면 안
        final = chunk
        
        for victim in victims:
            scan_result[str(victim)] = {"ports" : []}
        
        print '*' * 50
        print '- Fast Port scanner -'
        print '   Number of threads     :%d' %threads
        print '   Size of each chunk    :%d' %final
        print '   Number of IPs to scan :%d' %len(victims) 
    
        print '- List of Ports -\n', ports
        print '*' * 50
    
        processes = []
    
        for i in range(1, threads + 1):
            subnet = victims[initial:final]
            
            process = multiprocessing.Process(target=syn_scan, args=(i, subnet, ports))
            processes.append(process)
            process.start()
    
            initial = final
            final   = chunk * (i+1)
    
            if (len(victims) - final) < (len(victims) / threads):
                final = len(victims)
    
        for item in processes:
            item.join()
    else:
        if len(victims) != 1:
            if threads > len(victims) or len(victims) / threads == 1:
                print "the number of thread problem!!!"
                sys.exit()
        initial = 1
        chunk   = (victims.size - 2) / threads
        final = chunk
        
        for victim in victims:
            scan_result[str(victim)] = {"ports" : []}
                    
        print '*' * 50
        print '- Fast Port scanner -'
        print '   Number of threads     :%d' %threads
        print '   Size of each chunk    :%d' %final
        print '   Number of IPs to scan :%d' %victims.size
    
        print '- List of Ports -\n', ports
        print '*' * 50
        
        processes = []
        for i in range(1, threads + 1):
            subnet = victims[initial:final]
            
            process = multiprocessing.Process(target=syn_scan, args=(i, subnet, ports))
            processes.append(process)
            process.start()
    
            initial = final
            final   = chunk * (i+1)
    
            if (victims.size - final) < (victims.size / threads):
                final = victims.size - 1

        for item in processes:
            item.join()    
            
    merge_pieces(glob.glob("jongwon*"), ip)

if __name__ == '__main__':
    start_time = timeit.default_timer()
    main()
    end_time = timeit.default_timer()
    print '\nPort scan is done: ', end_time - start_time
    


    

