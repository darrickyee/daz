from .g8f import FigureG8F
from .g8m import FigureG8M


def getFigure(figure_type, body_file=None, head_file=None):

    figure_class = {
        'g8f': FigureG8F,
        'g8m': FigureG8M
    }

    return figure_class[figure_type.lower()](body_file, head_file)
