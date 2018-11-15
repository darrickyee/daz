import pymel.core as pm
from .util import transferShapes


class TargetMesh(object):

    def __init__(self, src_mesh, tgt_name, tgt_file):
        self.src_mesh = src_mesh
        self.tgt_name = tgt_name
        self.tgt_file = tgt_file

        self.tgt_base = None
        self.tgt_new = None
        self.bs_node = None
        self.morph_list = None

    def transfer(self):
        self.importTarget()
        self.createTargetShape()
        self.createBlendShapes()
        self.transferBlendShapes()
        pm.delete(self.tgt_name + ':*')
        self.groupBlendShapes()
        self.tgt_new.rename(self.tgt_name + ':' + self.tgt_name)

    def importTarget(self):
        if not pm.ls(self.tgt_name):
            pm.importFile(self.tgt_file, namespace=self.tgt_name)

        self.tgt_base = pm.ls(self.tgt_name + ':' +
                              self.tgt_name, type='transform')[0]

    def createTargetShape(self):
        new_mesh = self.tgt_base.duplicate()[0]
        pm.transferAttributes(
            self.src_mesh, new_mesh, transferPositions=True, sampleSpace=3, targetUvSpace='UVOrig')
        pm.delete(new_mesh, ch=True)

        self.tgt_new = new_mesh

    def createBlendShapes(self):
        bs_node = pm.blendShape(self.tgt_new, self.tgt_base)[0]
        bs_node.setAttr(self.tgt_new.name(), 1.0, lock=True)

        morph_list = pm.ls(self.tgt_name + ':Morphs')[0].listRelatives()
        for morph in morph_list:
            bs_node.setTarget(
                (self.tgt_base, bs_node.numWeights(), morph, 1.0))

        self.bs_node = bs_node

    def transferBlendShapes(self):
        self.morph_list = transferShapes(
            self.bs_node, self.tgt_new, tgt_prefix='new' + self.tgt_name + '_')

    def groupBlendShapes(self):
        grp = pm.createNode('transform', n=self.tgt_name + ':Morphs')

        for mesh in self.morph_list:
            mesh.setParent(grp)
            mesh.rename(mesh.name().replace('new' + self.tgt_name + '_', ''))

        grp.setAttr('visibility', 0)
