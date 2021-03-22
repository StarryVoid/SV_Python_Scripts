#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Dynamic IPAddress Make Nginx Access Config (White List)
#
# Author: StarryVoid <stars@starryvoid.com>
# Intro:  https://blog.starryvoid.com/archives/585.html
# Build:  2021/03/22 Version 1.0.0
#
# Operating environment "Python3 dnspython"
# Install Command "pip3 install dnspython"
# About "dnspython" https://github.com/rthalley/dnspython https://dnspython.readthedocs.io/en/latest/
# About "ngx_http_access_module" http://nginx.org/en/docs/http/ngx_http_access_module.html
#
# Default Input File ./dns_read_list.txt
# One line of the configuration file is like "www.google.com#1.1.1.1#A#216.58.197.196#Annotation"
#
# Default Output File ./nginx_access_whitelist.conf
# One line of the output file is like "Allow 216.58.197.196/32;"
# There is an extra rule at the end of the configuration file "deny all;"
# And automatically reload the Nginx service "systemctl reload nginx.service"

import sys,dns.resolver,subprocess.Popen

def DNS_Query(domain_name,dns_server,domain_type,source_address):
    try:
        DNS_Resolver = dns.resolver.Resolver()
        DNS_Resolver.port = int("53")
        DNS_Resolver.timeout = float("2.0")
        DNS_Resolver.lifetime = float("5.0")
        DNS_Resolver.nameservers = list(str(dns_server).split('#'))
        return str(DNS_Resolver.resolve(str(domain_name),rdtype=str(domain_type),source=source_address).response.answer[-1].to_text().split("\n")[0].split(" ")[4])
        #
        #DNS_Answer_List=list()
        #DNS_Answer_List_Rdata = DNS_Resolver.resolve(str(domain_name),str(domain_type))
        #for rdata in DNS_Answer_List_Rdata:
        #    DNS_Answer_List.append(str(rdata))                              #IP
        #    DNS_Answer_List.append(str(rdata.target).strip(".").lower())    #CNAME
        #return tuple(DNS_Answer_List)
        #
        #DNS_Answer_List=tuple()
        #DNS_Answer_List_RRset = DNS_Resolver.resolve(str(domain_name),str(domain_type))
        #for rrset in DNS_Answer_List_RRset.response.answer:
        #    for i in rrset.items:
        #        print(i.to_text())
        #        DNS_Answer_List.append(str(i.to_text()).strip(".").lower())
        #return tuple(DNS_Answer_List)
        #
    except Exception as Error:
        print (domain_name,domain_type,'Error: unable to start def \"DNS_Query\"')

def main():
    try:
        Input_tmp_data=[]
        Output_tmp_data=[]
        Difference_Status=int(0)
        DNS_Query_Source_Address=None    #Your Network Bind Address , Default is "None" , Change to "str("127.0.0.1")"
        #
        with open("dns_read_list.txt", "r") as r_file:
            r_file_lines = r_file.readlines()
        #
        for r_line in r_file_lines:
            #r_line="www.163.com#1.2.4.5#A#216.58.197.196#Annotation"
            DNS_query_info=str(r_line).split('#')
            DNS_query_info[-1]=DNS_query_info[-1].replace('\n', '').replace('\r', '')
            #print("Inf1",DNS_query_info)
            Old_DNS_Answer=DNS_query_info[3].strip()
            New_DNS_Answer=DNS_Query(DNS_query_info[0].strip(),DNS_query_info[1].strip(),DNS_query_info[2].strip(),DNS_Query_Source_Address)
            if str(New_DNS_Answer) == "None" :
                New_DNS_Answer=Old_DNS_Answer
            #print("Inf2",DNS_query_info)
            #print("Old",Old_DNS_Answer)
            #print("New",New_DNS_Answer)
            if str(New_DNS_Answer.strip()) != str(Old_DNS_Answer.strip()) :
                Difference_Status+=1
                DNS_query_info[3]=str(New_DNS_Answer)
                #print("Inf3",DNS_query_info)
            Input_tmp_data.append(str("#".join(DNS_query_info)))
            Output_tmp_data.append("allow " + str(New_DNS_Answer) + "/32;")
            #print(New_DNS_Answer,Old_DNS_Answer,"Num =",Difference_Status)
        #
        if bool(Difference_Status) :
            Output_tmp_data.append('deny all;\n')
            #print("O1",Input_tmp_data)
            #print("O2",Output_tmp_data)
            with open("dns_read_list.txt", "w+") as w_file_output:
                w_file_output.write("\n".join(Input_tmp_data))
            with open("nginx_access_whitelist.conf", "w+") as w_file_input:
                w_file_input.write("\n".join(Output_tmp_data))
            subprocess.Popen('systemctl reload nginx.service',shell=True).returncode
    #
    except Exception as Error:
        print ('[Error]: Some errors have occurred, please check the configuration file.')

if __name__ == "__main__":
    main()
