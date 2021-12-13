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

def _spline_polygon_into_rounded_polygon(polygon, num_pts_between_vertex):
    """
    Parameters
    ----------
    polygon : a 2D array of polygon with N vertices, with shape (N+1, 2).
                Note that the start and end point are expected to be duplicated.
    num_pts_between_vertex : how many interpolated points to put between each vertex pair.
    Returns
    -------
    a 2D array of polygon verticies, with shape (N*num_pts_between_vertex+1, 2)
    """
    from scipy.interpolate import interp1d
    x_coords, y_coords = [], []

    for i, (p1, p2) in enumerate(zip(polygon[:-1], polygon[1:])):
        p0 = polygon[i-1] if (i-1)>=0 else polygon[-2] # if i==0, choose the PENULTIMATE point to skip over the duplicated point.
        p3 = polygon[i+2] if (i+2)<(len(polygon)-1) else polygon[(i+2+1)%len(polygon)]
        print(i, f"{p0=},\n{p1=},\n{p2=},\n{p3=}")
        line_smooth = interp1d([0,1,2,3], ary([p0, p1, p2, p3]).T, kind='cubic', )
        sample_locations = np.linspace(1, 2, num_pts_between_vertex)
        interpolated_coords = line_smooth(sample_locations) # get the interpolated coordinates

        x_coords.extend(interpolated_coords[0]), y_coords.extend(interpolated_coords[1])

    return ary([x_coords, y_coords]).T

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
            sorted_to_components = [_equidistribute_points_on_circle(3)]
        elif self.N == 2:
            # return a rhombus, rotated 
            sorted_to_components = [
            ary([[2,0], [0,1], [-0.5,0], [0,-1], [2,0]]),
            ary([[-2,0], [0,-1], [0.5,0], [0,1], [-2,0]])
            ]

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

class EqualizedVennDiagram():
    def polygon_coordinates(self):
        pass

class RoundedVennDiagram(PolygonVennDiagram):
    def __init__(self, N):
        super().__init__(N)

    def polygon_coordinates(self, num_pts_between_vertex=100):
        list_of_polygon_vertices = super().polygon_coordinates()
        new_coords = [_spline_polygon_into_rounded_polygon(coords, num_pts_between_vertex) for coords in list_of_polygon_vertices]
        return new_coords

if __name__=="__main__":
    import matplotlib.pyplot as plt

    # coords = PolygonVennDiagram(5).polygon_coordinates()
    # plt.plot(*coords[0][:].T)
    # plt.plot(*_spline_polygon_into_rounded_polygon(coords[0], 100).T)
    # plt.show()

    ax, lines = RoundedVennDiagram(5).plot()
    plt.show()
