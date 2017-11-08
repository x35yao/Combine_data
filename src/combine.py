__author__ = 'srkiyengar'

from datetime import datetime, timedelta
from scipy.interpolate import UnivariateSpline, interp1d
import matplotlib.pyplot as plt

labview_file = "706685-2017-11-05-12-28-52.txt-preprocessed-transformed"
gripper_file = "706685-2017-11-05-12-28-Servo-displacement-preprocessed"
final_file = "706685-2017-11-05-12-28-final"

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

        try:
            with open(processed_servo) as f:
                self.servo_lines = f.readlines()
        except IOError,e:
            print("Failure during opening processed_servo file {}".format(e))
            raise IOError ("Unable to open processed data file {}".format(processed_servo))

    def merge_data(self):

        clock_diff = int(self.servo_lines[0])   #Positive means the gripper clock is behind ndi
        sf1 = []
        sf2 = []
        sf3 = []
        sf4 = []

        ndi_time_for_gripper = []

        dateSetting = '%Y-%m-%d %H:%M:%S.%f'
        y = self.servo_lines[1].strip().split(",")
        t0 = datetime.strptime(y[0],dateSetting)            #start time - Gripper zero
        clock_diff = timedelta(microseconds=clock_diff)


        for line in self.servo_lines[1:]:
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

        start = self.ndi_lines[0].strip().split(",")[0:1]
        start = ''.join(start)

        dateSetting = '%Y-%m-%d-%H-%M-%S.%f'
        #t0 = datetime.strptime(start, dateSetting)

        try:
            f = open(final_file,"w")
        except IOError,e:
            print("Failure during opening final file {}".format(e))
            raise IOError ("Unable to open file for writing combined output {}".format(final_file))

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
        f.close()
        return



if __name__== "__main__":

    m = combine(labview_file,gripper_file)
    m.merge_data()
    pass