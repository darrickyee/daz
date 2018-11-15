import pymel.core as pm


class G8Mesh(object):

    def __init__(self, mesh_name, uvadj_dict=None, del_list=None):
        self._mesh = pm.ls(mesh_name)[0]
        self.processed = False

        # {Tile:(start_index, end_index)} for UV adjustment faces
        self.uvadj_dict = uvadj_dict

        # List of (start_index, end_index) tuples for faces to be deleted
        self.del_list = del_list

    @property
    def mesh(self):
        return self._mesh

    def moveUVs(self):
        for tile in self.uvadj_dict:
            face_sets = [self.mesh.f[face_range[0]: face_range[1]]
                         for face_range in self.uvadj_dict[tile]]
            offsets = [tile - int(face_set.getUVs()[0][0])
                       for face_set in face_sets]
            for face_set, offset in zip(face_sets, offsets):
                pm.polyEditUV(face_set, uValue=offset, relative=True)

    def processMesh(self):
        if not self.processed:

            pm.delete(self.mesh, ch=True)
            self.mesh.setParent(world=True)

            for face_range in self.del_list:
                pm.delete(self.mesh.f[face_range[0]: face_range[1]])

            self.moveUVs()

            self.processed = True
