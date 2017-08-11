import csv
import random as r
import pygal
from time import sleep

fileName = input('Enter file path with file name (must be CSV format - no suffix needed on name): ')
csvinput = (fileName + '.csv')
distChart = ('.\\output\\' + fileName + '.svg')
xyChart = ('.\\output\\' + fileName + 'XY.svg')
outputfile = ('.\\output\\' + fileName + '.txt')
tasks = {}
iterations = ''
midConfidence = ''
highConfidence = ''

def tidyInput():
    global iterations
    global midConfidence
    global highConfidence
    iterations = input('Enter number of simulation runs (defaults to 10000): ')
    midConfidence = input('Enter lower confidence percentage chance of completing as a number (defaults to 80): ')
    highConfidence = input('Enter lower confidence percentage chance of completing as a number (defaults to 90): ')
    if iterations == '':
        iterations = int(10000)
        print('Performing default iterations of 10,000')
    else:
        iterations = int(iterations)
        print('Performing ' + str(iterations) + ' iterations')
    if midConfidence == '':
        midConfidence = int(80)
        print('Using default lower confidence of 80%')
    else:
        midConfidence = int(midConfidence)
        print('Using ' + str(midConfidence) + ' lower confidence value')
    if highConfidence == '':
        highConfidence = int(90)
        print('Using default higher confidence of 90%')
    else:
        highConfidence = int(highConfidence)
        print('Using ' + str(highConfidence) + ' higher confidence value')
    sleep(4)
    



def produceTaskDict(taskDict):
    with open(csvinput, 'r', newline='') as csvfile:
        estimates = csv.reader(csvfile, delimiter=',', quotechar='|')
        rownum = 0
        for row in estimates:
            tempdict = {}
            if rownum == 0:
                header = row
            else:
                for i in range(0, len(row)):
                    key = header[i]
                    value = row[i]
                    tempdict[key] = value                          
            if rownum == 0:
                pass
            else:
                taskDict["Task_number_" + str(rownum)] = tempdict
            rownum += 1
            

def monteMyCarlo(taskDict, iterations):
    for j in taskDict:
        simulated = []
        rangemin = float(taskDict[j]['Shortest time'])
        rangemax = float(taskDict[j]['Longest time'])
        if ((taskDict[j]['Multi']) == '1'):           
            rangemin *= 0.7
            rangemax *= 0.7
        for i in range(0, iterations):
            predicted = r.uniform(rangemin, rangemax)
            simulated.append(predicted)
        taskDict[j]["simulated_outcomes"] = simulated


def simulateTotal(taskDict, iterations):
    totalList = []
    for k in range(0,iterations):
        totalList.append(0)
    for j in taskDict.values():
        for l in range(0, iterations):
            totalList[l] += int(j["simulated_outcomes"][l])
    return(totalList)    

def estimatePerItem(taskDict, iterations, output):
    totalTask = 0
    with open(output, 'w') as delfile:
        delfile.truncate()
    with open(output, 'a') as outfile:
        for i in taskDict.values():
            for j in range(0, iterations):
                totalTask += i['simulated_outcomes'][j]
            totalTask /= iterations
            i['Estimate'] = totalTask
            outfile.write('Name: ' + str(i['Name']) + '\nEstimate: ' + str(i['Estimate']) + ' days\n\n')

def drawGraph(uniqueDataSet, unsortedDataSet, iterations):
    chart = pygal.Bar(show_legend=False, human_readable=True, print_values=True)
    otherchart = pygal.Line(show_legend=False, human_readable=True, print_values=False)
    xychart = pygal.XY(legend_at_bottom=True, show_legend=True, human_readable=True, print_values=False)
    total = 0
    percentage = 0
    incrpercent = 0
    percentagedisp = ""
    valuesForLine = []
    valueTuple = ()
    valueTupleList = []
    valueTupleToo = ()
    valueTupleListToo = []
    looped = 0  #this variable allows us to show values for limited items on the graph
    if isinstance(uniqueDataSet, set):
        newdataSet = uniqueDataSet
    else:
        newdataSet = set(uniqueDataSet)
    #for j in newdataSet:
        #total += j
    for i in sorted(newdataSet):
        looped += 1
        value = unsortedDataSet.count(i)
        percentage = (value/iterations) * 100
        incrpercent = incrpercent + percentage
        label = (str(i) + " days")
        valuesForLine.append(i)
        valueTuple = (i, percentage)
        valueTupleList.append(valueTuple)
        valueTupleToo = (i, incrpercent)
        valueTupleListToo.append(valueTupleToo)
        if incrpercent > midConfidence:
            print(str(incrpercent) + "% chance of finishing in " + str(i) + ' days')     
        if incrpercent < midConfidence:
            if (looped % 10) == 0:  #here looped provides the value to assess for value display
                chart.add(str(incrpercent) + "%", [{'value': value,
                                                    'label': label,
                                                    'color': 'rgba(139, 45, 87, .8)',
                                                    'formatter': lambda x: '{} days'.format(x)}])
                otherchart.add(str(incrpercent) + "%", [{'value': i,
                                                    'label': label,
                                                    'color': 'rgba(139, 45, 87, .8)',
                                                    'formatter': lambda x: '{} days'.format(x)}])
            else:
                chart.add(str(incrpercent) + "%", [{'value': value,
                                                    'label': label,
                                                    'color': 'rgba(139, 45, 87, .8)',
                                                    'formatter': lambda x: ''}])
                otherchart.add(str(incrpercent) + "%", [{'value': i,
                                                    'label': label,
                                                    'color': 'rgba(139, 45, 87, .8)',
                                                    'formatter': lambda x: '{} days'.format(x)}])
        elif incrpercent >= midConfidence and incrpercent < highConfidence:
            if (looped % (iterations/10)) == 0:
                chart.add(str(incrpercent) + "%", [{'value': value,
                                                    'label': label,
                                                    'color': 'rgba(80, 139, 200, .8)',
                                                    'formatter': lambda x: '{}%'.format(x)}])
                otherchart.add(str(incrpercent) + "%", [{'value': i,
                                                    'label': label,
                                                    'color': 'rgba(80, 139, 200, .8)',
                                                    'formatter': lambda x: '{}%'.format(x)}])
            else:
                chart.add(str(incrpercent) + "%", [{'value': value,
                                                    'label': label,
                                                    'color': 'rgba(80, 139, 200, .8)',
                                                    'formatter': lambda x: ''}])
                otherchart.add(str(incrpercent) + "%", [{'value': i,
                                                    'label': label,
                                                    'color': 'rgba(80, 139, 200, .8)',
                                                    'formatter': lambda x: ''}])
        else:
            if (looped % (iterations/10)) == 0:
                chart.add(str(incrpercent) + "%", [{'value': value,
                                                    'label': label,
                                                    'color': 'rgba(10, 180, 90, .8)',
                                                    'formatter': lambda x: '{}%'.format(x)}])
                otherchart.add(str(incrpercent) + "%", [{'value': i,
                                                    'label': label,
                                                    'color': 'rgba(10, 180, 90, .8)',
                                                    'formatter': lambda x: '{}%'.format(x)}])
            else:
                chart.add(str(incrpercent) + "%", [{'value': value,
                                                    'label': label,
                                                    'color': 'rgba(10, 180, 90, .8)',
                                                    'formatter': lambda x: ''}])
                otherchart.add(str(incrpercent) + "%", [{'value': i,
                                                    'label': label,
                                                    'color': 'rgba(10, 180, 90, .8)',
                                                    'formatter': lambda x: ''}])
    chart.render_to_file(distChart)
    xychart.add('% occurrence of each estimate', valueTupleList)
    xychart.add('% chance of estimate being achieved', valueTupleListToo)
    xychart.render_to_file(xyChart)
    print('A distribution chart has been created, named: ' + distChart + '. Red columns are below the lower confidence level, blue above the lower confidence level but below the higher, and green are values above the higher confidence level.')
    sleep(4)
    print('\n')
    print('An occurrence chart has been created showing how often each estimate occurred. It is named: ' + xyChart)
    sleep(4)
    print('\n')
    print('Text output of the simulation is named: ' + outputfile)




tidyInput()
produceTaskDict(tasks)

monteMyCarlo(tasks, iterations)

total = simulateTotal(tasks, iterations)

estimatePerItem(tasks, iterations, outputfile)

uniquetotal = set(total)
drawGraph(uniquetotal, total, iterations)

