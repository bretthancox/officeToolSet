import csv
from pprint import pprint as pp
import random as r
from collections import Counter

class MonteMyCarlo:

    def __init__(self, iterations, conf_high, conf_low, estimate_file=None):
        """Iterations should be the number of times to run the simulation.

           Conf high and conf low are the bounds for estimate output. If you want
           99% confidence in your estimates and nothing less, conf low should be
           99. Normally 80% and 90%, respectively, are recommended.
           
           Estimate file is only needed if you have a csv file. If you do, ensure
           you have the following structure: Name,Best,Most,Worst
           Optionally, use: Name,Best,Most,Worst,Multi. Multi is a 1 or 0 indicating
           if more than one dev pair can work on the task at the same time.
           Types: Name == string, [Best, Most, Worst, Multi] == integer."""
        
        self.iterations = iterations
        self.high = conf_high
        self.low = conf_low
        self.file = estimate_file
        self.tasks = {}


    def unpack(self):
        """opens the source csv file and builds a task_dictionary for the object.
           Uses the first row of the csv to define key values (e.g. "Most").
           AtrributeError allows the object to inform the user if they have not
           provided a file."""
        if self.file is None:
            raise AttributeError('Cannot unpack. No file provided. '
                                 'Please use "object.manual()" method')
        else:
            with open(self.file, 'r', newline='') as infile:
                opened = csv.DictReader(infile, delimiter=',')
                for rownum, row in enumerate(opened, start=1):
                    tempDict = {}
                    for pairs in row.items():
                        tempDict[pairs[0]] = pairs[1]
                    
                    self.tasks["Task_number_" +
                                         str(rownum)] = tempDict
        pp(self.tasks)
        


    def manual(self):
        """Completely unfinished. TypeError is not the correct error.
           Intent is to allow a user to manually enter three point estimates
           in the form 'name', 'best', 'most', 'worst' and package as
           self.task_dictionary for use in subsequent functions."""
        try:
            if self.file:
                print('You have provided a file. Please use "object.unpack()" instead')
        except TypeError:
            pass


    def calculate(self):
        """calculates PERT, standard deviation, and records the estimate range
           as (PERT - SD) to (PERT + SD). This range allows random selection
           later."""
        for task in self.tasks.values():
            best = int(task['Best'])
            most = int(task['Most'])
            worst = int(task['Worst'])
            task['PERT'] = (best + (4 * most) + worst )/6
            task['PM standard deviation'] = (worst - best)/6
            task['Shortest time'] = (task['PERT'] - task['PM standard deviation'])
            task['Longest time'] = (task['PERT'] + task['PM standard deviation'])
            if 'Multi' not in task.keys():
                task['Multi'] = 0
            else:
                pass

        
    def simulate(self):
        """Runs the actual simulation. Adjusts the ranges from self.calculate()
           to 0.7 of original if the task can be accomplished by > 1 pair,
           represented as a 'Multi' value of 1. For the number of self.iterations,
           the function picks a value in the min to max range and appends to a
           list. The list is added to the task in the dictionary for potential
           use outside this function. The list of lists enables the list
           comprehension at the end to sum all estimates across each iteration
           of each task for use in the primary output."""
        self.total_list = []
        list_of_lists = []
        total_duration = 0
                
        for sub_dict in self.tasks.values():
            simulated = []
            range_min = float(sub_dict['Shortest time'])
            range_max = float(sub_dict['Longest time'])
            if (sub_dict['Multi'] == '1'):
                range_min *= 0.7
                range_max *= 0.7

            for iteration in range(self.iterations):
                predicted = round(r.uniform(range_min, range_max),1)
                simulated.append(predicted)
            sub_dict['Simulated'] = simulated
            list_of_lists.append(simulated)
            sub_dict['Simulated'].sort()
                   
        self.total_list = [round(sum(x),1) for x in zip(*list_of_lists)]

        

    def confidence(self):
        """Uses collections.Counter() to produce a count of the instances of 
           each estimate, then creates a confidence value by adding each
           percentage incidence value.
           The logic being that if 6 occurs 10% of the time and 7 occurs 12% of
           the time, you can achieve the task in 7 days 22% of the time.
           NOTE: Task-level estimates should be treated with caution. Monte
           Carlo simulations are better suited to an entire schedule than a
           single task."""
        self.task_output = {}
        self.total_output = {}
        confidences = 0
        
        for task in self.tasks.values():
            confidence = 0
            if type(task) is dict:
                self.task_output[task['Name']] = {}
                est_count = Counter(task['Simulated'])
                for estimate, count in est_count.items():
                    task['Estimate occurrence'] = {}
                    confidence += self.to_percent(count)
                    self.task_output[task['Name']][estimate] = round(confidence,2)
            else:
                pass

        for total_estimate, total_count in Counter(self.total_list).items():
            confidences += self.to_percent(total_count)
            self.total_output[total_estimate] = round(confidences,2)
            #print(confidences)



    def to_percent(self, numerator):
        """Purely used to produce a percentage with the iterations as a denominator.
           Broken out for clarity of purpose. Mainly used in self.confidence()"""
        fraction = numerator/self.iterations
        percentage = fraction * 100
        return percentage



    def output(self, outfile):
        """Builds an output file with the tasks and total. This should be refined
           so that it only outputs the first value after the high and low
           confidence values. For now it outputs and unknown number of values as
           long as they are associated to > low confidence.
           Pipes > commas when source data task names might feature commas."""
        
        with open(outfile, 'w') as output:
            for key, value in self.task_output.items():
                output.write(key)
                for effort, occur in value.items():
                    if occur > float(self.low):
                        output.write('|' + str(occur) + '%|' + str(effort))
                    else:
                        pass
                output.write('\n')
            output.write('Total')
            for tot_eff, tot_occur in self.total_output.items():
                if tot_occur > float(self.low):
                    output.write('|' + str(tot_occur) + '%|' + str(tot_eff))
                    

    def all(self):
        """Just run all of the simulation functions for the object. User must
           still run the output method to create files."""
        self.unpack()
        self.calculate()
        pp(self.tasks)
        self.simulate()
        self.confidence()
        
                    


if __name__ == "__main__":

    #NOTE: User input would be better as part of class __init__
    #Should also include try/except to ensure data entered can be converted to int

    file_name = ''
    iterations = ''
    mid_confidence = ''
    high_confidence = ''
            
    file_name = input('Enter file path with file name (must be CSV format - '
                      'no suffix needed on name): ')
    
    iterations = input('Enter number of simulation runs (defaults to 100000): ')
    
    mid_confidence = input('Enter lower confidence percentage chance of '
                           'completing as a number (defaults to 80): ')
    
    high_confidence = input('Enter lower confidence percentage chance of '
                            'completing as a number (defaults to 90): ')
    
    csvinput = (file_name + '.csv')
    
    output_file = (file_name + '_output.txt')

    
    if iterations == '':
        iterations = 100000
    else:
        iterations = int(iterations)
    print('Performing default iterations of {}'.format(iterations))        


    if mid_confidence == '':
        mid_confidence = 80
    else:
        mid_confidence = int(mid_confidence)
    print('Using default lower confidence of {}%'.format(mid_confidence))


    if high_confidence == '':
        high_confidence = 90
    else:
        high_confidence = int(high_confidence)
    print('Using default higher confidence of {}%'.format(high_confidence))



    analysis = MonteMyCarlo(iterations,
                            high_confidence,
                            mid_confidence,
                            csvinput)

    analysis.all()

    analysis.output(output_file)    
