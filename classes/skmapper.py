import pymel.core as pm
from .baseskeleton import BaseSkeleton
from ..core.util import getPoleVector, orientJoint, getRootsInSet


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
            self.joint_map.map[jnt])[0] for jnt in self.skeleton.joint_names if jnt in self.joint_map.map and pm.ls(self.joint_map.map[jnt])}

        self.joints = {jntname: pm.createNode('joint', n=jntname)
                       for jntname in self.skeleton.joint_names}

        for jnt in self.joints.values():
            jnt.radius.set(10)

        for j in joint_dict:
            self.joints[j].setTranslation(
                joint_dict[j].getTranslation(space='world'), space='world')

            if j == 'Spine1_M':
                self.joints[j].setTranslation(self.joints['COG_M'].getTranslation(
                    space='world') + (0, 1, 0), space='world')

        self.buildHierarchy()

        for j in self.joint_map.manual_xforms:
            self.joints[j].setTranslation((0, 0, 0))
            pm.move(self.joints[j],
                    self.joint_map.manual_xforms[j], relative=True)

        self.orientSkeleton()

        for j in [joint for joint in self.joints.values()
                  if 'End' in joint.nodeName() and joint.nodeName() not in self.joint_map.manual_xforms]:
            if [round(t, 5) for t in j.getTranslation(space='world')] == [0.0, 0.0, 0.0]:
                j.jointOrient.set((0, 0, 0))
                j.setTranslation((2, 0, 0))

    def buildHierarchy(self):
        for j in self.joints:
            if self.skeleton.joint_tree[j]:
                self.joints[j].setParent(
                    self.joints[self.skeleton.joint_tree[j]])

    def initSkeleton(self):
        self.createHalfSkeleton()

        self.orientSkeleton()

    def orientSkeleton(self):

        # Unparent joints
        for jnt in self.joints.values():
            jnt.setParent(None)

        for grp in self.skeleton.orient_grps:

            jnt_list = pm.ls(grp)

            for i, jnt in enumerate(jnt_list):
                if len(jnt_list) < 3:
                    w_up = (0, 1, 0)
                # FOR DAZ: Use middle finger orient for all
                elif ('Finger' in jnt.name()) and ('Thumb' not in jnt.name()):
                    w_up = getPoleVector(
                        *pm.ls('FingerMiddle1_R', 'FingerMiddle2_R', 'FingerMiddle3_R'))
                else:
                    w_up = getPoleVector(*pm.ls(*jnt_list[-3:]))

                if jnt != jnt_list[-1]:
                    orientJoint(jnt, jnt_list[i+1], world_up=w_up)
                else:
                    jnt.setParent(jnt_list[-2])
                    jnt.jointOrient.set((0, 0, 0))
                    jnt.setParent(None)

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

        for jnt in getRootsInSet([jnt for jnt in self.joints.values()
                                  if '_R' in jnt.name() and 'Eye' not in jnt.name()]):
            pm.mirrorJoint(jnt, myz=True, sr=['_R', '_L'], mb=True)

        pm.mirrorJoint(self.joints['Eye_R'], myz=True,
                       sr=['_R', '_L'], mb=False)

    def createTwistJoints(self):
        for jnt_name in self.joint_map.twist_joints:
            jnt = pm.createNode('joint', n="{0}Twist{1}".format(
                jnt_name[:-2], jnt_name[-2:]))

            jnt.radius.set(10)

            parent = pm.ls(jnt_name)[0]
            child = parent.listRelatives()[0]

            jnt.setParent(parent)
            pm.makeIdentity(jnt)
            jnt.setTranslation([child.translateX.get()/2, 0, 0])
            jnt.jointOrient.set((0, 0, 0))

    def orientManual(self, joint, aim_offset=(1, 0, 0), up_obj_name=None, **kwargs):

        tgt = pm.createNode('transform')
        pm.delete(pm.pointConstraint(joint, tgt))
        pm.move(tgt, aim_offset, relative=True)

        if up_obj_name:
            w_up = self.joints[up_obj_name].getTranslation(
                space='world') - joint.getTranslation(space='world')
        else:
            w_up = kwargs.pop('world_up', None) or (0, 0, -1)

        orientJoint(joint, tgt, world_up=w_up, **kwargs)

        pm.delete(tgt)

# A comment