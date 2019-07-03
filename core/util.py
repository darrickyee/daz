import pymel.core as pm
from ngSkinTools.importExport import JsonImporter


def alignJointToVector(joint, aim_x=(1, 0, 0), aim_y=(0, 1, 0)):
    """
    Rotates joint so that axes align with specified world-space directions.

    Parameters
    ----------
    joint : pm.nt.Transform
        Joint or transform to rotate.
    aim_x : tuple, optional
        World-space direction for the x-axis of `joint`.
    aim_y : tuple, optional
        World-space direction for the y-axis of `joint`.

    """

    aim_node = pm.createNode('transform')
    aim_loc = aim_loc = joint.getTranslation(
        space='world') + (t*10 for t in aim_x)
    aim_node.setTranslation(aim_loc, space='world')

    pm.delete(pm.aimConstraint(aim_node, joint, worldUpVector=aim_y), aim_node)


def getRootsInSet(joints):
    return [joint for joint in joints if joint.getParent() not in joints]


def getPoleVector(start, mid, end):
    """
    Returns a unit pole vector for `start`, `mid`, and `end` transforms.
    The pole vector is (parallel to) the vector orthogonal to the vector
    between `start` and `end` that passes through `mid`.
    (Note that `start` and `end` are interchangeable.)

    Parameters
    ----------
    start : pm.nodetypes.Transform

    mid : pm.nodetypes.Transform

    end : pm.nodetypes.Transform


    Returns
    -------
    pm.datatypes.Vector

    """

    locs = [xform.getTranslation(space='world') for xform in [start, mid, end]]
    vec_basen = (locs[2] - locs[0]).normal()
    vec_mid = (locs[1] - locs[0])
    pole_vec = (vec_mid - vec_mid.dot(vec_basen)*vec_basen).normal()

    return pole_vec


def orientJoint(joint, target, aim_vector=(1, 0, 0), up_vector=(0, 1, 0), world_up=(0, 1, 0)):
    pm.delete(pm.aimConstraint(target, joint, aimVector=aim_vector,
                               upVector=up_vector, worldUpVector=world_up))
    pm.makeIdentity(joint, apply=True)


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


def applyNgSkin(file_path, mesh):
    with open(file_path) as f:
        skin_str = ''.join(f.read().split())

    ngs_importer = JsonImporter()
    ngs_data = ngs_importer.process(skin_str)
    ngs_data.saveTo(mesh.name())


def createWtDriver(joint, target, rotation=(0, 0, 0), angle=None):

    joint = pm.ls(joint)[0]
    target = pm.ls(target)[0]

    angle = angle or sum(rot**2 for rot in rotation)**(1.0/2)
    invert = joint.name()[-2:] == '_L'

    wtdrv = pm.createNode('weightDriver')
    pm.rename(wtdrv.getParent(), 'wtDrv_{}1'.format(joint.name()))

    pm.delete(pm.parentConstraint(joint, wtdrv.getParent()))

    pm.rotate(wtdrv, rotation, os=True, r=True)

    pm.parentConstraint(joint.getParent(),
                        wtdrv.getParent(), mo=True)

    # Connect matrices
    wtdrv.getParent().worldMatrix[0].connect(wtdrv.readerMatrix)
    target.worldMatrix[0].connect(wtdrv.driverMatrix)

    # Set weightDriver attributes
    wtdrv.angle.set(angle)
    wtdrv.invert.set(invert)
    wtdrv.blendCurve[0].blendCurve_Interp.set(1)

    return wtdrv


def attachWtDriverMorph(wt_driver, morph_attr, keys=((0.0, 0.0), (1.0, 1.0))):

    wt_driver = pm.ls(wt_driver)[0]
    morph_attr = pm.ls(morph_attr)[0]

    rv_node = pm.createNode(
        'remapValue', name='drv_{}'.format(morph_attr.getAlias()))

    for i, key in enumerate(keys):
        rv_node.value[i].value_Position.set(key[0])
        rv_node.value[i].value_FloatValue.set(key[1])

    wt_driver.outWeight.connect(rv_node.inputValue)
    rv_node.outValue.connect(morph_attr)

    return rv_node


CHILD_JNTS = {
    'Jaw': 'JawEnd',
    'Neck': 'Head',
    'Clavicle': 'Shoulder',
    'Shoulder': 'Elbow',
    'Elbow': 'Wrist',
    'Hip': 'Knee',
    'Knee': 'Ankle'
}


def buildWtDrivers(blend_shape, driver_data):
    bs_node = pm.ls(blend_shape)[0]
    bs_morph_list = [alias[0] for alias in bs_node.listAliases()]
    wt_drv_list = list()

    for base_morph in driver_data:
        morphs = [
            morph for morph in bs_morph_list if morph.startswith(base_morph)]

        if morphs:
            driver_args = driver_data[base_morph]

            for morph in morphs:

                if pm.ls('wtDrv_{}'.format(morph)):
                    wt_drv = pm.ls('wtDrv_{}'.format(morph))[0].getShape()
                else:
                    side = morph[-2:] if morph[-2:] in ['_L', '_R'] else '_M'

                    joint = driver_args['joint']
                    target = CHILD_JNTS[joint] + side
                    rotation = driver_args.get('rotation', None)
                    angle = driver_args.get('angle', None)

                    wt_drv = createWtDriver(
                        joint+side, target, rotation, angle)
                    pm.rename(wt_drv.getParent(), 'wtDrv_{}'.format(morph))

                attachWtDriverMorph(wt_drv, '{0}.{1}'.format(
                    bs_node.name(), morph), driver_args.get('keys', ((0.0, 0.0), (1.0, 1.0))))

                wt_drv_list.append(wt_drv.getParent())

    return wt_drv_list


# def createWtDrivers(bs_node, morph_name, joint_base, rotation, radius=None, keys=((0.0, 0.0), (1.0, 1.0)), mirror=False, invert_axis=False):
#     bs_node = pm.ls(bs_node_name)[0]

#     radius = radius or sum(rot**2 for rot in rotation)**(1.0/2.0)

#     if mirror:
#         suffixes = ['_L', '_R']
#     else:
#         suffixes = ['_M']

#     for suf in suffixes:
#         m_suf = suf if mirror else ''
#         if bs_node.hasAttr(morph_name+m_suf):
#             morph = bs_node.attr(morph_name + m_suf)
#         else:
#             continue

#         joint = pm.ls(joint_base + suf)[0]
#         target = pm.ls(TARGET_MAP[joint_base]+suf)[0]

#         if suf == '_R':
#             inv = not invert_axis
#         else:
#             inv = invert_axis

#         wd_node = pm.createNode(
#             'weightDriver')
#         pm.rename(wd_node.getParent(), 'wtDrv_' + morph.getAlias())

#         pm.delete(pm.parentConstraint(joint, wd_node.getParent()))

#         pm.rotate(wd_node, rotation, os=True, r=True)

#         pm.parentConstraint(joint.getParent(),
#                             wd_node.getParent(), mo=True)

#         # Connect matrices
#         wd_node.getParent().worldMatrix[0].connect(wd_node.readerMatrix)
#         target.worldMatrix[0].connect(wd_node.driverMatrix)

#         # Set weightDriver attributes
#         wd_node.angle.set(radius)
#         wd_node.invert.set(inv)
#         wd_node.blendCurve[0].blendCurve_Interp.set(1)

#         # Create remapValue nodes and set keys
#         rv_node = pm.createNode(
#             'remapValue', name='drv_' + morph.getAlias())
#         for i, key in enumerate(keys):
#             rv_node.value[i].value_Position.set(key[0])
#             rv_node.value[i].value_FloatValue.set(key[1])

#         wd_node.outWeight.connect(rv_node.inputValue)
#         rv_node.outValue.connect(morph)
