__author__ = 'srkiyengar'

import pre_process as pp


class bulk_process:

    def __init__(self,dirname):
        self.processed_dir = dirname + "/" + "processed"
        self.archive_good_dir = dirname + "/" + "archived-good"
        self.archive_bad_dir = dirname + "/" + "archived-bad"
        self.working_dir = dirname + "/" + "working"

        self.file_list = []
        

    def pre_process(self):

        for gripper_file in self.file_list:
            servo_file = pp.process_gripper_file(gripper_file)
            if servo_file.good:
                servo_file.pre_process()
                servo_file.save_processed_file()
                labview_file_number = gripper_file.find("-")
                #find the labview file with the number
                ndi_file = pp.process_labview_file(labview_file)
                p.preprocess()
                p.save_processed_file()