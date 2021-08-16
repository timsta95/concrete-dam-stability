class Segment: 
    """
    Segment is the lowest level of classes that describe a dam geometry.
    One or more segments form a pillar (also for gravity dams),
    one or more pillars form a dam.
    
    """
    
    def __init__ (self, poly, width, spec_weight, axis, name):   
        """
        Parameters
        ----------
        poly : shapely.geometry.polygon.Polygon
            2D polygon (on the xz-plane) depicting the segment profile,
            length unit: m
        width : positive float
            segment width,
            unit: m
        spec_weight : positive float
            specific weight of the building material,
            unit: kN/m3
        axis : float
            position of the segments center line on the y-axis,
            length unit: m
        name : string
            Name of the segment, e.g. 'pillar', 'buttress', ...

        Returns
        -------
        None. 
        
        """
        self.poly = poly
        self.width = width
        self.spec_weight = spec_weight
        self.axis = axis
        self.name = name
     
    def centroid(self):  
        """
        Returns
        -------
        shapely.geometry.point.Point
            Centroid/ load-carrying point (xz-plane) of the segment,
            length unit: m
            
        """
        return self.poly.centroid
    
    def area(self):       
        """
        Returns
        -------
        positive float
            Segment profile area,
            unit: m2
            
        """
        return self.poly.area
    
    def load(self):     
        """
        Returns
        -------
        positive float
            Segment load,
            unit: kN
            
        """
        return self.poly.area * self.width * self.spec_weight