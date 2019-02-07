import pymel.core as pm
from .skeletons import BaseSkeleton
from .core.util import getPoleVector, orientJoint


def getRoot(joint):
    if not joint.getParent():
        return joint

    return getRoot(joint.getParent())


class SkeletonMapper(object):
    """
    Steps:

    1. Call initSkeleton()
    2. Move end joints
    3. Call buildSkeleton()

    Parameters
    ----------
    object : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """

    def __init__(self, joint_map):
        self.joint_map = joint_map
        self.skeleton = BaseSkeleton()
        self.joints = None

    def createHalfSkeleton(self):
        joint_dict = {jnt: pm.ls(
            self.joint_map[jnt])[0] for jnt in self.skeleton.joint_names if jnt in self.joint_map and pm.ls(self.joint_map[jnt])}

        joints = {jntname: pm.createNode('joint', n=jntname)
                  for jntname in self.skeleton.joint_names}

        for jnt in joints.values():
            jnt.radius.set(10)

        for j in joint_dict:
            joints[j].setTranslation(
                joint_dict[j].getTranslation(space='world'), space='world')

            if j == 'Spine1_M':
                joints[j].setTranslation(joints['COG_M'].getTranslation(
                    space='world') + (0, 1, 0), space='world')

        for j in self.skeleton.manual_xforms:
            joints[j].setParent(joints[self.skeleton.joint_tree[j]])
            joints[j].setTranslation([0, 0, 0])
            joints[j].setParent(None)
            pm.move(joints[j], self.skeleton.manual_xforms[j], relative=True)

        return joints

    def buildHierarchy(self):
        for j in self.joints:
            if self.skeleton.joint_tree[j]:
                self.joints[j].setParent(
                    self.joints[self.skeleton.joint_tree[j]])

    def initSkeleton(self):
        self.joints = self.createHalfSkeleton()

        self.orientSkeleton()

    def orientSkeleton(self):
        for jnt in self.joints.values():
            jnt.setParent(None)

        for grp in self.skeleton.orient_grps:

            jnt_list = pm.ls(grp)

            for i, jnt in enumerate(jnt_list):
                if len(jnt_list) < 3:
                    w_up = (0, 1, 0)
                elif ('Finger' in grp[-1]) and ('Thumb' not in grp[-1]):
                    w_up = getPoleVector(*pm.ls(
                        ['FingerMiddle1_R', 'FingerMiddle2_R', 'FingerMiddle3_R']))
                else:
                    w_up = getPoleVector(*pm.ls(*jnt_list[-3:]))

                if jnt != jnt_list[-1]:
                    orientJoint(jnt, jnt_list[i+1], world_up=w_up)

        for jnt_name in self.skeleton.manual_orients:
            self.orientManual(
                self.joints[jnt_name], **self.skeleton.manual_orients[jnt_name])

        self.buildHierarchy()

        for end_joint in [jnt for jnt in self.joints.values() if not jnt.listRelatives()]:
            end_joint.jointOrient.set((0, 0, 0))

    def buildSkeleton(self):
        self.orientSkeleton()
        self.buildHierarchy()

        self.createTwistJoints()

        for jnt_name in ['Clavicle_R', 'Hip_R', 'Breast_R']:
            pm.mirrorJoint(self.joints[jnt_name],
                           myz=True, sr=['_R', '_L'], mb=True)

        pm.mirrorJoint(self.joints['Eye_R'], myz=True,
                       sr=['_R', '_L'], mb=False)

    def createTwistJoints(self):
        for jnt_name in self.skeleton.twist_joints:
            jnt = pm.createNode('joint', n="{0}Twist{1}".format(
                jnt_name[:-2],  jnt_name[-2:]))

            jnt.radius.set(10)

            parent = pm.ls(jnt_name)[0]
            child = parent.listRelatives()[0]

            jnt.setParent(parent)
            pm.makeIdentity(jnt)
            jnt.setTranslation([child.translateX.get()/2, 0, 0])
            jnt.jointOrient.set((0, 0, 0))

    def orientManual(self, joint, aim_offset=(0, 1, 0), up_obj_name=None):

        tgt = pm.createNode('transform')
        pm.delete(pm.pointConstraint(joint, tgt))
        pm.move(tgt, aim_offset, relative=True)

        if up_obj_name:
            w_up = self.joints[up_obj_name].getTranslation(
                space='world') - joint.getTranslation(space='world')
        else:
            w_up = (0, 0, -1)

        orientJoint(joint, tgt, world_up=w_up)

        pm.delete(tgt)
