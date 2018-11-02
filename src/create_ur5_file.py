__author__ = 'srkiyengar'


import os

dir_name = "../raw_data/results"

class process_result():

    def __init__(self,dname):
        if not os.path.exists(dname):
            raise ("The directory" + dname + "does not exist")
            sys.exit(1)
        else:
            self.dname = dname
            tempname = os.path.join(dname, "results-ur5")
            if not os.path.exists(tempname):
                os.mkdir(tempname)
            self.folder = tempname
            self.file_list = []
            self.count = 0
            self.total = 0


    def process_files(self):
        a = os.walk(self.dname)
        all_files = a.next()[2]
        self.total = len(all_files)
        for name in all_files:
            if len(name)==6:
                try:
                    with open(self.dname+"/"+name) as f:
                        lines = f.readlines()
                except IOError, e:
                    print("Failure: opening result file {} msg: {}".format(name,e))
                    continue
                new_file = self.folder +'/'+ name + "-ur5"

                try:
                    with open(new_file, "w") as f:
                        for line in lines[-3:]:
                            if line[0] == 'T':
                                my_index = line.find("*")+2
                                f.write(line[my_index:])
                        f.write(lines[0])
                        z = 999
                        f1 = 0
                        line_num = 0
                        for line in lines[:-3]:
                            data = line.strip().split(",")
                            my_z = float(data[3])
                            if my_z < z:
                                z = my_z
                                y = line.strip().split(",")
                                grasp_p1 = map(float,y[0:7])
                                line_num += 1
                        for line in lines[line_num:-3]:
                            data = line.strip().split(",")
                            my_f1 = int(data[7])
                            if my_f1 > f1:
                                f1 = my_f1
                                y = line.strip().split(",")
                                grasp_p2 = map(int,y[7:])
                        grasp = grasp_p1 + grasp_p2
                        grasp = ",".join(map(str,grasp))
                        f.write(grasp)

                except Exception as e:
                    print("Failure: opening or writing file: {} : {}".format(new_file,e))
                    continue
                self.count += 1

            else:
                continue


if __name__ == "__main__":

    s = process_result(dir_name)
    s.process_files()
    print("Total number of Files = {}, files successfully processed = {}".format(s.total, s.count))