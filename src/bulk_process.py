__author__ = 'srkiyengar'

import pre_process as pp
import os
import shutil

# "706685-2017-11-05-12-28-Servo-displacement"
dname = "/home/srkiyengar/raw_data"

class bulk_process:

    def __init__(self,dname):


        # create directories if they don't exisit
        if not os.path.exists(dname):
            raise ("The directory" + dname + "does not exist")
        else:
            self.dname = dname

        tempname = os.path.join(dname,"processed_dir")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.processed_dir = tempname

        tempname = os.path.join(dname,"archive_good_dir")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.archive_good_dir = tempname

        tempname = os.path.join(dname,"archive_bad_dir")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.archive_bad_dir = tempname

        tempname = os.path.join(dname,"results_dir")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.results_dir = tempname

        self.servo_file_list = []

        #read servo files from raw_data directory
        a = os.walk(dname)
        all_files = a.next()[2]
        for name in all_files:
            if "Servo-displacement" in name:
                self.servo_file_list.append(name)
        

    def pre_process_servo_data(self):

        for gripper_file in self.servo_file_list:
            servo_file = os.path.join(self.dname,gripper_file)
            servo_data = pp.process_gripper_file(gripper_file)
            if servo_data.good:
                servo_data.pre_process()
                servo_data.save_processed_file(fullpath = self.processed_dir)
                shutil.move(servo_file,os.path.join(self.archive_good_dir,gripper_file)) #move servofile it to archive good
            else:
                shutil.move(servo_file,os.path.join(self.archive_bad_dir,gripper_file)) #move servofile it to archive good


if __name__ == "__main__":

    my_bulk_object = bulk_process(dname)
    my_bulk_object.pre_process_servo_data()
