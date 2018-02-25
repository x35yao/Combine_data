__author__ = 'srkiyengar'

import pre_process as pp
import transform as tf
import combine as c
import os
import shutil

# "706685-2017-11-05-12-28-Servo-displacement"
dname = "../raw_data"

class bulk_process:

    def __init__(self,dname):

        # create directories if they don't exisit
        if not os.path.exists(dname):
            raise ("The directory" + dname + "does not exist")
        else:
            self.dname = dname

        tempname = os.path.join(dname,"processed")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.processed= tempname

        tempname = os.path.join(dname,"archive_good")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.archive_good = tempname

        tempname = os.path.join(dname,"archive_bad")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.archive_bad = tempname

        tempname = os.path.join(dname,"processing_failure")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.processing_failure = tempname

        tempname = os.path.join(dname,"unmatched")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.unmatched = tempname

        tempname = os.path.join(dname,"results")
        if not os.path.exists(tempname):
            os.mkdir(tempname)
        self.results = tempname

        self.servo_files_list = []
        self.servo_files_processed = []
        self.servo_files_processing_failure = []
        self.servo_files_bad_grasp = []
        self.ndi_files_list = []
        self.matched_list = [] #it will be a tuple
        self.unmatched_list = [] # it will be tuple missing filename , a 0 (servo) or 1(ndi)

        #read files from raw_data directory
        a = os.walk(dname)
        all_files = a.next()[2]
        for name in all_files:
            if "Servo-displacement" in name:
                self.servo_files_list.append(name)
            elif ".txt" in name:
                self.ndi_files_list.append(name)

    def pre_process_servo_data(self):

        for gripper_file in self.servo_files_list:
            servo_file = os.path.join(self.dname,gripper_file)
            servo_data = pp.process_gripper_file(servo_file)
            if servo_data.good:
                servo_data.pre_process()
                if servo_data.save_processed_file(fullpath = self.processed):
                    self.servo_files_processed.append(gripper_file)
                    shutil.move(servo_file,os.path.join(self.archive_good,gripper_file))
                else:
                    self.servo_files_processing_failure.append(gripper_file)
                    shutil.move(servo_file,os.path.join(self.processing_failure,gripper_file))
            else:   #move servofile it to archive bad
                self.servo_files_bad_grasp.append(gripper_file)
                shutil.move(servo_file,os.path.join(self.archive_bad,gripper_file))

    def match_servo_ndi_files(self):

        servo_processed_files = list(self.servo_files_processed)
        ndi_files = list(self.ndi_files_list)

        for name in self.servo_files_processed:
            fname = name.split("-")[0]
            for ndi_filename in self.ndi_files_list:
                if fname in ndi_filename:
                    self.matched_list.append((name,ndi_filename))
                    servo_processed_files.remove(name)
                    ndi_files.remove(ndi_filename)
                    break
        for fname in servo_processed_files:
            self.unmatched_list.append((fname,0))
            fname = fname + "-preprocessed"
            shutil.move(os.path.join(self.processed,fname),os.path.join(self.unmatched,fname))

        for fname in ndi_files:
            self.unmatched_list.append((fname,1))
            shutil.move(os.path.join(self.dname,fname),os.path.join(self.unmatched,fname))

    def pre_process_ndi_data(self):
        i = 0
        for fname in self.matched_list:
            ndi_file = os.path.join(self.dname,fname[1])
            ndi_data = pp.process_labview_file(ndi_file)
            if ndi_data.good:
                if ndi_data.preprocess():
                    if ndi_data.save_processed_file(fullpath = self.processed):
                        shutil.move(ndi_file,os.path.join(self.archive_good,fname[1]))
                    else:
                        self.matched_list[i]=(fname[0],fname[1],"ndi-processing failed")
                        shutil.move(ndi_file,os.path.join(self.processing_failure,fname[1]))
                else:
                    self.servo_files_bad_grasp.append(ndi_file)
                    shutil.move(ndi_data,os.path.join(self.archive_bad,fname[1]))
            else:
                self.servo_files_bad_grasp.append(ndi_file)
                shutil.move(ndi_data,os.path.join(self.archive_bad,fname[1]))
            i=+1

    def transform_preprocessed_ndi_files(self,st):
        bad_list = []
        for name in self.matched_list:
            pname = name[1]+"-preprocessed"
            processed_ndi_file = os.path.join(self.processed,pname)
            my_transform = tf.transformer(processed_ndi_file,st)
            if (my_transform.process_file()):
                my_transform.save_processed_file()
            else:
                bad_list.append(name)
        for val in bad_list:
            self.matched_list.remove(val)
            src = os.path.join(self.archive_good,val[1])
            shutil.move(src,self.archive_bad)
            # clean up the failed ndi file and its matching pair from processed good to processed bad.
        return

    def combine_processed_files(self):
        for name in self.matched_list:
            tname = name[1]+"-preprocessed"+"-transformed"
            ndi_file = os.path.join(self.processed,tname)
            pname = name[0]+"-preprocessed"
            gripper_file = os.path.join(self.processed,pname)
            m = c.combine(ndi_file,gripper_file)
            fname = name[0].split("-")[0]
            combined_file = os.path.join(self.results,fname)
            m.merge_data(combined_file)



if __name__ == "__main__":

    my_bulk_object = bulk_process(dname)
    my_bulk_object.pre_process_servo_data()
    my_bulk_object.match_servo_ndi_files()
    my_bulk_object.pre_process_ndi_data()

    static_transform = tf.ndi_transformation(my_bulk_object.dname)
    my_bulk_object.transform_preprocessed_ndi_files(static_transform)

    my_bulk_object.combine_processed_files()

    pass



