from abc import ABCMeta, abstractproperty
import pymel.core as pm


class FigureData(object):
    __metaclass__ = ABCMeta

    def __init__(self, body_file=None, head_file=None):
        self.files = {'Body': body_file, 'Head': head_file}
        self._mesh = None

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def mesh_names(self):
        pass

    @abstractproperty
    def uv_adjustments(self):
        pass

    @abstractproperty
    def del_face_list(self):
        pass

    @property
    def mesh(self):
        return self._mesh

    def moveUVs(self):
        for i, mesh_name in enumerate(self.mesh_names):
            meshes = pm.ls([mesh_name+'_*', mesh_name+'FBX*'],
                           type='transform')

            for tile, face_ranges in self.uv_adjustments[i].items():
                face_sets = [mesh.f[face_range[0]: face_range[1]]
                             for mesh in meshes
                             for face_range in face_ranges]
                offsets = [tile - int(face_set.getUVs()[0][0])
                           for face_set in face_sets]
                for face_set, offset in zip(face_sets, offsets):
                    pm.polyEditUV(face_set, uValue=offset, relative=True)

    def deleteFaces(self):
        for i, mesh_name in enumerate(self.mesh_names):
            if self.del_face_list[i]:
                meshes = pm.ls([mesh_name+'_*', mesh_name+'FBX*'],
                               type='transform')
                faces = [mesh.f[face_range[0]:face_range[1]]
                         for mesh in meshes
                         for face_range in self.del_face_list[i]]
                pm.delete(faces)

    def mergeMeshes(self):
        self._mesh = pm.polyUnite(pm.ls(
            (mesh_name+'FBXASC046Shape' for mesh_name in self.mesh_names), type='transform'),
            n='Base', muv=1)[0]
        pm.delete(self.mesh, ch=True)

    def process(self):
        self.moveUVs()
        self.deleteFaces()
        self.mergeMeshes()
