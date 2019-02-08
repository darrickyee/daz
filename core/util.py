import pymel.core as pm


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
