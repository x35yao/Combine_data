__author__ = 'srkiyengar'

from datetime import datetime, timedelta
from scipy.interpolate import UnivariateSpline, interp1d
import matplotlib.pyplot as plt
import logging.handlers

labview_file = "../raw_data/897034-2018-05-17-13-53-31.txt-preprocessed-transformed"
gripper_file = "../raw_data/897034-2018-05-17-13-53-Servo-displacement-preprocessed"
final_file = "897034-final"

my_logger = logging.getLogger("pose_data_bulk_process")
LOG_LEVEL = logging.DEBUG

class combine:

    def __init__(self,processed_ndi,processed_servo):

        self.ndi = processed_ndi
        self.gripper = processed_servo
        try:
            with open(processed_ndi) as f:
                self.ndi_lines = f.readlines()
        except IOError,e:
            print("Failure during opening processed_ndi file {}".format(e))
            raise IOError ("Unable to open processed data file {}".format(processed_ndi))
            my_logger.info("Unable to open processed data file {}".format(processed_ndi))

        try:
            with open(processed_servo) as f:
                self.servo_lines = f.readlines()
        except IOError,e:
            print("Failure during opening processed_servo file {}".format(e))
            raise IOError ("Unable to open processed data file {}".format(processed_servo))
            my_logger.info("Unable to open processed data file {}".format(processed_ndi))

        self.f1 = []
        self.f2 = []
        self.f3 = []
        self.f4 = []

        self.ndi_time = []

    def merge_data(self,*args):

        clock_diff = int(self.servo_lines[0])   #Positive means the gripper clock is behind ndi
        sf1 = []
        sf2 = []
        sf3 = []
        sf4 = []

        ndi_time_for_gripper = []

        dateSetting = '%Y-%m-%d %H:%M:%S.%f'
        y = self.servo_lines[1].strip().split(",")
        try:
            t0 = datetime.strptime(y[0],dateSetting)            #start time - Gripper zero
            clock_diff = timedelta(microseconds=clock_diff)
            F = y[1:]
        except:
            print("Gripper File {} may not have figner position data".format(self.gripper))
            return 0

        if self.servo_lines[-1] == '\n':
            hangingNewline =1
        else:
            hangingNewline = 0

        taxonomy = self.servo_lines[-1-hangingNewline]
        for line in self.servo_lines[1:-1-hangingNewline]:
            y = line.strip().split(",")
            servo_time = datetime.strptime(y[0], dateSetting)
            ndi_time_for_gripper.append((servo_time-t0+clock_diff).total_seconds())
            sf1.append(int(y[1]))
            sf2.append(int(y[2]))
            sf3.append(int(y[3]))
            sf4.append(int(y[4]))

        tmax = (servo_time-t0+clock_diff).total_seconds()   #last time stamp of Gripper

        #spl1 = UnivariateSpline(gripper_time,sf1)
        #spl2 = UnivariateSpline(gripper_time,sf2)
        #spl3 = UnivariateSpline(gripper_time,sf3)
        #spl4 = UnivariateSpline(gripper_time,sf4)

        spl1 = interp1d(ndi_time_for_gripper, sf1)
        spl2 = interp1d(ndi_time_for_gripper, sf2)
        spl3 = interp1d(ndi_time_for_gripper, sf3)
        spl4 = interp1d(ndi_time_for_gripper, sf4)

        #start = self.ndi_lines[0].strip().split(",")[0:1]

        dateSetting = '%Y-%m-%d-%H-%M-%S.%f'
        #t0 = datetime.strptime(start, dateSetting)

        if args:
            fname = args[0]
        else:
            fname = final_file

        try:
            f = open(fname,"w")
        except IOError,e:
            print("Failure during opening final file {}".format(fname))
            my_logger.info("Failure during opening final file {}".format(fname))
            return 0



        for line in self.ndi_lines:
            t= ''.join(line.strip().split(",")[0:1])
            t = ((datetime.strptime(t,dateSetting))-t0).total_seconds() #time elapsed from gripper zero
            x, y, z, Rx,Ry,Rz = map(float,(line.strip().split(",")[1:]))
            if (t <= tmax):
                finger1 = int(spl1(t))
                finger2 = int(spl2(t))
                finger3 = int(spl3(t))
                finger4 = int(spl4(t))
                #print t,"\t",x,"\t",y,"\t",z,"\t",Rx,Ry,Rz,"\t",finger1,finger2,finger3,finger4
                f.write("{:f},{:f},{:f},{:f},{:f},{:f},{:f},{:d},{:d},{:d},{:d}\n".
                        format(t,x,y,z,Rx,Ry,Rz,finger1,finger2,finger3,finger4))
                self.f1.append(finger1)
                self.f2.append(finger2)
                self.f3.append(finger3)
                self.f4.append(finger4)
                self.ndi_time.append(t)

        tokens = taxonomy.split('**')
        if len(tokens)!=2:
            first = tokens[0]
            last = 'Finger calibration not recorded'
        else:
            first, last = tokens

        if 'obs' in first.lower():
            second = first[-6:].strip()
            first = first[:-6].strip()
        else:
            second = '0 obs'
        footer = '\n'.join([first, second, last])
        f.write(footer)
        # Finger start position has an offset of 840
        #f.write("Finger start position = {}".format(map(int,F)))
        f.close()
        return 1



if __name__== "__main__":

    m = combine(labview_file,gripper_file)
    m.merge_data()
    plt.plot(m.ndi_time, m.f1, 'r', label = 'Finger1')
    plt.plot(m.ndi_time, m.f2, 'b', label = 'Finger2')
    plt.plot(m.ndi_time, m.f3, 'g', label = 'Finger3')
    plt.plot(m.ndi_time, m.f4, 'y', label = 'Finger4')
    plt.show()
    pass
