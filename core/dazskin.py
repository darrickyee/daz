import pymel.core as pm
from .util import applyNgSkin, buildWtDrivers
from ..data import DRIVERS

SKIN_PATHS = {
    'g8f': {
        'Head': 'C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/data/G8F_HeadWeights_AS5.json',
        'Body': 'C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/data/G8F_BodyWeights_AS5.json'
    },
    'g8m': {
        'Head': 'C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/data/G8M_HeadWeights.json',
        'Body': 'C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/data/G8M_BodyWeights.json'
    },
    'g8fhi': {
        'Head': 'C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/data/G8FHi_HeadWeights_AS5.json',
        'Body': 'C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/data/G8FHi_BodyWeights_AS5.json'
    }
}


def applySkins(figure=None):
    figure = figure or getFigureName()
    for ns_prefix, skin_path in SKIN_PATHS[figure].items():
        applySkin(ns_prefix, skin_path)
        bs_node = addBlendShapes(ns_prefix+'Geo')
        buildWtDrivers(bs_node, driver_data=DRIVERS)

    applyShaders()

    # Hide weightDrivers and group under appropriate group
    wtdrv_grp = pm.createNode('transform', n='WeightDriverSystem')
    for node in (wtdrv.getParent() for wtdrv in pm.ls('*', type='weightDriver')):
        node.setParent(wtdrv_grp)
    wtdrv_grp.visibility.set(False)
    if pm.ls('Main'):
        wtdrv_grp.setParent('Main')
    else:
        pm.group(wtdrv_grp, n='Main')


def applySkin(ns_prefix, skindata_path):
    mesh_name = '{}Geo:Mesh'.format(ns_prefix)

    # Bind skin
    pm.skinCluster('Root_M', mesh_name, skinMethod=1)

    # Load weights
    applyNgSkin(skindata_path, pm.ls(mesh_name)[0])


def applyShaders(shader_file='C:/Users/Darrick/Documents/Maya/projects/_UE4-Chars/assets/G8_MATS.ma'):

    if not pm.ls('MAT_Skin'):
        pm.importFile(shader_file)

    shader_map = {
        'MAT_Skin': pm.ls('Mesh', recursive=True),
        'MAT_Eyelash': pm.ls('FacEyelash', recursive=True)[0].members(),
        'MAT_EyeSurf': pm.ls('FacEyeSurf', recursive=True)[0].members()
    }

    for shader, faces in shader_map.items():
        pm.select(faces)
        pm.hyperShade(assign=shader)


def addBlendShapes(name_space):
    body_part = name_space.replace('Geo', '')
    if not pm.ls('Morphs'+body_part+'*', type='blendShape'):
        pm.select(pm.ls('{}:Morphs'.format(name_space))
                  [0].listRelatives(), r=True)
        pm.select('{}:Mesh'.format(name_space), add=True)
        return pm.blendShape(frontOfChain=1, n='Morphs{}'.format(
            name_space.replace('Geo', '')))[0]


def getFigureName():

    if pm.ls('TestesBase_M'):
        return 'g8m'

    if pm.ls('HeadGeo:Mesh'):
        if len(pm.ls('HeadGeo:Mesh')[0].vtx) > 7000:
            return 'g8fhi'

        return 'g8f'

    raise pm.MayaNodeError('No DAZ figure found.')
