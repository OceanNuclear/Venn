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
            # TODO: deal with this edge case
        elif self.N == 2:
            # return a rhombus, rotated 
            shape = ary([[0.5, 0], [0, 1], [-0.5, 0], [0, -1], [0.5, 0]])
            offset_angle, scale_factor = pi/2, 2
            # TODO: deal with this edge case
        else:
            shape = _equidistribute_points_on_circle(self.N)
            offset_angle, scale_factor = pi/self.N, cos(pi/self.N) # isoceles triangle with unique angle = tau/N and leg=1 has height = cos(pi/self.N)

            layered_coordinates = []
            for layer in range(self.N):
                layered_coordinates.append(_rotate_and_scale(shape, offset_angle*layer, scale_factor**layer))
            layered_coordinates = ary(layered_coordinates)

            sorted_to_components = []
            for component in range(self.N):
                indices = np.vstack([ary([[i, component] for i in range(self.N)]), ary([[self.N-1-i, (i+component+1)%self.N] for i in range(self.N)])])
                sorted_to_components.append(layered_coordinates[indices.T[0], indices.T[1]])
        return sorted_to_components
    # the increase in area between successive areas is 1/cos(pi/N)**2 -1.
    # I would prefer it if a different shape is chosen such that this is kept constant, i.e. independent of N.
    # Or better yet, the area of each region should be the same.

    def plot(self, ax=None):
        import matplotlib.pyplot as plt
        if not ax:
            ax = plt.axes()
        polygons = self.polygon_coordinates()
        xcoords = ary([p[:,0] for p in polygons]).T
        ycoords = ary([p[:,1] for p in polygons]).T
        ax.set_aspect(1)
        ax.set_xticks([]), ax.set_yticks([])
        return ax, ax.plot(xcoords, ycoords)

if __name__=="__main__":
    # coords = PolygonVennDiagram(5).polygon_coordinates()
    ax, lines = PolygonVennDiagram(16).plot()
    import matplotlib.pyplot as plt
    plt.show()