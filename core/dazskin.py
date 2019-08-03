import pymel.core as pm
from .util import applyNgSkin, buildWtDrivers
from ..data import DRIVERS

SKIN_PATHS = {
    'g8f': {
        'Head': 'C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/data/G8F_HeadWeights_AS5.json',
        'Body': 'C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/data/G8F_BodyWeights_AS5.json'
    },
    'g8m': {
        'Head': 'C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/data/G8M_HeadWeights.json',
        'Body': 'C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/data/G8M_BodyWeights.json'
    },
    'g8fhi': {
        'Head': 'C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/data/G8F_HeadWeights_AS5.json',
        'Body': 'C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/data/G8F_BodyWeights_AS5.json'
    }
}


def applySkins(figure=None):
    figure = figure or getFigureName()
    for prefix, skin_path in SKIN_PATHS[figure].items():
        applySkin(prefix, skin_path)

    wtdrv_grp = pm.group([wtdrv.getParent() for wtdrv in pm.ls(
        '*', type='weightDriver')], name='WeightDrivers_GRP')
    pm.hide(wtdrv_grp)

    pm.importFile(
        'C:/Users/DSY/Documents/Maya/projects/_UE4-Chars/assets/G8_MATS.ma')


def applySkin(ns_prefix, skindata_path):
    mesh_name = '{}Geo:Mesh'.format(ns_prefix)

    # Bind skin
    pm.skinCluster('Root_M', mesh_name, skinMethod=1)

    # Load weights
    applyNgSkin(skindata_path, pm.ls(mesh_name)[0])

    # Add blendshapes
    shapes = pm.listRelatives(
        '{}Geo:Morphs'.format(ns_prefix)) + pm.ls(mesh_name)
    blend_shape = pm.blendShape(
        shapes, n='Morphs{}'.format(ns_prefix), foc=True)

    # Apply weight drivers
    buildWtDrivers(blend_shape, driver_data=DRIVERS)


def getFigureName():

    if pm.ls('TestesBase_M'):
        return 'g8m'

    if len(pm.ls('HeadGeo:Mesh')[0].vtx) > 7000:
        return 'g8fhi'

    return 'g8f'
