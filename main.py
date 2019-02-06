from daz.skeletons import SKEL_FULL, SKEL_HALF, TREE_FULL, TREE_HALF, JOINT_MAP
from daz.figures import loadMeshes
from daz.core import TargetMesh
import pymel.core as pm
import sys
sys.path.append("C:/Users/DSY/Documents/Maya/2018/scripts/daz")

TGT_BODY = {
    'name': 'Body',
    'file': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/Ref/Body_ChildF_Lo.ma"
}

TGT_HEAD = {
    'name': 'Head',
    'file': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/Ref/Head_ChildF_Lo.ma"
}

HEADNECK_VERTS = ['Head:HeadShape.vtx[1156:1174]',
                  'Head:HeadShape.vtx[1176:1178]',
                  'Head:HeadShape.vtx[1182]',
                  'Head:HeadShape.vtx[3076:3092]',
                  'Head:HeadShape.vtx[3094:3096]',
                  'Head:HeadShape.vtx[3100]',
                  'Body:BodyShape.vtx[11435:11478]']


def execTransfer():

    src_list = loadMeshes('G8F')

    for mesh_obj in src_list:
        mesh_obj.processMesh()

    src_mesh = pm.polyUnite([src.mesh for src in src_list])[0]

    for tgt in [TGT_BODY, TGT_HEAD]:
        tgt_obj = TargetMesh(src_mesh, tgt['name'], tgt['file'])
        tgt_obj.transfer()

    pm.delete(pm.ls('Genesis8Female*', type=['transform', 'joint']))
    pm.delete(src_mesh)
    pm.mel.eval('cleanUpScene 3')

    return tgt_obj


MIRROR_JOINT_LIST = [joint_name for joint_name in SKEL_HALF if joint_name[-2:]
                     == '_R' and joint_name[0:3] != 'Eye']
CENTER_JOINT_LIST = [
    joint_name for joint_name in JOINT_MAP if joint_name[-2:] == '_M']


def buildSkeleton():
    joint_dict = {jnt: pm.ls(
        JOINT_MAP[jnt])[0] for jnt in SKEL_HALF if jnt in JOINT_MAP and pm.ls(JOINT_MAP[jnt])}
    joints = {jntname: pm.createNode('joint', n=jntname)
              for jntname in SKEL_HALF}

    for j in joint_dict:
        joints[j].setTranslation(
            joint_dict[j].getTranslation(space='world'), space='world')
            
        if j == 'Spine1_M':
            joints[j].setTranslation(joints['COG_M'].getTranslation(space='world') + (0, 1, 0), space='world')

    for j in joints:
        if TREE_HALF[j]:
            joints[j].setParent(joints[TREE_HALF[j]])
            print('Parented {0} to {1}'.format(j, joints[TREE_HALF[j]]))

    free_joints = [joint for joint in joints if joint not in joint_dict]

    for j in free_joints:
        joints[j].setTranslation([0, 0, 0])


# STILL NOT RIGHT - FIX THIS
# def alignNormals():
#     verts = pm.ls(HEADNECK_VERTS)
#     pm.polySetToFaceNormal(verts)

#     for mesh in set(vert.node() for vert in verts):
#         pm.polySoftEdge([vert for vert in verts if vert.node()
#                          == mesh], angle=180, ch=False)

#     pm.polyAverageNormal(verts, prenormalize=False,
#                          postnormalize=False, distance=0.01)
