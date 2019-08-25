import pymel.core as pm
import as5util
from .core.util import getFigureName
from . import buildDazMeshes, applySkins


def rigDazFigure(name, path='C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/scenes'):
    """Need to load DAZ FBX first"""

    figure = getFigureName()

    # File paths
    mesh_path = '{0}/Mesh/Ref/Mesh_{1}.ma'.format(path, name)
    rig_path = '{0}/Rig/Ref/Rig_{1}.ma'.format(path, name)
    skel_path = '{0}/Rig/Ref/Skel_{1}.ma'.format(path, name)
    anim_path = '{0}/Rig/Ref/AnimRig_{1}.mb'.format(path, name)

    # Build and save meshes
    print('Converting DAZ figure geometry:')
    buildDazMeshes()
    print('Exporting geometry...')
    meshes = pm.ls(('*Mesh', '*Morphs'), type='transform', r=True)
    face_sets = pm.ls('Fac*', recursive=True)
    pm.select(meshes + face_sets, ne=True)
    pm.exportSelected(mesh_path, force=True)
    print('Geometry exported to {}'.format(mesh_path))

    # Load and setup AS5 skeleton
    print('Loading and setting up AS5 skeleton...')
    as5util.preBuild(figure, load=True)

    # Edit joint placement, if necessary

    # Remove shading face sets from namespaces so they don't get deleted
    for sel_set in pm.ls('Fac*', recursive=True):
        pm.rename(sel_set, sel_set.name().split(':')[1])
    # Delete geometry + namespaces
    for name_space in 'HeadGeo', 'BodyGeo':
        pm.namespace(rm=name_space, deleteNamespaceContent=True)

    # Reference geometry
    pm.createReference(mesh_path, defaultNamespace=True)

    # Build AS5 rig
    print('Building AS5 rig...')
    pm.mel.eval(
        'source "C:/Users/Darrick/Documents/Maya/scripts/AdvancedSkeleton5.mel";')
    pm.mel.eval('asBuildAdvancedSkeleton();')

    print('Executing post-build script...')
    as5util.postBuild(figure)
    pm.mel.eval('asSetBuildPose("");')

    # Skin mesh and apply blendshapes
    print('Skinning geometry and applying weight drivers...')
    applySkins()

    # Add to layers, cleanup
    print('Cleaning up...')
    layer = pm.ls('GeoLayer')[0] if pm.ls(
        'GeoLayer') else pm.createDisplayLayer(name='GeoLayer')
    layer.displayType.set(2)

    for grp in pm.ls(('Mesh', 'Morphs'), r=True):
        grp.setParent('Geometry')
        layer.addMembers(grp)

    pm.delete('Genesis8*')
    for grp in 'Geometry', 'DeformationSystem':
        pm.parent(grp, None)

    # Export skeleton
    print('Exporting skeleton to {}'.format(skel_path))
    pm.select('DeformationSystem', r=True)
    pm.exportSelected(skel_path, force=True, channels=False)

    # Save rig file
    print('Saving rig file to {}'.format(rig_path))
    pm.saveAs(rig_path)
    print('Saving animRig file to {}'.format(anim_path))
    refs = pm.ls(type='reference')
    for ref in refs:
        file_ref = pm.FileReference(ref)
        file_ref.importContents()
    pm.saveAs(anim_path)
    pm.openFile(rig_path, force=True)
    print('Conversion complete.')


FIGURE_EDGES = {
    'g8f': {
        'HeadGeo': 10308,
        'BodyGeo': 45788
    }
}


def convertSmoothSkin(name, path='C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/scenes'):

    pm.newFile(force=True)
    pm.importFile(path+'/Mesh/Ref/Mesh_'+name+'.ma')
    pm.importFile(path+'/Rig/Ref/Skel_'+name+'.ma')

    print('Smoothing meshes.  Please wait...')
    for mesh in pm.ls(type='mesh'):
        pm.polySmooth(mesh, ch=False)

    pm.select(None)

    print('Averaging seam vertex normals...')
    edge_dict = FIGURE_EDGES['g8f']
    for name, edge in edge_dict.items():
        mesh = pm.ls(name+':Mesh')[0]
        pm.polySelect(mesh, edgeBorder=edge, add=True)

    pm.select(pm.polyListComponentConversion(pm.ls(sl=True), toVertex=True))
    pm.polyAverageNormal()
    pm.select(None)

    print('Applying skins...')
    applySkins()
    print('Saving file to {}'.format(
        '{0}/Rig/Ref/Skin_{1}.ma'.format(path, name)))
    print('Completed.')
