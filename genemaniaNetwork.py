#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 02:06:55 2015

@author: k1r1ll0v
"""

#TODO: solve the problem with incorrect networks and groups

import igraph as ig
import requests
import sys
import os
import bs4
import re
import codecs
import argparse

def downloadFile(filename, url):
    print("Downloading "+filename)
    fh = open(filename, "wb")
    data = requests.get(url)
    fh.write(data.content)
    print("Done")

def downloadCombinedNetwork():
    wurl = "http://genemania.org/data/current/Homo_sapiens.COMBINED/COMBINATION_WEIGHTS.DEFAULT_NETWORKS.BP_COMBINING.txt"
    nurl = "http://genemania.org/data/current/Homo_sapiens.COMBINED/COMBINED.DEFAULT_NETWORKS.BP_COMBINING.txt"
    murl = "http://genemania.org/data/current/Homo_sapiens/identifier_mappings.txt"
    downloadFile("./data/weights.txt", wurl)
    downloadFile("./data/network.txt", nurl)
    downloadFile("./data/idMapping.txt", murl)

def downloadSeparateNetworks():
    dataDir = "./data"
    rawDir = dataDir + "/separate"
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)
    if not os.path.exists(rawDir):
        os.makedirs(rawDir)
    link = "http://genemania.org/data/current/Homo_sapiens/"
    s = requests.get(link)
    soup = bs4.BeautifulSoup(s.text)
    links = list(
        set(
            list(
                map(lambda y: y['href'], 
                    soup.find_all(
                        "a", 
                        href=re.compile(
                            "(.+\.txt$)|(.+\.gmt$)")
                        )
                    )
                )
           )
        )
    for a in links:
        downloadFile(rawDir+"/"+a, link+a)

def lst(s):
    return(s.replace("\n", "").split("\t"))

def dumpMapping(mapping):
    fh = codecs.open("./data/mapping.csv", "w", "Utf-8")
    for a in mapping:
        fh.write(a[0]+","+str(a[1])+"\n")
    fh.close()

def combineFile():
    dataRaw = "./data/separate"
    files = []
    j = 0
    stoplist = []
    networks = []
    for (c, b, a) in os.walk(dataRaw):
        files = a
    oh = codecs.open("./data/combined.txt", "w", "Utf-8")
    for a in files:
        if a.split(".")[-1] == "txt" and a not in stoplist:
            fh = codecs.open(dataRaw+"/"+a, "r", "Utf-8")
            for b in fh:
                if b != "Gene_A\tGene_B\tWeight\n":
                    j += 1
                    oh.write(b)
            networks.append((a,j))
            fh.close()
            print(a+" added")
    oh.close()
    dumpMapping(networks)

class CombinedNetwork:

    def __init__(self):
        self.graph = ig.Graph(directed=True)
        self.weights = []
        self.ids = []
        self.rev_ids = []
        
    def downloadCombined(self):
        downloadCombinedNetwork()
        
    def downloadSeparate(self):
        downloadSeparateNetworks()
        
    @staticmethod
    def load(filename):
        print("Loading "+filename)
        g = ig.read(
            filename, format="ncol",
            directed=True, names=True
        )
        g.delete_vertices([0,1])
        print("Done")
        return(g)
        
    @staticmethod
    def loadIdentifiersMapping(filename):
        print("Loading "+filename)
        fh = codecs.open(filename, "r", "Utf-8")
        r = {}
        for a in fh:
            s = lst(a)
            if s[0] in r.keys():
                r[s[0]].append(s[1])
            else:
                r[s[0]] = [s[0], s[1]]
        fh.close()
        result = {}
        for a in r:
            for b in r[a]:
                result[b] = a
        print("Done")
        return(result, r)
        
    @staticmethod
    def loadInteractionList(filename):
        print("Loading "+filename)
        fh = open(filename, "r")
        r = []
        for a in fh:
            s = lst(a)
            r.append(s)
        fh.close()
        print("Done")
        return(r)
        
    @staticmethod
    def loadWeights(wfilename="./data/weights.txt"):
        print("Loading "+wfilename)
        wh = open(wfilename, "r")
        r = {}
        for a in wh:
            if a == "group\tnetwork\tweight\n":
                continue
            s = lst(a)
            r[float(s[2])] = (s[0], s[1])
        wh.close()
        print("Done")
        return(r)
            
    def readNetwork(self, filename, wfilename, idfilename):
        self.graph = CombinedNetwork.load(filename)
        self.weights = CombinedNetwork.loadWeights(wfilename)
        k = CombinedNetwork.loadIdentifiersMapping(idfilename)
        self.ids = k[0]
        self.rev_ids = k[1]
        for a in self.graph.es:
            try:
                a["group"] = self.weights[a["weight"]][0]
                a["network"] = self.weights[a["weight"]][1]
            except:
                a["group"] = "unknown"
                a["network"] = "unknown"
        
    def lookForSynonims(self, geneA, geneB):
        indexA = self.graph.vs["name"].index(geneA)
        indexB = self.graph.vs["name"].index(geneB)
        inA = list(
            map(
                lambda x: self.graph.vs["name"][x.tuple[1]], 
                self.graph.es(_source_in = [indexB])
            )
        )
        inB = list(
            map(
                lambda x: self.graph.vs["name"][x.tuple[1]], 
                self.graph.es(_source_in = [indexB])
            )
        )
        result = False
        for a in inA:
            for b in inB:
                synonimsA = self.rev_ids[a]
                synonimsB = self.rev_ids[b]
                intrsct = list(set(synonimsA).intersection(synonimsB))
                if intrsct != []:
                    result = True
                break
        #print(result)
        return(result)
                
        
    def verify(self, filename):
        rh = codecs.open("./data/report.txt", "w", "Utf-8")
        interactions = CombinedNetwork.loadInteractionList(filename)
        rh.write("Network verification report\n")
        rh.write(self.graph.summary()+"\n")
        rh.write("Number of nodes = "+str(len(self.graph.vs))+"\n")
        rh.write("Number of edges = "+str(len(self.graph.es))+"\n")
        rh.write("Number of network groups = "+str(
                len(list(set(self.graph.es["group"])))
            ) + "\n"
        )
        rh.write("Number of subnetworks = "+str(
                len(list(set(self.graph.es["network"])))
            ) + "\n"
        )
        rh.write("\n\n\n")
        print("Verifying the network")
        for a in interactions[1:len(interactions)]:
            geneA = self.ids[a[0]]
            geneB = self.ids[a[1]]
            e = ""
            try:
                e = self.graph.es[
                    self.graph.get_eid(geneA, geneB)
                ]
            except:
                isHere = self.lookForSynonims(geneA, geneB)
                if not isHere:
                    print("Missing", a[0], geneA, a[1], geneB)
                    rh.write(
                        "Missing connection: ("+geneA+","+geneB+")\n"
                    )
            else:
                grp = a[3].replace("&nbsp;", " ")
                if e["group"] != grp:
                    weights = str(e["weight"])
                    rh.write(
        "Incorrect group "+grp+" "+e["group"]+" "+weights+"\n"
                    )
                if e["network"] != a[4]:
                    print(e["network"])
                    rh.write("Incorrect network "+a[4]+" "+
                        e["network"]+"\n")
        print("Done")
        rh.close()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input",
        dest="i",
        action="store", 
        help="set input interaction_list.txt file", 
        default="interaction_list.txt"
        )
    parser.add_argument(
        "-dc", "--download-combined",
        dest="dc",
        action="store_true",
        help="download combined network and weights",
        default=False
    )
    parser.add_argument(
        "-v", "--verify",
        dest="ver",
        action="store_true",
        help="verify the network",
        default=False
    )
    parser.add_argument(
        "-ds", "--download-separate",
        dest="ds",
        action="store_true",
        help="download separate networks",
        default=False
    )
    args = parser.parse_args()
    c = CombinedNetwork()
    if args.dc:
        c.downloadCombined()
    if args.ds:
        c.downloadSeparate()
    c.readNetwork(
        "./data/network.txt", "./data/weights.txt",
        "./data/idMapping.txt"
        )
    if args.ver:
        c.verify(args.i)
