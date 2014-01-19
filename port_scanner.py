# -*- coding: UTF-8 -*- 
import timeit
import time
import netaddr
import multiprocessing
import threading
import Queue
import socket
import json
import sys
import os
import glob

lock = threading.Lock()
scan_result = {}        

def combineDicts(dictionary1, dictionary2):
    output = {}
    for item, value in dictionary1.iteritems():
        output[item] = {"ports" : dictionary1[item]["ports"] + dictionary2[item]["ports"]}
    return output


def merge_jsons(files):
    merge = {}   
    for index in range(len(files)):
        if index == len(files) - 1:
            filename = 'fast_scaning_reports.json'
            report = file(filename, 'w+')
            json.dump(str(merge), report, ensure_ascii=False)
            return merge
        if index == 0:  
            input_1 = file(files[index]).read()
            os.remove(files[index])
            input_2 = file(files[index + 1]).read()
            os.remove(files[index + 1])
            json_input_1= json.loads(input_1)
            json_input_2= json.loads(input_2)
            merge = combineDicts(json_input_1, json_input_2)
        if index > 0:
            input_2 = file(files[index + 1]).read()
            os.remove(files[index + 1])
            json_input_2= json.loads(input_2)
            merge = combineDicts(merge, json_input_2)
            
def save_file(scan_result, ident):
#     time_stamp = time.strftime("%Y-%m-%d-%H-%M")
    filename = 'jongwon\'s_fast_scaning_' + str(ident)
    report = file(filename, 'w')
    json.dump(scan_result, report, ensure_ascii=False)
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
        s.settimeout(0.5)
        response = s.connect_ex((str(ip), int(port)))
        if not response:
            lock.acquire()
#             print 'IP %s, port: %d open' %(str(ip),int(port))
            scan_result[str(ip)]["ports"].append(str(port))
            lock.release()
    
def main():
#     ports = [21,22,23,53,80,443,8080]
    ports = [80]

    threads = 1
    victims = netaddr.IPNetwork("74.125.235.0/24")
#     victims = ["74.125.235.100", "74.125.235.101", "74.125.235.102", "74.125.235.103"]

    if type(victims) == list:
        if threads > len(victims) or len(victims) / threads == 1:
            print "the number of thread problem!!!"
            sys.exit()
        initial = 0
        chunk   = len(victims) / threads #chuck가 1이되면 안
        final = chunk
        
        for victim in victims:
            scan_result[str(victim)] = {"ports" : []}
        
        print '*'*50
        print '- Fast Port scanner -'
        print '   Number of threads     :%d' %threads
        print '   Size of each chunk    :%d' %final
        print '   Number of IPs to scan :%d' %len(victims) 
    
        print '- List of Ports -\n', ports
        print '*'*50
    
        processes = []
    
        for i in range(1,threads+1):
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
        if threads > len(victims) or len(victims) / threads == 1:
            print "the number of thread problem!!!"
            sys.exit()
        initial = 1
        chunk   = (victims.size - 2) / threads
        final = chunk
        
        for victim in victims:
            scan_result[str(victim)] = {"ports" : []}
                    
        print '*'*50
        print '- Fast Port scanner -'
        print '   Number of threads     :%d' %threads
        print '   Size of each chunk    :%d' %final
        print '   Number of IPs to scan :%d' %victims.size
    
        print '- List of Ports -\n', ports
        print '*'*50
        
        processes = []
        for i in range(1,threads+1):
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


if __name__ == '__main__':
    start_time = timeit.default_timer()
    main()
    end_time = timeit.default_timer()
    merge_jsons(glob.glob("jongwon*"))
    print '\nPort scan is done: ', end_time - start_time


