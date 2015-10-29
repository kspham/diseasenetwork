# diseasenetwork

Changes:  switched from networkx to igraph.   
          Reason: igraph is hundred times faster(according to https://graph-tool.skewed.de/performance).   
          added the verifier.   
            To use, save the interactions list(for example with GRID2 connections) from Genemania and run python3 ./genemaniaNetwork.py -v -i yourlist.txt   
TODO: solve the problem with incorrect networks and groups or combine own network from separated networks.   
