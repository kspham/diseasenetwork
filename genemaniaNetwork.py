#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 02:06:55 2015

@author: k1r1ll0v
"""

import networkx as nx
import requests

def downloadFile(filename, url):
    print("Downloading "+filename)
    fh = open(filename, "wb")
    data = requests.get(url)
    fh.write(data.content)
    print("Done")

def downloadNetworkData():
    wurl = "http://genemania.org/data/current/Homo_sapiens.COMBINED/COMBINATION_WEIGHTS.DEFAULT_NETWORKS.BP_COMBINING.txt"
    nurl = "http://genemania.org/data/current/Homo_sapiens.COMBINED/COMBINED.DEFAULT_NETWORKS.BP_COMBINING.txt"
    downloadFile("./data/weights.txt", wurl)
    downloadFile("./data/network.txt", nurl)

def lst(s):
    return(s.replace("\n", "").split("\t"))

def getWeights(wfilename="./data/weights.txt"):
    wh = open(wfilename, "r")
    r = {}
    for a in wh:
        if a == "group\tnetwork\tweight\n":
            continue
        s = lst(a)
        r[float(s[2])] = (s[0], s[1])
    wh.close()
    return(r)
        
def getNetwork(weights, nfilename="./data/network.txt"):
    n = nx.MultiDiGraph()
    nh = open(nfilename, "r")
    print("Reading network")
    for a in nh:
        if a == "Gene_A\tGene_B\tWeight\n":
            continue
        s = lst(a)
        edgeAttr = {
            "weight": 0,
            "group": "unknown",
            "network": "unknown"
        }
        weight = float(s[2])
        if weight in weights.keys():
            edgeAttr = {
                "weight": weight,
                "group": weights[weight][0],
                "network": weights[weight][1]
            }
        n.add_edge(s[0], s[1], attr_dict=edgeAttr)
    nh.close()    
    print("Done")
    return(n)