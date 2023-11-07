from math import pi, cos, sin

class SVG:
    """
    SVG drawing class
    """
    def __init__(self, width=300, height=300):
        self.width = width
        self.height = height
        self.elements = []

    def _add_element(self, element):
        self.elements.append(element)

    def add_circle(self, cx, cy, r, fill):
        circle = f'    <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />\n'
        self._add_element(circle)

    def add_rectangle(self, x, y, width, height, fill):
        rect = f'    <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}" />\n'
        self._add_element(rect)

    def add_pie_segment(self, cx, cy, r, start_angle, end_angle, fill):
        # Convert angles from degrees to radians
        start_angle_rad = pi / 180 * start_angle
        end_angle_rad = pi / 180 * end_angle

        # Calculate the points on the circle circumference
        x1 = cx + r * cos(start_angle_rad)
        y1 = cy + r * sin(start_angle_rad)
        x2 = cx + r * cos(end_angle_rad)
        y2 = cy + r * sin(end_angle_rad)

        large_arc_flag = 1 if end_angle - start_angle > 180 else 0

        # Create the path for the segment
        path_d = f'M {cx},{cy} L {x1},{y1} A {r},{r} 0 {large_arc_flag} 1 {x2},{y2} Z'
        segment = f'    <path d="{path_d}" fill="{fill}" />\n'
        self._add_element(segment)

    def get_svg_string(self):
        header = f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{self.width}" height="{self.height}">\n'
        footer = '</svg>'
        return header + "".join(self.elements) + footer

    def save(self, filename):
        with open(filename, 'w') as file:
            file.write(self.get_svg_string())


