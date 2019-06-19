import pymel.core as pm

MESH_FILES_F = {
    'Head': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/G8F_HeadBase.ma",
    'Body': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/G8F_BodyBase.ma"
}

MESH_FILES_M = {
    'Head': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/G8M_HeadBase.ma",
    'Body': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes/Mesh/G8M_BodyBase.ma"
}

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

    # Unparent mesh and rescale blendshape targets
    pm.delete(figure_name+'Genitalia')
    for shp in [figure_name+'FBXASC046Shape', figure_name+'EyelashesFBXASC046Shape']:
        pm.ls(shp)[0].setParent(None)
    tgt_scale = pm.ls(figure_name)[0].getScale()
    for shp in pm.ls([figure_name+'__*', figure_name+'Eyelashes__*'], type='transform'):
        shp.setScale(tgt_scale)
        pm.makeIdentity(shp, apply=True)

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

    # Build and group morph targets
    for mtype in ['Head', 'Body']:
        buildMorphTargets(mtype, base_mesh)
        pm.group([shp for shp in pm.ls(mtype+'Geo:*')
                  if 'Mesh' not in shp.name()], n=mtype+'Geo:Morphs')

    # Clean up
    pm.delete('JCM*', 'POS*', 'Base')
    pm.mel.eval('cleanUpScene 3')


def buildMorphTargets(mesh_type, base_mesh):
    pm.importFile(MESH_FILES[mesh_type], namespace=mesh_type+'Geo')
    tgt_mesh = pm.ls(mesh_type+'Geo:Mesh')[0]

    # Transfer existing blendshapes on imported mesh
    if tgt_mesh.inMesh.listConnections(type='blendShape'):
        dup_mesh = duplicateClean(tgt_mesh, name='TMP_'+base_mesh.name())
        bs_node = tgt_mesh.inMesh.listConnections(type='blendShape')[0]

        # Transfer new shape to dup_mesh
        pm.transferAttributes(
            base_mesh, dup_mesh, transferPositions=True, sampleSpace=3, targetUvSpace='UVOrig')
        pm.delete(dup_mesh, ch=True)
        # Add as target to tgt_mesh
        pm.blendShape(bs_node, edit=True, target=(
            tgt_mesh, len(bs_node.listAliases()), dup_mesh, 1.0))
        # Set new shape and lock
        bs_node.setAttr(dup_mesh.name(), 1.0, lock=True)

        new_shapes = transferShapes(
            bs_node, dup_mesh, tgt_prefix=mesh_type+'Geo:NEW_')

        # Delete existing blendshape targets
        for shp in bs_node.inputTarget.listConnections():
            pm.delete(shp)

        for shp in new_shapes:
            pm.rename(shp, shp.name().replace('NEW_', ''))

        pm.delete(tgt_mesh, ch=True)

    pm.transferAttributes(
        base_mesh, tgt_mesh, transferPositions=True, sampleSpace=3, targetUvSpace='UVOrig')
    pm.delete(tgt_mesh, ch=True)

    target_lists = {
        'Head': pm.ls('POS_*', type='transform') + pm.ls(['JCM*' + limb + '*' for limb in ['Collar', 'Neck', 'Shldr']], type='transform'),
        'Body': pm.ls('JCM_*', type='transform')
    }

    for src_mesh in target_lists[mesh_type]:
        new_mesh = duplicateClean(
            tgt_mesh, name=mesh_type+'Geo:'+src_mesh.name())
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


def transferShapes(src_bsnode, tgt_node, tgt_prefix='_'):
    """
    Generates new blendshape meshes

    Parameters
    ----------
    src_bsnode : nt.BlendShape
        BlendShape node whose shapes are to be copied
    tgt_node : nt.Transform or nt.Mesh
        Target mesh from which to generate new blendshapes
    tgt_prefix : str
        Optional prefix for new meshes (default = '_')

    Returns
    -------
    list
        List of nt.Transforms for newly-generated meshes
    """

    prefix = tgt_prefix
    src_mesh = src_bsnode.getBaseObjects()[0]

    new_shapes = list()
    bs_list = src_bsnode.listAliases()
    bs_list.sort()

    for bs_name, bs_attr in bs_list:

        # Skip blendshape if weight cannot be changed
        if not bs_attr.isSettable():
            pm.warning("{0} is locked or connected; skipping".format(bs_name))
            continue

        # Create target shape
        tgt_shape = duplicateClean(tgt_node, name=prefix + bs_name)

        # Ensure blendshape weight is reset to zero
        bs_attr.set(0)

        # Create wrap deformer
        pm.select([tgt_shape, src_mesh], r=True)
        wrap_name = pm.mel.eval(
            'doWrapArgList "7" { "1","0","1", "2", "1", "1", "0", "0" };')

        # Get "base" shape node from wrap deformer (needed for later deletion)
        wrap_node = pm.ls(wrap_name)[0]
        wrap_base = pm.listConnections(wrap_node.basePoints)[0]

        # Set blendshape to 1, bake target shape, delete remaining wrap node
        bs_attr.set(1)
        pm.delete(tgt_shape, ch=True)
        pm.delete(wrap_base)

        # Reset blendshape weight
        bs_attr.set(0)

        new_shapes.append(tgt_shape)

    return new_shapes
