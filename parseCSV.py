import csv

#Test comments

class parseCsv:

    def __init__(self):
        return
        
    def produceDict(self, sourceDict, csvInput):
        with open(csvInput, 'r', newline='') as csvfile:
            estimates = csv.reader(csvfile, delimiter=',', quotechar='|')
            rownum = 0
            for row in estimates:
                tempDict = {}
                if rownum == 0:
                    header = row
                else:
                    for i in range(0, len(row)):
                        key = header[i]
                        value = row[i]
                        tempDict[key] = value
                if rownum == 0:
                    pass
                else:
                    sourceDict["Item_number_" + str(rownum)] = tempDict
                rownum += 1
        return sourceDict

    def yieldRow(self, sourceDict):
        """This function allows you to iterate through each task item in order"""
        for i in range(1,(len(sourceDict.values()) + 1)):
            yield sourceDict['Item_number_' + str(i)]
