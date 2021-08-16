from shapely.ops import unary_union

class Dam:
    """
    Dam is the third level of classes forming a dam.
    A dam consists of one or more pillars which in turn consist of one or
    multiple segments.
    
    """
    
    def __init__(self, pillars):
        """
        Parameters
        ----------
        pillars : list
            List of instances of Pillar

        Returns
        -------
        None.

        """
        self.pillars = pillars
        
    def draw(self):
        """
        Returns
        -------
        shapely.geometry.polygon.Polygon
            Section through the entire dam along the cutting (shear) surface

        """
        return unary_union([p.cutting_surface() for p in self.pillars])