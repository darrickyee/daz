import pymel.core as pm
import as5util
from .core.util import getFigureName
from . import buildDazMeshes, applySkins


def rigDazFigure(name, path='C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/scenes'):
    """Need to load DAZ FBX first"""

    figure = getFigureName()

    # Build and save meshes
    buildDazMeshes()
    meshes = pm.ls(('*Mesh', '*Morphs'), type='transform', r=True)
    face_sets = pm.ls('Fac*', recursive=True)
    pm.select(meshes + face_sets, ne=True)
    pm.exportSelected(path+'/Mesh/Ref/Mesh_'+name+'.ma', force=True)

    # Load and setup AS5 skeleton
    as5util.preBuild(figure, load=True)

    # Edit joint placement, if necessary

    # Remove shading face sets from namespaces so they don't get deleted
    for sel_set in pm.ls('Fac*', recursive=True):
        pm.rename(sel_set, sel_set.name().split(':')[1])
    # Delete geometry + namespaces
    for ns in 'HeadGeo', 'BodyGeo':
        pm.namespace(rm=ns, deleteNamespaceContent=True)

    # Reference geometry
    pm.createReference(path+'/Mesh/Ref/Mesh_'+name+'.ma', defaultNamespace=True)

    # Build AS5 rig
    pm.mel.eval(
        'source "C:/Users/DSY/Documents/Maya/scripts/AdvancedSkeleton5.mel";')
    pm.mel.eval('asBuildAdvancedSkeleton();')

    as5util.postBuild(figure)
    pm.mel.eval('asSetBuildPose("");')

    # Skin mesh and apply blendshapes
    applySkins()

    # Add to layers, cleanup
    layer = pm.ls('GeoLayer')[0] if pm.ls(
        'GeoLayer') else pm.createDisplayLayer(name='GeoLayer')
    layer.displayType.set(2)

    for grp in pm.ls(('Mesh', 'Morphs'), r=True):
        grp.setParent('Geometry')
        layer.addMembers(grp)

    pm.delete('Genesis8*')

    # Export skeleton
    pm.select('DeformationSystem', r=True)
    pm.exportSelected(path+'/Rig/Ref/SK_'+name+'.ma', force=True)
    # Export skinned mesh
    pm.select('Geometry', add=True)
    pm.exportSelected(path+'/Rig/Ref/SKIN_'+name+'.ma', force=True)
    # Save rig file
    pm.saveAs(path+'/Rig/Ref/Rig_'+name+'.ma')