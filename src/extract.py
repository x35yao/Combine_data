__author__ = 'srkiyengar'

from datetime import datetime, timedelta
from scipy.interpolate import UnivariateSpline, interp1d
import matplotlib.pyplot as plt

gripper_file = "691960-2017-10-29-17-03-Servo-displacement-preprocessed"

class extrapolate:

    def __init__(self,processed_servo):
        self.gripper = processed_servo
        self.gripper_time =[]
        self.sf1 = []
        self.sf2 = []
        self.sf3 = []
        self.sf4 = []

        try:
            with open(processed_servo) as f:
                self.servo_lines = f.readlines()
        except IOError,e:
            print("Failure during opening processed_servo file {}".format(e))
            raise IOError ("Unable to open processed data file {}".format(processed_servo))

    def generate(self):
        clock_diff = int(self.servo_lines[0])   #Positive means the gripper is behind ndi


        y = self.servo_lines[1].strip().split(",")
        dateSetting = '%Y-%m-%d %H:%M:%S.%f'
        t0 = datetime.strptime(y[0],dateSetting)
        clock_diff = timedelta(microseconds=clock_diff)


        for line in self.servo_lines[1:]:
            y = line.strip().split(",")
            servo_time = datetime.strptime(y[0], dateSetting)
            self.gripper_time.append((servo_time-t0+clock_diff).total_seconds())
            self.sf1.append(int(y[1]))
            self.sf2.append(int(y[2]))
            self.sf3.append(int(y[3]))
            self.sf4.append(int(y[4]))

        return

if __name__ == "__main__":

    a = extrapolate(gripper_file)
    a.generate()
    length = len(a.sf1)
    #yinterp = UnivariateSpline(a.gripper_time, a.sf1, s = 5e8)(a.gripper_time)
    yinterp = interp1d(a.gripper_time, a.sf1)(a.gripper_time)
    print yinterp
    plt.plot(a.gripper_time, a.sf1, 'bo', label = 'Original')
    plt.plot(a.gripper_time, yinterp, 'r', label = 'Interpolated')
    #plt.plot(a.gripper_time, a.sf2, 'gs', label = 'Original')
    #plt.plot(a.gripper_time, a.sf3, 'rd', label = 'Original')
    plt.show()
    pass
