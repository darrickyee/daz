import os
import sys
import pymel.core as pm
from .core import TargetMesh
from .figures import loadMeshes
from .skeletons import BaseSkeleton, JOINT_MAP

bs = BaseSkeleton()
SKEL_HALF = bs.joint_names
TREE_HALF = bs.joint_tree
ORIENT_GRPS = bs.orient_grps
WORLDORIENT_JNTS = bs.manual_orients
TWIST_JNTS = bs.twist_joints
MANUAL_XFORMS = bs.manual_xforms

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


# STILL NOT RIGHT - FIX THIS
# def alignNormals():
#     verts = pm.ls(HEADNECK_VERTS)
#     pm.polySetToFaceNormal(verts)

#     for mesh in set(vert.node() for vert in verts):
#         pm.polySoftEdge([vert for vert in verts if vert.node()
#                          == mesh], angle=180, ch=False)

#     pm.polyAverageNormal(verts, prenormalize=False,
#                          postnormalize=False, distance=0.01)
