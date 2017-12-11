__author__ = 'srkiyengar'

import numpy as np
import math
import os

#the gripper handle has two locations (top and bottom)
#Static transformation is to convert measurements of a rigid body fro
#Pose and location when 449 is in the top - v1,q1 are 449 and v2,q2 are 339 at the center
v1_449 = [97.663788, -180.389755, -1895.446655]
q1_449 = [0.416817, -0.806037, 0.028007, -0.419267]
v2_339 = [78.019791, -26.525036, -1980.021118]
q2_339 = [0.222542, 0.551251, 0.281243, 0.753326]

object_origin = [195.30,23.96,-1886.08]

#pose and location when v1,q1 of 339 is at the bottom and v2,q2 of 449 at the center
v1_339 = [203.19, -58.99, -1621.9]
q1_339 = [0.7765, -0.2614, -0.5724, 0.032]
v2_449 = [107.71, -127.45, -1699.52]
q2_449 = [0.2803, -0.5491, 0.4564, -0.6415]

labview_ndi_file = "706685-2017-11-05-12-28-52.txt-preprocessed"

def rotmat_to_axis_angle(R):

    r00 = R[0, 0]
    r01 = R[0, 1]
    r02 = R[0, 2]
    r10 = R[1, 0]
    r11 = R[1, 1]
    r12 = R[1, 2]
    r20 = R[2, 0]
    r21 = R[2, 1]
    r22 = R[2, 2]

    theta = math.acos((r00 + r11 + r22 - 1) / 2)
    sinetheta = math.sin(theta)
    v = (2 * sinetheta) * theta

    cz = ((r10 - r01) / (2 * sinetheta)) * theta
    by = ((r02 - r20) / (2 * sinetheta)) * theta
    ax = ((r21 - r12) / (2 * sinetheta)) * theta

    return ax, by, cz


def rotation_matrix_from_quaternions(q_vector):

    '''
    :param q_vector: array, containing 4 values representing a unit quaternion that encodes rotation about a frame
    :return: an array of shape 3x3 containing the rotation matrix.
    Takes in array as [qr, qx, qy, qz]
    https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation, s = 1
    '''

    qr, qi, qj, qk = q_vector
    first = [1-2*(qj*qj+qk*qk), 2*(qi*qj-qk*qr),   2*(qi*qk+qj*qr)]
    second= [2*(qi*qj+qk*qr),   1-2*(qi*qi+qk*qk), 2*(qj*qk-qi*qr)]
    third = [2*(qi*qk-qj*qr),   2*(qj*qk+qi*qr),   1-2*(qi*qi+qj*qj)]
    R = np.array([first,second,third])
    return R


def homogenous_transform(R,vect):

    '''
    :param R: 3x3 matrix
    :param vect: list x,y,z
    :return:Homogenous transformation 4x4 matrix using R and vect
    '''

    H = np.zeros((4,4))
    H[0:3,0:3] = R
    frame_displacement = vect + [1]
    D = np.array(frame_displacement)
    D.shape = (1,4)
    H[:,3] = D
    return H

def inverse_homogenous_transform(H):

    '''
    :param H: Homogenous Transform Matrix
    :return: Inverse Homegenous Transform Matrix
    '''


    R = H[0:3,0:3]
    origin = H[:-1,3]
    origin.shape = (3,1)

    R = R.T
    origin = -R.dot(origin)
    return homogenous_transform(R,list(origin.flatten()))

def center_tool_339_to_gripper_center():

    '''
    The y-axis of 339 is aligned with the y axis of the gripper. The z-axis of the 339 will require a rotation of 90
    (counter clockwise with respect to y R (y,90) to get align gripper z axis to outward pointing. the origin of the
    339 needs to be moved in z-axis by + 40.45mm to get it to the origin of the gripper

    :return: homogenous transformation from 339 center to gripper center
    '''

    d =[0.0,0.0,40.45,1.0]
    H = np.zeros((4,4))
    H.shape = (4,4)
    H[:,3]= d
    H[(1,0),(1,2)]=1
    H[2,0]= -1
    return H

def center_tool_449_to_gripper_center():

    '''
    The y-axis of 4499 is aligned with the y axis of the gripper. The z-axis of the 449 will require a rotation of 90
    (counter clockwise with respect to y R (y,90) to get align gripper z axis to outward pointing. the origin of the
    449 needs to be moved in z-axis by + 35.36 (Not accurate) to get it to the origin of the gripper.
    the accurate measure from geometry 32.796

    :return: homogenous transformation from 339 center to gripper center
    '''

    d =[0.0,0.0,32.796,1.0]
    H = np.zeros((4,4))
    H.shape = (4,4)
    H[:,3]= d
    H[(1,0),(1,2)]=1
    H[2,0]= -1
    return H

def static_transform_449_top(q1,v1,q2,v2):
    '''

    :param q1: unit quaternions representing the rotation of the frame of 449 tool at the top
    :param v1: vector representing the rotation of the frame of 449 tool at the top
    :param q2: unit quaternions representing the rotation of the frame of 339 tool at the center
    :param v2: vector representing the rotation of the frame of 339 tool at the center
    :return: homogenous tranformation
    '''
    # H1 -  Homogenous transform from reference NDI frame to front tool
    # H2 -  Homogenous transform from reference NDI frame to center tool
    # H3 -  Homogenous transformation from the center tool frame to center of the gripper with axis rotated where the y
    # is parallel and between the two fingers and z is pointing outward


    R1 = rotation_matrix_from_quaternions(q1)
    H1 = homogenous_transform(R1, v1)
    h1 = inverse_homogenous_transform(H1)

    R2 = rotation_matrix_from_quaternions(q2)
    H2 = homogenous_transform(R2, v2)

    H3 = center_tool_339_to_gripper_center()
    H = (h1.dot(H2)).dot(H3)
    return H

def static_transform_339_bottom(q1,v1,q2,v2):
    '''

    :param q1: unit quaternions representing the rotation of the frame of 339 tool at the bottom of the gripper
    :param v1: vector representing the rotation of the frame of 339 tool
    :param q2: unit quaternions representing the rotation of the frame of 449 tool at the center
    :param v2: vector representing the rotation of the frame of 449
    :return: homogenous tranformation
    '''
    # H1 -  Homogenous transform from reference NDI frame to front tool
    # H2 -  Homogenous transform from reference NDI frame to center tool
    # H3 -  Homogenous transformation from the center tool frame to center of the gripper with axis rotated where the y
    # is parallel and between the two fingers and z is pointing outward


    R1 = rotation_matrix_from_quaternions(q1)
    H1 = homogenous_transform(R1, v1)
    h1 = inverse_homogenous_transform(H1)

    R2 = rotation_matrix_from_quaternions(q2)
    H2 = homogenous_transform(R2, v2)

    H3 = center_tool_449_to_gripper_center()
    H = (h1.dot(H2)).dot(H3)
    return H

def static_transform_object_reference(position_vector):

    first = [0,0,1]
    second= [0,1,0]
    third = [-1,0,0]
    R = np.array([first,second,third])
    H = homogenous_transform(R,position_vector)
    return H




class ndi_transformation:
    def __init__(self,*args):

        if args:
            filename = os.path.join(args[0],"transformation.constants")
        try:
            with open(filename) as f:
                lines = f.readlines()
        except:
            self.error = "Unable to open the transformation.constants file"
            self.success = 0
            return

        val = []
        for line in lines:
            val.append(line)
        if len(val) != 9:
            self.error = "transformation.constants did not have 9 lines"
            self.success = 0
            return


        v1_449 = list(map(float,val[0].strip().split(",")[1:]))
        if len(v1_449) != 3:
            self.error = "transformation.constants- v1_449 is not 3 numbers"
            self.success = 0
            return

        q1_449 = list(map(float,val[1].strip().split(",")[1:]))
        if len(q1_449) != 4:
            self.error = "transformation.constants q1_449 is not 4 numbers"
            self.success = 0
            return

        v2_339 = list(map(float,val[2].strip().split(",")[1:]))
        if len(v2_339) != 3:
            self.error = "transformation.constants- v2_339 is not 3 numbers"
            self.success = 0
            return

        q2_339 = list(map(float,val[3].strip().split(",")[1:]))
        if len(q2_339) != 4:
            self.error = "transformation.constants q2_339 is not 4 numbers"
            self.success = 0
            return

        v1_339 = list(map(float,val[4].strip().split(",")[1:]))
        if len(v1_339) != 3:
            self.error = "transformation.constants- v1_339 is not 3 numbers"
            self.success = 0
            return

        q1_339 = list(map(float,val[5].strip().split(",")[1:]))
        if len(q1_339) != 4:
            self.error = "transformation.constants q1_339 is not 4 numbers"
            self.success = 0
            return

        v2_449 = list(map(float,val[6].strip().split(",")[1:]))
        if len(v2_449) != 3:
            self.error = "transformation.constants- v2_449 is not 3 numbers"
            self.success = 0
            return

        q2_449 = list(map(float,val[7].strip().split(",")[1:]))
        if len(q2_449) != 4:
            self.error = "transformation.constants q2_449 is not 4 numbers"
            self.success = 0
            return

        object_origin = list(map(float,val[8].strip().split(",")[1:]))
        if len(object_origin) != 3:
            self.error = "transformation.constants object_origin is not 3 numbers"
            self.success = 0
            return

        self.HT_from449_to_gripper_center = static_transform_449_top(q1_449,v1_449,q2_339,v2_339)
        self.HT_from339_to_gripper_center = static_transform_339_bottom(q1_339,v1_339,q2_449,v2_449)
        self.Inverse_HT_object = inverse_homogenous_transform(static_transform_object_reference(object_origin))
        self.processed_lines = []
        self.fname = ""
        self.success = 1
        return

class transformer:
    def __init__(self,labview_ndi_file,static_transform):

        try:
            with open(labview_ndi_file) as f:
                self.lines = f.readlines()
        except:
                self.error = "Unable to open file {}".format(labview_ndi_file)
                self.success = 0
                return
        self.st = static_transform
        self.fname = labview_ndi_file
        self.success = 1
        self.error =""
        self.processed_lines = []
        return

    def process_file(self):

        for line in self.lines:
            capture_time,tool = line.split(",")[0:2]
            if (tool == "449"):
                x, y, z, qr, qi, qj, qk = map(float,(line.strip().split(",")[2:]))
                R = rotation_matrix_from_quaternions([qr, qi, qj, qk])
                H = homogenous_transform(R, [x, y, z])
                H = H.dot(self.st.HT_from449_to_gripper_center)            # pose and position of Gripper Center w.r.t NDI frame
                H_origin = self.st.Inverse_HT_object.dot(H)                # Gripper w.r.t to object frame
                R_origin = H_origin[0:3,0:3]
                Rx,Ry,Rz = rotmat_to_axis_angle(R_origin)
                x = H_origin[0,3]
                y = H_origin[1,3]
                z = H_origin[2,3]
                self.processed_lines.append(str(capture_time)+','+str(x)+','+str(y)+','+str(z)+','+str(Rx)+','
                                   +str(Ry)+','+str(Rz))

            elif (tool == "339"):
                x, y, z, qr, qi, qj, qk = map(float,(line.strip().split(",")[2:]))
                R = rotation_matrix_from_quaternions([qr, qi, qj, qk])
                H = homogenous_transform(R, [x, y, z])
                H = H.dot(self.st.HT_from339_to_gripper_center)   # pose and position of Gripper Center w.r.t NDI frame
                H_origin = self.st.Inverse_HT_object.dot(H)       # Gripper w.r.t to object frame
                R_origin = H_origin[0:3,0:3]
                Rx,Ry,Rz = rotmat_to_axis_angle(R_origin)
                x = H_origin[0,3]
                y = H_origin[1,3]
                z = H_origin[2,3]
                self.processed_lines.append(str(capture_time)+','+str(x)+','+str(y)+','+str(z)+','+str(Rx)+','
                                   +str(Ry)+','+str(Rz))

    def save_processed_file(self):

        try:
            with open(self.fname+"-transformed","w") as f:
                for i in self.processed_lines:
                    i = i + "\n"
                    f.write(i)
        except IOError,e:
            self.error = "Unable to create file to save transformed gripper trajectory"
            return False
        self.error = ""
        return True




if __name__ == "__main__":

    my_static_transform = ndi_transformation("/home/srkiyengar/raw_data")
    my_file_transform = transformer(labview_ndi_file,my_static_transform)
    my_file_transform.process_file()
    my_file_transform.save_processed_file()