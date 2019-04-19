# This script generates real-time streaming plot for word/tag count
# It needs support from lightning-viz (install: pip install lightning-python)
# To plot, start the streaming and lightning server and put the file in the intermediate result folder.

from lightning import Lightning
import numpy as np
import time
import os
import sys

# add Data to array 
def addData(fileName,targets,numOfWords):
    result = [0]*numOfWords
    with open(fileName, "r") as f:
            for line in f.readlines():
                terms = line.split(" ")
                if terms[0] in targets:
                    i = targets.index(terms[0])
                    result[i] += int(terms[-1])
    return result


def main():
    targets = sys.argv[1:]
    prefix = "./wordCountSplit/"
    foldersIni = list(filter(lambda x: x[0]!= ".", os.listdir(prefix)))
    count = []
    numOfWords = len(sys.argv)-1
    numOfFiles = 0

    #initialize the array
    for folder in foldersIni:
        fileName = prefix+folder+"/part-00000"
        count.append(addData(fileName,targets,numOfWords))
        numOfFiles += 1

    #plot the initialized array
    lgn = Lightning()
    numOfFiles = 10 if (numOfFiles > 10) else numOfFiles

    series = np.array(count[:numOfFiles]).reshape((numOfWords, numOfFiles))
    viz = lgn.linestreaming(series, max_width=15, xaxis="Window No. (each window is 60 sec with 5 sec update interval", yaxis="Word Frequency")
    
    time.sleep(4)
    for c in count[numOfFiles:]:
        viz.append(np.array(c).reshape((numOfWords, 1)))
        time.sleep(0.3)

    # update the new data generated by Spark Streaming
    while True:
        folders = filter(lambda x: x[0]!= ".", os.listdir(prefix))
        for folder in folders:
            if folder not in foldersIni:
                time.sleep(5)
                fileName = prefix+folder+"/part-00000"
                newData = addData(fileName,targets,numOfWords)
                viz.append(np.array(newData).reshape((numOfWords, 1)))
                time.sleep(0.3)

if __name__ == "__main__":
    main()