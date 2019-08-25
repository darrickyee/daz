import pymel.core as pm
from ..data import getJointMap
from .util import getPoleVector, orientJoint

SKEL_FILES = {
    'g8f': 'C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/assets/Chars/Skel/SK_G8F.ma'
}

# Attempt auto-move
# 'VtxBreastMid_R' VtxBreastEnd_R etc.


def getAverageLoc(node_list):
    locs = [pm.datatypes.Vector(pm.xform(node, query=True, t=True))
            for node in node_list]

    return sum(locs)/len(locs)


def setupJoints():

    pm.delete(
        'Eye_L',
        'Clavicle_L',
        'BreastBase_L',
        'Hip_L',
        'ButtockBase_L',
        'CTRL*_L'
    )

    joint_map = dict()

    for name in 'Genesis8Female', 'Genesis8Male':
        if pm.ls(name):
            joint_map = getJointMap(name)
            break

    if joint_map:
        matchTranslations(joint_map)


def buildJoints():

    orientSkeleton()

    # Set twist translations
    for jnt in pm.ls('*Twist_R', type='joint'):
        jnt.translateY.set(0)
        jnt.translateZ.set(0)

    # Set control joint translations
    matchCtrlTranslations()

    # Mirror joints
    for jnt in 'Eye_R', 'CTRLIKArm_R', 'CTRLIKLeg_R', 'CTRLPoleArm_R', 'CTRLPoleLeg_R':
        pm.mirrorJoint(jnt, searchReplace=('_R', '_L'))

    for jnt in 'Clavicle_R', 'Hip_R', 'BreastBase_R', 'ButtockBase_R':
        pm.mirrorJoint(jnt, searchReplace=('_R', '_L'), mirrorBehavior=True)


def matchTranslations(joint_map):

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

    pole_vec = getPoleVector(
        *pm.ls(['Hip_R', 'Knee_R', 'Ankle_R']))
    pole_vec[1] = 0
    pole_len = pole_vec.length()

    tgt_vec = getPoleVector(
        *pm.ls(['Hip_R', 'Ankle_R', 'Toes_R']))
    tgt_vec[1] = 0
    tgt_vec = -tgt_vec.normal()

    diff_vec = tgt_vec*pole_len - pole_vec
    pm.move('Knee_R', diff_vec, r=True, ws=True, pcp=True)

    # Move spine base
    pm.move('Spine1_M', pm.ls('COG_M')[0].getTranslation(
        space='world')+(0, 1, 0), ws=True, pcp=True)

    # Re-apply transforms for unmapped joints
    for jnt in aux_xforms:
        jnt.setTranslation(aux_xforms[jnt])


def matchCtrlTranslations():

    ctrl_map = {
        'CTRLIKArm_R': 'Wrist_R',
        'CTRLIKLeg_R': 'Ankle_R'
    }

    for ctrl in ctrl_map:
        pm.delete(pm.pointConstraint(ctrl_map[ctrl], ctrl))

    pole_map = {
        'CTRLPoleArm_R': ['Shoulder_R', 'Elbow_R', 'Wrist_R'],
        'CTRLPoleLeg_R': ['Hip_R', 'Knee_R', 'Ankle_R']
    }

    for pole in pole_map:
        mid = pm.ls(pole_map[pole][1])[0]
        loc = getPoleVector(
            *pm.ls(pole_map[pole])).normal()*20 + mid.getTranslation(ws=True)
        pm.move(pole, loc)

    eye_ht = pm.ls('Eye_R')[0].getTranslation(ws=True)[1]
    aim_loc = pm.ls('CTRLAimEye_M')[0].getTranslation(ws=True)
    aim_loc[1] = eye_ht
    pm.move('CTRLAimEye_M', aim_loc)


def orientSkeleton():
    # Orient joints
    jnt_grps = [
        ['Hip_R', 'Knee_R', 'Ankle_R'],
        ['Clavicle_R', 'Shoulder_R', 'Elbow_R', 'Wrist_R', 'MiddleFinger1_R'],
        ['Spine{}_M'.format(i) for i in range(1, 5)] +
        ['Neck_M', 'Head_M', 'HeadEnd_M'],
        ['IndexFinger{}_R'.format(i) for i in range(1, 5)],
        ['MiddleFinger{}_R'.format(i) for i in range(1, 5)],
        ['RingFinger{}_R'.format(i) for i in range(1, 5)],
        ['PinkyFinger{}_R'.format(i) for i in range(1, 5)],
        ['ThumbFinger{}_R'.format(i) for i in range(1, 5)],
        ['Toes_R', 'ToesEnd_R'],
        ['BreastBase_R', 'BreastMid_R', 'BreastEnd_R'],
        ['Jaw_M', 'JawEnd_M']
    ]

    for grp in jnt_grps:
        adjustOrientChain(pm.ls(grp))

    # Custom orient for Ankles
    jnt = pm.ls('Ankle_R')[0]
    tgt = pm.ls('Toes_R')[0]
    up_tgt = tgt.getTranslation(ws=True) - jnt.getTranslation(ws=True)

    orientJoint(jnt, jnt.getTranslation(ws=True)+(0, -1, 0), world_up=up_tgt)

    for jnt in pm.ls('Root_M')[0].listRelatives(ad=True, type='joint'):
        if not jnt.listRelatives():
            jnt.jointOrient.set((0, 0, 0))


def adjustOrient(joint, target):
    """Adjusts the orientation of a joint by pointing the x-axis toward `target` while 
    preserving its current up-axis as closely as possible.

    Parameters
    ----------
    joint : pm.nt.Joint

    target : pm.nt.Transform
        Note: Only the translation of the transform node is used.
    """

    inv_x = target.translateX.get() < 0
    x_axis = {
        False: (1, 0, 0),
        True: (-1, 0, 0)
    }

    orientJoint(joint, target.getTranslation(ws=True), aim_axis=x_axis[inv_x],
                world_up=joint.getMatrix(ws=True)[1][:3])


def adjustOrientChain(joint_list):

    if len(joint_list) < 2:
        pm.warning("Cannot orient a joint chain with fewer than 2 joints.")
        return

    for i, jnt in enumerate(joint_list[:-1]):
        adjustOrient(jnt, joint_list[i+1])
