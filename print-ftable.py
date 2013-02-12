#!/usr/bin/python
# -*- coding: utf-8 -*-
""" 
Script to parse and reformat OF flow table. Requires dpctl. Works with version from CPqD ofsoftswitch13.
"""

__all__ = ['make_match_dict','make_instr_dict','__main__']

__author__ =  ['Stephen Dabideen <dabideen@bbn.com>']

# Copyright (C) 2013 by 
# Raytheon BBN Technologies.
# All rights reserved. 
# BSD license. 

import sys
import re
import string
import os
import subprocess
import argparse

def make_match_dict(match_str):
    """ Function to convert the match string printed by dpctl into a python dictionary. 
    Example: match string - 
        'match="oxm{eth_dst="00:24:e8:79:08:a5", eth_dst_mask="ff:ff:ff:ff:ff:ff", eth_src="00:24:e8:7a:3e:88", eth_src_mask="ff:ff:ff:ff:ff:ff"'
    will be converted into: 
        {'eth_dst': '00:24:e8:79:08:a5', 'ipv4_dst': '192.168.13.0', 'ipv4_dst_mask': '255.255.255.0', 'ipv4_src': ' * ', 'eth_type': '0x800', 'mpls_label': '*', 'eth_dst_mask': 'ff:ff:ff:ff:ff:ff', 'eth_src': '00:24:e8:7a:3e:88', 'port': ' * ', 'eth_src_mask': 'ff:ff:ff:ff:ff:ff'}

    Note that if a field omitted in the match rule it is assigned a value of '*'
    """

    match_str = string.replace(match_str,'eth','"eth')
    match_str = string.replace(match_str,'=','"=')
    match_str = string.replace(match_str,'mpls_','"mpls_')
    match_str = string.replace(match_str,'ip','"ip')
    match_str = string.replace(match_str,'in_port','"port')
    match_str = string.replace(match_str,'=',':')
    temp_dict = eval('{' + match_str + '}')
    match_dict = {'eth_dst':'         *        ', 'eth_src':'         *         ','mpls_label':'*','eth_type':'   *','ipv4_dst':'     *         ','ipv4_src':'     *         ','port':' * '}
    for key in temp_dict.keys():
        match_dict[key] = temp_dict[key]
    return(match_dict)

def make_instr_dict(instr_str):
    """ Function to convert the instruction string printed by dpctl into a python dictionary.
    Example: instruction string - 
        'insts=[apply{acts=[set_field{field:eth_src="00:24:e8:79:08:a9"}, set_field{field:eth_dst="00:10:18:56:94:72"}, mpls_psh{eth="0x8847"}, set_field{field:mpls_label="121"}'
    will be converted into:
        {'eth_dst': '00:10:18:56:94:72', 'eth_type': '      *', 'mpls_label': '121', 'action': 'MPLS PUSH', 'eth_src': '00:24:e8:79:08:a9', 'eth': '0x8847', 'outport': '3', 'ipv4_src': '   *      ', 'ipv4_dst': '  *      '} 
   
    Note that if a field omitted in the instructions, it is assigned a value of '*'
    """

    instr_str = string.replace(instr_str,'[apply','')
    instr_str = string.replace(instr_str,'acts=[','')
    instr_str = string.replace(instr_str,'set_','')
    instr_str = string.replace(instr_str,'field','')
    instr_str = string.replace(instr_str,'{','')
    instr_str = string.replace(instr_str,'}','')
    instr_str = string.replace(instr_str,'[','')
    instr_str = string.replace(instr_str,']','')
    instr_str = string.replace(instr_str,':et','et')
    instr_str = string.replace(instr_str,':mpl','mpl')
    instr_str = string.replace(instr_str,'eth','"eth')
    instr_str = string.replace(instr_str,'=','"=')
    instr_str = string.replace(instr_str,'mpls_','"mpls_')
    instr_str = string.replace(instr_str,'ip','"ip')
    instr_str = string.replace(instr_str,'=',':')
    instr_str = string.replace(instr_str,'out','"out')
    instr_str = string.replace(instr_str,'mlen','"mlen')
    instr_str = string.replace(instr_str,'"mpls_pop','"action":"MPLS POP",')
    instr_str = string.replace(instr_str,'"mpls_psh','"action":"MPLS PUSH",')
    temp_dict = eval('{' + instr_str + '}')
    instr_dict = {'eth_dst':'     *     ', 'eth_src':'     *       ','mpls_label':'*','eth_type':'      *','ipv4_dst':'  *      ','ipv4_src':'   *      ','outport':' *', 'action':'   *    '}
    for key in temp_dict.keys():
        instr_dict[key] = temp_dict[key]
    return(instr_dict)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Script to parse and reformat OF flow table. Requires dpctl. Works with version from CPqD ofsoftswitch13.")
    parser.add_argument('-s',  metavar='[IP:Port]', help='Socket on which the switch is listening (default:127.0.0.1:6633)',default='127.0.0.1:6633')
    parser.add_argument('-a',  action='store_const', const=True, help='Only print flows to which packets have been matched.',default=False)
    parser.add_argument('-r',  action='store_const', const=True, help='Print the flow table in the raw format returned by dpctl.',default=False)

    args = parser.parse_args()

    # extract the match rule, packet count, byte count and instructions from the flow table
    match_rules = ['.*match="oxm{(?P<match>.*)}", dur.*', '.*pkt_cnt="(?P<pkt_count>\d*)".*', '.*byte_cnt="(?P<byte_count>\d*)".*','.*insts=(?P<instrs>.*)'] 
    p1 = subprocess.Popen(["dpctl", "tcp:"+args.s, "stats-flow"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    lines =  p1.stdout.readlines()

    if args.r:
        print lines
        sys.exit()

    for line in lines:

      if string.find(line,'insts=') < 0:
        continue

      tab_entry = line.split("table=")
      if len(tab_entry)> 1:
        for e in range(1,len(tab_entry)): 
            parts = {}
            for match in match_rules:
                m = re.match(match,tab_entry[e])
                if m:
                    groupdict = m.groupdict()
                    parts.update(groupdict)

            # convert the match rule into a python dictionary
            if parts['match'] != 'all match':
                match_dict = make_match_dict(parts['match'])
            else:
                match_dict = {'eth_dst':'         *        ', 'eth_src':'         *         ','mpls_label':'*','eth_type':'   *','ipv4_dst':'     *         ','ipv4_src':'     *         ','port':' * '}  

            # convert the instruction list into a python dictionary
            if parts['instrs']:
                instr_dict = make_instr_dict(parts['instrs'])

            if(int(parts['pkt_count']) > 0 or not args.a):
                print "-------------------------------------------------------------------------"
                print "|RULE # " +  str(e) + "|   Match Rules  \t|    Instructions  \t|    Stats \t|"
                print "-------------------------------------------------------------------------"
                print "| Eth SA | " + match_dict['eth_src'] + "\t|     " +  instr_dict['eth_src']  + "\t|"  + "   Pkts: " + parts['pkt_count'] + "\t|"
                print "| Eth DA | " + match_dict['eth_dst'] + "\t|     " +  instr_dict['eth_dst']  + "\t|"  + " Bytes: " + parts['byte_count'] + "\t|"
                print "| IP SRC |     " + match_dict['ipv4_src'] + "\t|       "     +  instr_dict['ipv4_src']  + "\t|" + " \t\t|"   
                print "| IP DST |     " + match_dict['ipv4_dst'] + "\t|        "    +  instr_dict['ipv4_dst']  + "\t|" + " \t\t|"   
                print "|  Port  |         " + match_dict['port'] + "\t\t|          " + instr_dict['outport'] + "\t\t|" + " \t\t|" 
                print "| Label  |          " + match_dict['mpls_label'] + "\t\t|          "      +  instr_dict['mpls_label'] + "\t\t|" + " \t\t|"
                print "| Action | \t    -\t\t|       " + instr_dict['action'] + "\t|  \t\t|"
                print "| E-TYPE |       " + match_dict['eth_type'] + "\t\t|    " + instr_dict['eth_type'] + "\t\t|" + "\t\t|" 
                print "-------------------------------------------------------------------------"


