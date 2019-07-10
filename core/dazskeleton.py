import pymel.core as pm
from ..data import getJointMap


def setupJoints():
    joint_map = dict()

    for name in 'Genesis8Female', 'Genesis8Male':
        if pm.ls(name):
            joint_map = getJointMap(name)
            break

    if joint_map:

        #
        aux_xforms = dict()
        for jnt in pm.ls('Root_M')[0].listRelatives(ad=True, type='joint'):
            if jnt.name() not in joint_map:
                aux_xforms[jnt] = jnt.getTranslation()

        for i, j in joint_map.items():
            jnt = pm.ls(i)[0]
            tgt = pm.ls(j)[0]

            pm.move(jnt, tgt.getTranslation(space='world'), pcp=True, ws=True)

        for jnt in aux_xforms:
            jnt.setTranslation(aux_xforms[jnt])
