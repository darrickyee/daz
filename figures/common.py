from abc import ABCMeta, abstractproperty


class FigureData(object):
    __metaclass__ = ABCMeta

    def __init__(self, body_file=None, head_file=None):
        self.body_file = body_file
        self.head_file = head_file

    @abstractproperty
    def mesh_names(self):
        pass

    @abstractproperty
    def uv_adjustments(self):
        pass

    @abstractproperty
    def del_face_list(self):
        pass
