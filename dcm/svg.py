from math import cos, sin, radians

class SVG:
    """
    SVG drawing class
    """
    def __init__(self, width=300, height=300, indent="  "):  # Default is two spaces
        self.width = width
        self.height = height
        self.elements = []
        self.indent = indent
        
    def get_svg_style(self):
        """
        Define styles for the SVG elements.
        """
        return (
            '<style>\n'
            '    .hoverable:hover { fill-opacity: 0.7; }\n'
            '</style>\n'
        )

    def _add_element(self, element,level:int=1):
        # Prepend the indent to the element according to its level
        indented_element = f'{self.indent * level}{element}\n'
        self.elements.append(indented_element)

    def add_circle(self, cx, cy, r, fill):
        circle = f'    <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />\n'
        self._add_element(circle)

    def add_rectangle(self, x, y, width, height, fill):
        rect = f'    <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}" />\n'
        self._add_element(rect)

    def add_group(self, content, group_id=None, group_class=None, level=1):
        # Create the attribute string for the group, if any attributes are present
        group_attrs = []
        if group_id:
            group_attrs.append(f'id="{group_id}"')
        if group_class:
            group_attrs.append(f'class="{group_class}"')
        attrs_str = " ".join(group_attrs)

        # We need to indent each line of the content
        indented_content = "\n".join(f"{self.indent * (level + 1)}{line}" for line in content.strip().split("\n"))

        # Assemble the group string with proper indentation for the opening and closing tags
        group_str = f"{self.indent * level}<g {attrs_str}>\n{indented_content}\n{self.indent * level}</g>\n"

        # Add the properly indented group to the SVG elements
        self._add_element(group_str, level=0)  # level=0 to avoid further indentation

    def add_pie_segment(self, cx, cy, radius, start_angle_deg, end_angle_deg, color, segment_name:str, segment_id=None, segment_class=None, segment_url=None):
        # Convert angles from degrees to radians for calculations
        start_angle_rad = radians(start_angle_deg)
        end_angle_rad = radians(end_angle_deg)

        # Calculate the start and end points
        start_x = cx + radius * cos(start_angle_rad)
        start_y = cy + radius * sin(start_angle_rad)
        end_x = cx + radius * cos(end_angle_rad)
        end_y = cy + radius * sin(end_angle_rad)

        # Determine if the arc should be drawn as a large-arc (values >= 180 degrees)
        large_arc_flag = '1' if end_angle_deg - start_angle_deg >= 180 else '0'

        # Create the path for the pie segment without indentation
        path_str = (
            f"M {cx} {cy} "
            f"L {start_x} {start_y} "
            f"A {radius} {radius} 0 {large_arc_flag} 1 {end_x} {end_y} "
            "Z"
        )
        
        # Assemble the path and title elements
        path_element = f'<path d="{path_str}" fill="{color}" />\n'
        title_element = f'<title>{segment_name}</title>'

        # Combine path and title into one string without adding indentation here
        group_content = f"{path_element}{title_element}"

        # If an URL is provided, wrap the content within an anchor
        if segment_url:
            group_content = f'<a xlink:href="{segment_url}" target="_blank">\n{group_content}</a>\n'

        # Use add_group to add the pie segment with proper indentation
        self.add_group(group_content, group_id=segment_id, group_class=segment_class, level=2)

    def add_donut_segment(self, cx, cy, inner_radius, outer_radius, start_angle_deg, end_angle_deg, color, segment_name:str, segment_id=None, segment_class="hoverable", segment_url=None):
        # Convert angles from degrees to radians for calculations
        start_angle_rad = radians(start_angle_deg)
        end_angle_rad = radians(end_angle_deg)
    
        # Calculate the start and end points for the outer radius
        start_x_outer = cx + outer_radius * cos(start_angle_rad)
        start_y_outer = cy + outer_radius * sin(start_angle_rad)
        end_x_outer = cx + outer_radius * cos(end_angle_rad)
        end_y_outer = cy + outer_radius * sin(end_angle_rad)
    
        # Calculate the start and end points for the inner radius
        start_x_inner = cx + inner_radius * cos(start_angle_rad)
        start_y_inner = cy + inner_radius * sin(start_angle_rad)
        end_x_inner = cx + inner_radius * cos(end_angle_rad)
        end_y_inner = cy + inner_radius * sin(end_angle_rad)
    
        # Determine if the arc should be drawn as a large-arc (values >= 180 degrees)
        large_arc_flag = '1' if end_angle_deg - start_angle_deg >= 180 else '0'
    
        # Create the path for the pie segment without indentation
        path_str = (
            f"M {start_x_inner} {start_y_inner} "  # Move to start of inner arc
            f"L {start_x_outer} {start_y_outer} "  # Line to start of outer arc
            f"A {outer_radius} {outer_radius} 0 {large_arc_flag} 1 {end_x_outer} {end_y_outer} "  # Outer arc
            f"L {end_x_inner} {end_y_inner} "  # Line to end of inner arc
            f"A {inner_radius} {inner_radius} 0 {large_arc_flag} 0 {start_x_inner} {start_y_inner} "  # Inner arc (reverse)
            "Z"
        )
    
        # Assemble the path and title elements
        path_element = f'<path d="{path_str}" fill="{color}" />\n'
        title_element = f'<title>{segment_name}</title>'
    
        # Combine path and title into one string without adding indentation here
        group_content = f"{path_element}{title_element}"
    
        # If an URL is provided, wrap the content within an anchor
        if segment_url:
            group_content = f'<a xlink:href="{segment_url}" target="_blank">\n{group_content}</a>\n'
    
        # Use add_group to add the pie segment with proper indentation
        self.add_group(group_content, group_id=segment_id, group_class=segment_class, level=2)

    def get_svg_markup(self):
        """
        Get the complete SVG markup with styles.
        """
        header = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.width}" height="{self.height}">\n'
        )
        styles = self.get_svg_style()  # Get the styles for the SVG
        body = "".join(self.elements)  # Combine all elements into one string
        footer = '</svg>'
        
        # Return the concatenated string
        return f"{header}{styles}{body}{footer}"

    def save(self, filename:str):
        """
        save my svg markup to the given filename
        """
        with open(filename, 'w') as file:
            file.write(self.get_svg_markup())
