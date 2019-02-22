import pymel.core as pm
from .core import TargetMesh
from .figures import loadMeshes


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


FIGURES = [
    {
        'mesh_name': 'Genesis8Female',
        'uvadj': {
            8: [(16286, 17003)]
        },
        'del_list': []
    },
    {
        'mesh_name': 'Genesis8FemaleEyelashes',
        'uvadj': {
            7: [(0, 251)]
        },
        'del_list': [
            (252, 351)
        ]
    }
]


def buildDazMeshes():

    # Move UVs
    for uvd in FIGURES:
        moveUVs(uvd)
        deleteFaces(uvd)

    # Merge base & eyelash meshes
    base_mesh = pm.polyUnite(*[pm.ls(fig['mesh_name']+'FBXASC046Shape',
                                     type='transform')[0] for fig in FIGURES], n='Base')[0]
    pm.delete(base_mesh, ch=True)

    # Delete joints
    pm.delete('Genesis8Female')

    # Rename shapes
    renameShapes()

    # Delete unused eyelash morph targets
    pm.delete('Genesis8FemaleEyelashes_*')

    # Import head/body mesh
    pm.importFile(
        "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/Ref/Head_ChildF_Lo.ma")
    tgt_mesh = pm.ls('Mesh')[0]

    # Transfer shape to base mesh
    pm.transferAttributes(
        base_mesh, tgt_mesh, transferPositions=True, sampleSpace=3, targetUvSpace='UVOrig')
    pm.delete(tgt_mesh, ch=True)

    # Build morph targets
    for src_mesh in pm.ls('POS_*', type='transform'):
        new_mesh = duplicateClean(tgt_mesh, name='new_'+src_mesh.name())
        pm.transferAttributes(
            src_mesh, new_mesh, transferPositions=True, sampleSpace=3, targetUvSpace='UVOrig')
        pm.delete(new_mesh, ch=True)


def moveUVs(uvadj_dict):
    for mesh in pm.ls([uvadj_dict['mesh_name']+'_*', uvadj_dict['mesh_name']+'FBX*'], type='transform'):
        for tile in uvadj_dict['uvadj']:
            face_sets = [mesh.f[face_range[0]: face_range[1]]
                         for face_range in uvadj_dict['uvadj'][tile]]
            offsets = [tile - int(face_set.getUVs()[0][0])
                       for face_set in face_sets]
            for face_set, offset in zip(face_sets, offsets):
                pm.polyEditUV(face_set, uValue=offset, relative=True)


def deleteFaces(uvadj_dict):
    for mesh in pm.ls([uvadj_dict['mesh_name']+'_*', uvadj_dict['mesh_name']+'FBX*'], type='transform'):
        for face_range in uvadj_dict['del_list']:
            pm.delete(mesh.f[face_range[0]: face_range[1]])


def renameShapes():
    for shp in pm.ls('Genesis8Female__eCTRL*', type='transform'):
        base_name = shp.name()[21:]
        pm.rename(shp, 'BODY_'+base_name)
        if pm.ls('Genesis8FemaleEyelashes__eCTRL'+base_name):
            pm.rename('Genesis8FemaleEyelashes__eCTRL' +
                      base_name, 'LASHES_'+base_name)

    for shp in pm.ls('BODY_*', type='transform'):
        base_name = shp.name()[5:]
        newmesh = pm.polyUnite(shp, 'LASHES_'+base_name, n='POS_'+base_name)
        pm.delete(newmesh, ch=True)

    for shp in pm.ls('Genesis8Female_*', type='transform'):
        base_name = shp.name()[16:]
        if base_name[:4] == 'pJCM':
            pm.rename(shp, 'JCM_'+base_name[4:])
        else:
            pm.rename(shp, 'JCM_'+base_name)


TGT_BODY = {
    'name': 'Body',
    'file': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/Ref/Body_ChildF_Lo.ma"
}

TGT_HEAD = {
    'name': 'Head',
    'file': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/Ref/Head_ChildF_Lo.ma"
}


def duplicateClean(src_mesh, name=None):
    """
    Creates a "clean" duplicate of an input mesh

    Parameters
    ----------
    src_mesh : nt.Transform or nt.Mesh
        Shape to duplicate
    name : str
        Optional name for new mesh (defaults to source mesh name)

    Returns
    -------
    nt.Transform
        Transform node for duplicate mesh
    """

    new_name = name or src_mesh.nodeName()

    new_mesh = pm.polyCube(name=new_name)[0]
    pm.delete(new_mesh, ch=True)

    src_mesh.outMesh.connect(new_mesh.inMesh)
    pm.transferShadingSets(src_mesh, new_mesh, sampleSpace=0, searchMethod=3)
    pm.delete(new_mesh, ch=True)

    return new_mesh
