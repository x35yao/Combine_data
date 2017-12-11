__author__ = 'srkiyengar'

import numpy as np
import os


gripper_file = "706685-2017-11-05-12-28-Servo-displacement"
#labview_ndi_file = "706685-2017-11-05-12-28-52.txt"

labview_ndi_file = "131618-2017-10-28-13-34-20.txt"
#labview_ndi_file = "706687-2017-11-05-12-29-32.txt"

class process_gripper_file:

    def __init__(self,some_file):

        self.original_file = some_file
        try:
            with open(some_file) as f:
                self.lines = f.readlines()
                self.processed_lines = []
                self.clock_difference = 0
        except IOError,e:
            #print("Failure during opening gripper file {}".format(e))
            #raise IOError ("Unable to open Gripper data file {}".format(some_file))
            self.good = False
            self.error = "unable to open file"
            return
        if self.lines[-1][0] == 'S':
            del self.lines[-1]
            self.good = True
            self.error = "No error"
        else:
            self.good = False
            self.error = "Bad grasp"
        return

    def pre_process(self):

        max_val = 0

        #Append 1st line which is the start position
        #self.processed_lines.append(''.join(self.lines[0].strip()))
        self.processed_lines.append(self.lines[0].strip())
        #Extract clock difference between NDI machine and Gripper machine
        _,n = self.lines[1].split(':')
        self.clock_difference = int(n)

        #remove lines which do not have servo positions
        for line in self.lines[2:-4]:
            y = line.strip().split(",")
            del y[0]
            y = map(int,y)
            if y[0] and y[1] and y[2] and y[3]:
                self.processed_lines.append(line.strip())
                if y[0] > max_val:
                    max_val = y[0]

        #identify the end point by looking at the highest value of servo1.
        i=0
        for line in reversed(self.processed_lines):  # from the bottom identify the largest value of servo motor 1
            y = line.strip().split(",")
            del y[0]
            y = map(int,y)
            if y[0] == max_val:
                break
            i=i+1

        while(i != 0):  #removing lines that are below the largest since they indicate gripper opening after closing
            del self.processed_lines[-i]
            i=i-1
        return

    def save_processed_file(self,**kwargs):

        if kwargs:
            fname = self.original_file+"-preprocessed"
            filename = os.path.split(fname)[1]
            my_file = os.path.join(kwargs['fullpath'],filename)
        else:
            my_file = self.original_file+"-preprocessed"
        try:
            with open(my_file,"w") as f:
                i = str(self.clock_difference)+"\n"
                f.write(i)
                for i in self.processed_lines:
                    i = i + "\n"
                    f.write(i)
            return True
        except :
            self.error ="Failure in opening and writing preprocessed servo file"
            return False
            #print("While opening the preprocessed file for writing {}".format(e))
            #raise IOError ("Unable to create pre-processed Gripper data file")

class process_labview_file:

    def __init__(self,some_file):
        self.original_file = some_file
        try:
            with open(some_file) as f:
                self.lines = f.readlines()
                self.processed_lines = []
        except IOError,e:
            #print("Failure during opening labview file {}".format(e))
            #raise IOError ("Unable to open NDI Labview file {}".format(some_file))
            self.error = "Unable to open NDI Labview file"
            self.good = False
            return
        self.error ="No Error"
        self.good = True
        return

    def preprocess(self):
    # preprocess cannot delete the lines based on NDI x-axis since 449 and 339 are in different position
        for line in self.lines[6:]:
            y = line.strip().split(",")
            del y[0]
            if "Both" not in y[1]:
                if "449" in self.lines[0]:
                    if "339" in self.lines[1]:
                        y[1] = str(449)
                        y[9] = str(339)
                    else:
                        #raise IOError ("Cannot pre-process NDI Labview file-Tool in line 2 should be 339")
                        self.error = "Cannot pre-process NDI Labview file-Tool in line 2 should be 339"
                        return False

                elif "339" in self.lines[0]:
                    if "449" in self.lines[1]:
                        y[9] = str(449)
                        y[1] = str(339)
                    else:
                        #raise IOError ("Cannot pre-process NDI Labview file-Tool in line 2 should be 449")
                        self.error = "Cannot pre-process NDI Labview file-Tool in line 2 should be 449"
                        return False
                else:
                    #raise IOError ("Cannot pre-process NDI Labview file:Tool in line 1 should be 449 or 339")
                    self.error = "Cannot pre-process NDI Labview file:Tool in line 1 should be 449 or 339"
                    return False

                if (float(y[2])==0.0) and (float(y[3])==0.0) and (float(y[4])==0.0): # just checking if x,y,z are zero which means no values
                    y[1]=y[9]
                    y[2]=y[10]
                    y[3]=y[11]
                    y[4]=y[12]
                    y[5]=y[13]
                    y[6]=y[14]
                    y[7]=y[15]
                    y[8]=y[16]

                y = y[:9]
                newline = ','.join(y)
                self.processed_lines.append(newline)
        self.error ="No Error"
        return True


    def save_processed_file(self, **kwargs):

        if kwargs:
            fname = self.original_file+"-preprocessed"
            filename = os.path.split(fname)[1]
            my_file = os.path.join(kwargs['fullpath'],filename)

        else:
            my_file = self.original_file+"-preprocessed"
        try:
            with open(my_file,"w") as f:
                for i in self.processed_lines:
                    i = i + "\n"
                    f.write(i)
            return True
        except IOError,e:
            self.error = "Unable to opening file to save NDI preprosessed file"
            return False
            #print("While opening the preprocessed file for writing {}".format(e))
            #raise IOError ("Unable to create pre-processed NDI data file")



if __name__=="__main__":

    p = process_gripper_file(gripper_file)
    if p.good:
        p.pre_process()
        p.save_processed_file()

        p = process_labview_file(labview_ndi_file)
        p.preprocess()
        p.save_processed_file()

    pass




