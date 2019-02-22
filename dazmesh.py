import pymel.core as pm

MESH_FILES_F = {
    'Head': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/G8F_HeadBase.ma",
    'Body': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/G8F_BodyBase.ma"
}

MESH_FILES_M = {
    'Head': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/G8M_HeadBase.ma",
    'Body': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/G8M_BodyBase.ma"
}

global MESH_FILES
MESH_FILES = dict()

FIGURE_F = [
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

FIGURE_M = [
    {
        'mesh_name': 'Genesis8Male',
        'uvadj': {
            8: [(16114, 17265)]
        },
        'del_list': []
    },
    {
        'mesh_name': 'Genesis8MaleEyelashes',
        'uvadj': {
            7: [(0, 251)]
        },
        'del_list': [
            (252, 351)
        ]
    }
]


def buildDazMeshes():
    if pm.ls('Genesis8Female'):
        figure_list = FIGURE_F
        figure_name = 'Genesis8Female'
        global MESH_FILES
        MESH_FILES = MESH_FILES_F
    elif pm.ls('Genesis8Male'):
        figure_list = FIGURE_M
        figure_name = 'Genesis8Male'
        global MESH_FILES
        MESH_FILES = MESH_FILES_M
    else:
        raise MayaNodeError("Source mesh not found")

    # Move UVs
    for uvd in figure_list:
        moveUVs(uvd)
        deleteFaces(uvd)

    # Merge base & eyelash meshes
    base_mesh = pm.polyUnite(*[pm.ls(fig['mesh_name']+'FBXASC046Shape',
                                     type='transform')[0] for fig in figure_list], n='Base', muv=1)[0]
    pm.delete(base_mesh, ch=True)

    # Delete joints
    pm.delete(figure_name)

    # Rename shapes
    renameShapes(figure_name)

    # Delete unneeded morphs
    for morph in pm.ls(['*PuckerWide', '*Pucker_*', '*OpenLips*'], type='transform'):
        pm.delete(morph)

    # Build morph targets
    for mtype in ['Head', 'Body']:
        buildMorphTargets(mtype, base_mesh)

    # Clean up
    pm.delete('JCM*', 'POS*', 'Base')
    pm.mel.eval('cleanUpScene 3')


def buildMorphTargets(mesh_type, base_mesh):
    pm.importFile(MESH_FILES[mesh_type], namespace=mesh_type)
    tgt_mesh = pm.ls(mesh_type+':Mesh')[0]

    pm.transferAttributes(
        base_mesh, tgt_mesh, transferPositions=True, sampleSpace=3, targetUvSpace='UVOrig')
    pm.delete(tgt_mesh, ch=True)

    target_lists = {
        'Head': pm.ls('POS_*', type='transform') + pm.ls(['JCM*' + limb + '*' for limb in ['Collar', 'Neck', 'Shldr']], type='transform'),
        'Body': pm.ls('JCM_*', type='transform')
    }

    for src_mesh in target_lists[mesh_type]:
        new_mesh = duplicateClean(tgt_mesh, name=mesh_type+':'+src_mesh.name())
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


def renameShapes(figure_name):
    for shp in pm.ls(figure_name+'__*', type='transform'):
        base_name = shp.name()[(len(figure_name)+2):]
        pm.rename(shp, 'BODY_'+base_name)
        if pm.ls(figure_name+'Eyelashes__'+base_name):
            pm.rename(figure_name+'Eyelashes__' +
                      base_name, 'LASHES_'+base_name)

        newmesh = pm.polyUnite(shp, 'LASHES_'+base_name,
                               n='MERGED_'+base_name, muv=1)[0]
        pm.delete(newmesh, ch=True)

        if 'eCTRL' in newmesh.name():
            pm.rename(newmesh, newmesh.name().replace('MERGED_eCTRL', 'POS_'))
        else:
            pm.rename(newmesh, newmesh.name().replace(
                'pJCM', '').replace('MERGED_', 'JCM_'))


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


buildDazMeshes()
