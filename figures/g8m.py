from .abstract import FigureData


class FigureG8M(FigureData):

    def __init__(self, body_file, head_file):
        super(FigureG8M, self).__init__({'Body': body_file, 'Head': head_file})

    @property
    def name(self):
        return 'Genesis8Male'

    @property
    def mesh_names(self):
        return ['Genesis8Male',
                'Genesis8MaleEyelashes']

    @property
    def uv_adjustments(self):
        return [{8: [(16114, 17265)]},
                {7: [(0, 251)]}]

    @property
    def del_face_list(self):
        return [[],
                [(252, 351)]]
