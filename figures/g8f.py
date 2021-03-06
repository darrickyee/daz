from .abstract import FigureData


class FigureG8F(FigureData):

    def __init__(self, body_file, head_file):
        super(FigureG8F, self).__init__({'Body': body_file, 'Head': head_file})

    @property
    def name(self):
        return 'Genesis8Female'

    @property
    def mesh_names(self):
        return ['Genesis8Female',
                'Genesis8FemaleEyelashes']

    @property
    def uv_adjustments(self):
        return [{8: [(16286, 17003)]},
                {7: [(0, 251)]}]

    @property
    def del_face_list(self):
        return [[],
                [(252, 351)]]
