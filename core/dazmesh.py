import pymel.core as pm
from ..figures import getFigure
from .util import duplicateClean, transferShapes, invertBlendShapeWeights, setBlendShapeWeights

MESH_FILES_F = {
    'head_file': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/assets/Chars/Geo/G8F_HeadBase.ma",
    'body_file': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/assets/Chars/Geo/G8F_BodyBase.ma"
}

MESH_FILES_M = {
    'head_file': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/assets/Chars/Geo/G8M_HeadBase.ma",
    'body_file': "C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/assets/Chars/Geo/G8M_BodyBase.ma"
}


def buildDazMeshes():

    if pm.ls('Genesis8Female'):
        figure = getFigure('g8f', **MESH_FILES_F)
    elif pm.ls('Genesis8Male'):
        figure = getFigure('g8m', **MESH_FILES_M)
    else:
        raise pm.MayaNodeError("Source mesh not found")
    print("Processing figure '{}':".format(figure.name))

    # Delete unneeded skeleton/mesh
    if pm.ls(figure.name+'Genitalia'):
        pm.delete(figure.name+'Genitalia')

    # Unbind skins
    for shp in (mesh_name+'FBXASC046Shape' for mesh_name in figure.mesh_names):
        pm.skinCluster(pm.ls(shp)[0], edit=True, unbind=True)

    # Transfer scale from skeleton to blendshape target meshes
    tgt_scale = pm.ls(figure.name)[0].getScale()
    for shp in pm.ls((mesh_name+'__*' for mesh_name in figure.mesh_names), type='transform'):
        shp.setScale(tgt_scale)
        pm.makeIdentity(shp, apply=True)

    # Move UVs, delete faces, merge base & eyelash meshes, delete history
    figure.process()

    # Rename shapes
    _renameShapes(figure.name)

    # Delete unneeded morphs
    for morph in pm.ls(['*PuckerWide', '*Pucker_*', '*OpenLips*'], type='transform'):
        pm.delete(morph)

    # Build and group morph targets
    print('Building morph targets...')
    for mtype in 'Head', 'Body':
        _buildMorphTargets(mtype, figure)
        pm.group([shp for shp in pm.ls(mtype+'Geo:*')
                  if 'Mesh' not in shp.name()], n=mtype+'Geo:Morphs')

    print('Editing Eyelid morphs.  Please wait...')
    _buildEyelidMorphTargets()

    # Clean up
    # pm.delete(figure.name)
    print('Cleaning up...')
    pm.delete(pm.ls('JCM*', 'POS*', 'SHP*', 'Base'))
    pm.mel.eval('cleanUpScene 3')

    # Group, sort, hide morph shapes
    for mtype in 'Head', 'Body':
        grp_node = pm.ls(mtype+'Geo:Morphs')[0]
        grp_node.visibility.set(False)

        # Sort morph nodes
        names = [node.name()
                 for node in grp_node.listRelatives(type='transform')]
        names.sort()
        for name in names:
            node = pm.ls(name)[0]
            node.setParent(None)
            node.setParent(grp_node)

    pm.warning(
        'It may be necessary to average normals between Head and Body meshes.')


def _buildEyelidMorphTargets(morph_names=None):
    morph_names = morph_names or (
        'HeadGeo:POS_EyesClosedL', 'HeadGeo:POS_EyesClosedR')

    # Create head with original eyelid blendshapes
    head_mesh = duplicateClean('HeadGeo:Mesh', name='TMP_Head')
    pm.select(morph_names, head_mesh)
    bs_node = pm.blendShape(n='TMP_Morphs')[0]
    wt_dict = dict(bs_node.listAliases())

    # Start with Upper by setting lower vertex weights to 0
    vtx_idx = pm.ls('HeadGeo:VtxEyelidsLower')[0].members()[0].indices()
    setBlendShapeWeights(bs_node, indices=vtx_idx)

    targets = list()

    for morph in morph_names:
        side = morph[-1]
        morph_base = morph.split(':')[1]
        wt_dict[morph_base].set(1)
        targets.append(duplicateClean(head_mesh, name=morph[:-1]+'Upper'+side))

        # Invert weights
        all_weights = (bs_node.inputTarget[0].baseWeights[i]
                       for i in range(len(bs_node.getBaseObjects()[0].vtx)))
        for weight in all_weights:
            weight.set(0)
        setBlendShapeWeights(bs_node, indices=vtx_idx, weight=1.0)

        targets.append(duplicateClean(head_mesh, name=morph[:-1]+'Lower'+side))

        wt_dict[morph_base].set(0)
        invertBlendShapeWeights(bs_node)

    pm.delete('TMP_Morphs', morph_names, head_mesh)
    for target in targets:
        target.setParent('HeadGeo:Morphs')


def _buildMorphTargets(mesh_type, figure):
    pm.importFile(figure.files[mesh_type], namespace=mesh_type+'Geo')
    tgt_mesh = pm.ls(mesh_type+'Geo:Mesh')[0]

    # Transfer existing blendshapes on imported mesh
    if tgt_mesh.inMesh.listConnections(type='blendShape'):
        dup_mesh = duplicateClean(tgt_mesh, name='TMP_'+figure.mesh.name())
        bs_node = tgt_mesh.inMesh.listConnections(type='blendShape')[0]

        # Transfer new shape to dup_mesh
        pm.transferAttributes(
            figure.mesh, dup_mesh, transferPositions=True, sampleSpace=3, targetUvSpace='UVOrig')
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

    # Transfer new figure shape to base geo
    pm.transferAttributes(
        figure.mesh, tgt_mesh, transferPositions=True, sampleSpace=3, targetUvSpace='UVOrig')
    pm.delete(tgt_mesh, ch=True)

    target_lists = {
        'Head': pm.ls(('POS_*', 'SHP_*'), type='transform') + pm.ls(['JCM*' + limb + '*' for limb in ['Collar', 'Neck', 'Shldr']], type='transform'),
        'Body': pm.ls(('JCM_*', 'SHP_*'), type='transform')
    }

    # Create morph target meshes
    for src_mesh in target_lists[mesh_type]:
        new_mesh = duplicateClean(
            tgt_mesh, name=mesh_type+'Geo:'+src_mesh.name())
        pm.transferAttributes(
            src_mesh, new_mesh, transferPositions=True, sampleSpace=3, targetUvSpace='UVOrig')
        pm.delete(new_mesh, ch=True)


def _renameShapes(figure_name):
    for shp in pm.ls(figure_name+'__*', type='transform'):
        base_name = shp.name().split('__')[1]
        pm.rename(shp, 'BODY_'+base_name)
        if pm.ls(figure_name+'Eyelashes__'+base_name):
            pm.rename(figure_name+'Eyelashes__' +
                      base_name, 'LASHES_'+base_name)

        newmesh = pm.polyUnite(shp, 'LASHES_'+base_name,
                               n='MERGED_'+base_name, muv=1)[0]
        pm.delete(newmesh, ch=True)

        if 'eCTRL' in newmesh.name():
            pm.rename(newmesh, newmesh.name().replace('MERGED_eCTRL', 'POS_'))
        elif 'CTRL' in newmesh.name():
            pm.rename(newmesh, newmesh.name().replace('MERGED_CTRL', 'SHP_'))
        else:
            pm.rename(newmesh, newmesh.name().replace(
                'pJCM', '').replace('MERGED_', 'JCM_'))
