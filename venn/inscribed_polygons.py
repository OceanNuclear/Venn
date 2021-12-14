"""Makes a Pseudo-Venn diagram:
Failed attempt at making a venn diagram using regular inscribed polygons.
Instead this became a side projects to generate artistic logos.
"""
from numpy import pi, sin, cos, array as ary, sqrt
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

    def plot(self, ax=None):
        import matplotlib.pyplot as plt
        if not ax:
            ax = plt.axes()
        polygons = self.polygon_coordinates()
        xcoords = ary([p[:,0] for p in polygons]).T
        ycoords = ary([p[:,1] for p in polygons]).T
        ax.set_aspect(1)
        ax.set_xticks([]), ax.set_yticks([])
        colours = plt.cm.rainbow(np.linspace(0, 1, self.N))
        lines = []
        for x, y, c in zip(xcoords.T, ycoords.T, colours):
            lines.append(ax.plot(x, y, color=c)[0])
        return ax, lines
        # return ax, ax.plot(xcoords, ycoords, )

class EqualizedVennDiagram(PolygonVennDiagram):
    def polygon_coordinates(self):
        if self.N <=2:
            return super().polygon_coordinates()
        else:
            # take N=4 as an example.
            # The outermost ring (ring[0]) has total area = F[0]**2=1, net area = 1-F[1]**2 which will be evenly shared among 5 regions.
            # ring[1] has total area = F[1]**2, net area = F[2]**2-F[1]**2 which will be evenly shared among 5 regions.
            # ring [3] has total area = F[3]**2 = net area, which will be evenly shared among 1 region.
            # total number of regions = N*(N-1) + 1
            area_of_each_region = 1/(self.N*(self.N-1)+1)
            scale_factor = [sqrt(area_of_each_region)]
            for n in range(self.N-1):
                scale_factor.append(sqrt(area_of_each_region*self.N + scale_factor[-1]**2))
            F = scale_factor[::-1]
            shape = _equidistribute_points_on_circle(self.N)
            offset_angle = pi/self.N

            layered_coordinates = []
            for layer in range(self.N):
                layered_coordinates.append(_rotate_and_scale(shape, offset_angle*layer, F[layer]))
            layered_coordinates = ary(layered_coordinates)

            sorted_to_components = []
            for component in range(self.N):
                indices = np.vstack([ary([[i, component] for i in range(self.N)]), ary([[self.N-1-i, (i+component+1)%self.N] for i in range(self.N)])])
                sorted_to_components.append(layered_coordinates[indices.T[0], indices.T[1]])
        return sorted_to_components

class RoundedVennDiagram(EqualizedVennDiagram):
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

    # ax, lines = EqualizedVennDiagram(18).plot()
    ax, lines = RoundedVennDiagram(9).plot()
    plt.show()
