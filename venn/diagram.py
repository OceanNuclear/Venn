"""Makes a Venn diagram"""
from numpy import pi, sin, cos, array as ary
import numpy as np
tau = pi*2

__all__=["PolygonVennDiagram"]

def _rotate_and_scale(data, rotation_radian, scale):
    """Rotate and scale a list of 2D data.
    Parameters
    ----------
    data : bad data.
    rotation_radian : a scalar, denoting the anticlockwise rotation angle in radian.
    scale : scale factor of how much bigger the thingy needs to be. Identity transformation = 1.
    """
    rotation_matrix = ary([[cos(rotation_radian), -sin(rotation_radian)],
                            [sin(rotation_radian), cos(rotation_radian)]])
    scale_rotate = scale * rotation_matrix
    return (scale_rotate @ ary(data).T).T

def _equidistribute_points_on_circle(N):
    """Equally space out N some points on the unit circle.
    Make sure to duplicate the very last point for plotting purpose."""
    angles = np.arange(N+1)/N * tau
    return ary([cos(angles), sin(angles)]).T

class PolygonVennDiagram():
    """A Venn diagram with sharp edges"""
    def __init__(self, N):
        """Initialize a Venn diagram made from polygons"""
        self.N = N
        return

    def polygon_coordinates(self):
        """returns N lists of 2D coordinates"""
        if self.N == 1:
            # A single triangle
            shape = _equidistribute_points_on_circle(3)
            offset_angle, scale_factor = 0, 1
        elif self.N == 2:
            # return a rhombus, rotated 
            shape = ary([[0.5, 0], [0, 1], [-0.5, 0], [0, -1], [0.5, 0]])
            offset_angle, scale_factor = pi/2, 2
        else:
            shape = _equidistribute_points_on_circle(self.N)
            offset_angle, scale_factor = pi/self.N, 1/cos(pi/self.N) # isoceles triangle with unique angle = tau/N and leg=1 has height = cos(pi/self.N)

        coordinates = []
        for layer in range(self.N):
            coordinates.append(_rotate_and_scale(shape, offset_angle*layer, scale_factor**layer))
        return coordinates
    # the increase in area between successive areas is 1/cos(pi/N)**2 -1.
    # I would prefer it if a different shape is chosen such that this is kept constant, i.e. independent of N.

    def plot(self, ax=None):
        import matplotlib.pyplot as plt
        if not ax:
            ax = plt.axes()
        polygons = self.polygon_coordinates()
        xcoords = ary([p[:,0] for p in polygons]).T
        ycoords = ary([p[:,1] for p in polygons]).T
        return ax, ax.plot(xcoords, ycoords)

if __name__=="__main__":
    # coords = PolygonVennDiagram(5).polygon_coordinates()
    ax, lines = PolygonVennDiagram(5).plot()
    import matplotlib.pyplot as plt
    ax.set_aspect(1)
    plt.show()