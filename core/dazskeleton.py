import pymel.core as pm
from ..data import getJointMap
from .util import getPoleVector, orientJoint


def setupJoints():

    pm.delete([name for name in ('Eye_L', 'Clavicle_L',
                                 'BreastBase_L', 'Hip_L') if pm.ls(name, type='joint')])

    joint_map = dict()

    for name in 'Genesis8Female', 'Genesis8Male':
        if pm.ls(name):
            joint_map = getJointMap(name)
            break

    if joint_map:

        # Save local transforms for unmapped joints
        aux_xforms = dict()
        for jnt in pm.ls('Root_M')[0].listRelatives(ad=True, type='joint'):
            if jnt.name() not in joint_map:
                aux_xforms[jnt] = jnt.getTranslation()

        # Move mapped joints
        for i, j in joint_map.items():
            jnt = pm.ls(i)[0]
            tgt = pm.ls(j)[0]

            pm.move(jnt, tgt.getTranslation(space='world'), pcp=True, ws=True)

        # Fix knee location for pole vector
        pole_vec = getPoleVector(*pm.ls(['Hip_R', 'Knee_R', 'Ankle_R']))
        pole_vec[1] = 0
        pole_len = pole_vec.length()

        tgt_vec = getPoleVector(*pm.ls(['Hip_R', 'Ankle_R', 'Toes_R']))
        tgt_vec[1] = 0
        tgt_vec = -tgt_vec.normal()

        diff_vec = tgt_vec*pole_len - pole_vec
        pm.move('Knee_R', diff_vec, r=True, ws=True, pcp=True)

        # Move spine base
        pm.move('Spine1_M', (0, 1, 0), r=True, ws=True, pcp=True)

        # Orient joints
        jnt_grps = [
            ['Hip_R', 'Knee_R', 'Ankle_R'],
            ['Shoulder_R', 'Elbow_R', 'Wrist_R'],
            'Spine*',
            'Index*',
            'Middle*',
            'Ring*',
            'Pinky*',
            'Thumb*'
        ]

        for grp in jnt_grps:
            orientChain(*pm.ls(grp), type='joint')

        # Re-apply transforms for unmapped joints
        for jnt in aux_xforms:
            jnt.setTranslation(aux_xforms[jnt])

        # Mirror joints
        for jnt in ['Eye_R', 'BreastBase_R']:
            pm.mirrorJoint(jnt, searchReplace=('_R', '_L'))

        for jnt in ['Clavicle_R', 'Hip_R']:
            pm.mirrorJoint(jnt, searchReplace=(
                '_R', '_L'), mirrorBehavior=True)


def orientChain(joint_list):

    if len(joint_list) < 3:
        pm.warning("Cannot orient a joint chain with fewer than 3 joints.")
        return

    up_vec = getPoleVector(*joint_list[-3:]).normal()

    for i, jnt in enumerate(joint_list[:-1]):
        orientJoint(jnt, joint_list[i+1], world_up=up_vec)

    joint_list[-1].jointOrient.set((0, 0, 0))
