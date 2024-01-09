import html
from math import cos, radians, sin
from typing import List, Optional, Tuple

from pydantic.dataclasses import dataclass


@dataclass
class SVGConfig:
    """
    Configuration class for SVG generation.

    Attributes:
        width (int): Width of the SVG canvas in pixels.
        height (int): Height of the SVG canvas in pixels.
        legend_height (int): Height reserved for the legend in pixels.
        font (str): Font family for text elements.
        font_size (int): Font size in points for text elements.
        indent (str): Indentation string, default is two spaces.
        default_color (str): Default color code for SVG elements.
    """

    width: int = 600
    height: int = 600
    legend_height: int = 150
    font: str = "Arial"
    font_size: int = 12
    indent: str = "  "
    default_color: str = "#C0C0C0"

    @property
    def total_height(self) -> int:
        """
        Calculate total height of the SVG canvas including the legend.

        Returns:
            int: Total height of the SVG canvas.
        """
        return self.height + self.legend_height


@dataclass
class SVGNodeConfig:
    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None
    fill: Optional[str] = "black"
    indent_level: int = 1
    element_type: Optional[str] = None
    id: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    show_as_popup: bool = False  # Flag to indicate if the link should opened as a popup
    comment: Optional[str] = None
    element_class: Optional[str] = "hoverable"


class SVG:
    """
    Class for creating SVG drawings.

    Attributes:
        config (SVGConfig): Configuration for the SVG drawing.
    """

    def __init__(self, config: SVGConfig = None):
        """
        Initialize SVG object with given configuration.

        Args:
            config (SVGConfig): Configuration for SVG generation.
        """
        self.config = config if config else SVGConfig()
        self.width = self.config.width
        self.height = self.config.height
        self.elements = []
        self.indent = self.config.indent

    def get_svg_style(self) -> str:
        """
        Define styles for SVG elements.

        Returns:
            str: String containing style definitions for SVG.
        """
        return (
            f"{self.indent}<style>\n"
            f"{self.indent * 2}.hoverable {{ cursor: pointer; fill-opacity: 1; stroke: black; stroke-width: 0.5; }}\n"
            f"{self.indent * 2}.hoverable:hover {{ fill-opacity: 0.7; }}\n"
            f"{self.indent * 2}.popup {{\n"
            f"{self.indent * 3}border: 2px solid black;\n"
            f"{self.indent * 3}border-radius: 15px;\n"
            f"{self.indent * 3}overflow: auto;\n"  # changed to 'auto' to allow scrolling only if needed
            f"{self.indent * 3}background: white;\n"
            f"{self.indent * 3}box-sizing: border-box;\n"  # ensures padding and border are included
            f"{self.indent * 3}padding: 10px;\n"  # optional padding inside the popup
            f"{self.indent * 3}height: 100%;\n"  # adjusts height relative to foreignObject
            f"{self.indent * 3}width: 100%;\n"  # adjusts width relative to foreignObject
            f"{self.indent * 2}}}\n"
            f"{self.indent * 2}.close-btn {{\n"  # style for the close button
            f"{self.indent * 3}cursor: pointer;\n"
            f"{self.indent * 3}position: absolute;\n"
            f"{self.indent * 3}top: 0;\n"
            f"{self.indent * 3}right: 0;\n"
            f"{self.indent * 3}padding: 5px;\n"
            f"{self.indent * 3}font-size: 20px;\n"
            f"{self.indent * 3}user-select: none;\n"  # prevents text selection on click
            f"{self.indent * 2}}}\n"
            f"{self.indent}</style>\n"
        )

    def get_text_width(self, text: str) -> int:
        """
        Estimate the width of a text string in the SVG based on the font size and font name.

        Args:
            text (str): The text content.

        Returns:
            int: The estimated width of the text in pixels.
        """
        average_char_width_factor = 0.6
        average_char_width = average_char_width_factor * self.config.font_size
        return int(average_char_width * len(text))

    def add_element(self, element: str, level: int = 1, comment: str = None):
        """
        Add an SVG element to the elements list with proper indentation.

        Args:
            element (str): SVG element to be added.
            level (int): Indentation level for the element.
            comment(str): optional comment to add
        """
        base_indent = f"{self.indent * level}"
        if comment:
            indented_comment = f"{base_indent}<!-- {comment} -->\n"
            self.elements.append(indented_comment)
        indented_element = f"{base_indent}{element}\n"
        self.elements.append(indented_element)

    def add_circle(self, config: SVGNodeConfig):
        """
        Add a circle element to the SVG, optionally making it clickable and with a hover effect.

        Args:
            config (SVGNodeConfig): Configuration for the circle element.
        """
        color = config.fill if config.fill else self.config.default_color
        circle_element = f'<circle cx="{config.x}" cy="{config.y}" r="{config.width}" fill="{color}" class="{config.element_class}" />'

        # If URL is provided, wrap the circle in an anchor tag to make it clickable
        if config.url:
            circle_indent = self.indent * (config.indent_level + 1)
            circle_element = f"""<a xlink:href="{config.url}" target="_blank">
{circle_indent}{circle_element}
</a>"""

        # Use add_group to add the circle element with proper indentation
        self.add_group(
            circle_element,
            group_id=config.id,
            group_class=config.element_class,
            level=config.indent_level,
            comment=config.comment,
        )

    def add_rectangle(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        fill: str = None,
        indent_level: int = 1,
    ):
        """
        Add a rectangle element to the SVG.

        Args:
            x (int): X-coordinate of the rectangle's top-left corner.
            y (int): Y-coordinate of the rectangle's top-left corner.
            width (int): Width of the rectangle.
            height (int): Height of the rectangle.
            fill (str, optional): Fill color of the rectangle. Defaults to the default color.
            indent_level (int): Indentation level for the rectangle.
        """
        color = fill if fill else self.config.default_color
        rect = f'{self.indent * 3}<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{color}" />\n'
        self.add_element(rect)

    def add_legend_column(
        self,
        items: List[Tuple[str, str]],
        title: str,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """
        Add a legend column to the SVG.

        Args:
            items (List[Tuple[str, str]]): List of tuples with color code and label.
            title (str): Title of the legend.
            x (int): X position of the legend.
            y (int): Y position of the legend.
            width (int): Width of the color box in the legend.
            height (int): Height of each legend item.
        """
        self.add_text(x, y - height, title, font_weight="bold")
        for index, (color, label) in enumerate(items):
            self.add_rectangle(x, y + index * (height + 5), width, height, color)
            self.add_text(x + width + 10, y + index * (height + 5) + height / 2, label)

    def add_text(
        self,
        x: int,
        y: int,
        text: str,
        fill: str = "black",
        font_weight: str = "normal",
        text_anchor: str = "start",
    ) -> None:
        """
        Add text to the SVG.

        Args:
            x (int): X position of the text.
            y (int): Y position of the text.
            text (str): Text content.
            fill (str, optional): Fill color of the text. Defaults to "black".
            font_weight (str, optional): Font weight (normal, bold, etc.). Defaults to "normal".
            text_anchor (str, optional): Text alignment (start, middle, end). Defaults to "start".
        """
        escaped_text = html.escape(text)
        text_element = (
            f'<text x="{x}" y="{y}" fill="{fill}" '
            f'font-family="{self.config.font}" '
            f'font-size="{self.config.font_size}" '
            f'font-weight="{font_weight}" '
            f'text-anchor="{text_anchor}">'
            f"{escaped_text}</text>\n"
        )
        self.add_element(text_element)

    def add_group(
        self,
        content: str,
        group_id: str = None,
        group_class: str = None,
        level: int = 1,
        comment: str = None,
    ):
        """
        Add a group of elements to the SVG.

        Args:
            content (str): SVG content to be grouped.
            group_id (str, optional): ID for the group.
            group_class (str, optional): Class for the group.
            level (int): Indentation level for the group.
        """
        group_attrs = []
        if group_id:
            group_attrs.append(f'id="{group_id}"')
        if group_class:
            group_attrs.append(f'class="{group_class}"')
        attrs_str = " ".join(group_attrs)
        indented_content = "\n".join(
            f"{self.indent * (level + 1)}{line}" for line in content.strip().split("\n")
        )
        group_str = f"{self.indent * level}<g {attrs_str}>\n{indented_content}\n{self.indent * level}</g>\n"
        self.add_element(group_str, level=level, comment=comment)

    def add_pie_segment(
        self,
        cx: int,
        cy: int,
        radius: int,
        start_angle_deg: float,
        end_angle_deg: float,
        color: str,
        segment_name: str,
        segment_id: str = None,
        segment_class: str = None,
        segment_url: str = None,
    ) -> None:
        """
        Add a pie segment to the SVG.

        Args:
            cx (int): X-coordinate of the center of the pie.
            cy (int): Y-coordinate of the center of the pie.
            radius (int): Radius of the pie.
            start_angle_deg (float): Start angle of the segment in degrees.
            end_angle_deg (float): End angle of the segment in degrees.
            color (str): Fill color of the segment.
            segment_name (str): Name of the segment, used for the tooltip.
            segment_id (str, optional): ID for the segment group. Defaults to None.
            segment_class (str, optional): Class for the segment group. Defaults to None.
            segment_url (str, optional): URL linked to the segment. Defaults to None.

        Returns:
            None
        """
        if color is None:
            color = self.config.default_color
        # Convert angles from degrees to radians for calculations
        start_angle_rad = radians(start_angle_deg)
        end_angle_rad = radians(end_angle_deg)

        # Calculate the start and end points
        start_x = cx + radius * cos(start_angle_rad)
        start_y = cy + radius * sin(start_angle_rad)
        end_x = cx + radius * cos(end_angle_rad)
        end_y = cy + radius * sin(end_angle_rad)

        # Determine if the arc should be drawn as a large-arc (values >= 180 degrees)
        large_arc_flag = "1" if end_angle_deg - start_angle_deg >= 180 else "0"

        # Create the path for the pie segment without indentation
        path_str = (
            f"M {cx} {cy} "
            f"L {start_x} {start_y} "
            f"A {radius} {radius} 0 {large_arc_flag} 1 {end_x} {end_y} "
            "Z"
        )

        # Assemble the path and title elements
        path_element = f'<path d="{path_str}" fill="{color}" />\n'
        escaped_title = html.escape(segment_name)  # Escape special characters

        title_element = f"<title>{escaped_title}</title>"

        # Combine path and title into one string without adding indentation here
        group_content = f"{path_element}{title_element}"

        # If an URL is provided, wrap the content within an anchor
        if segment_url:
            group_content = (
                f'<a xlink:href="{segment_url}" target="_blank">\n{group_content}</a>\n'
            )

        # Use add_group to add the pie segment with proper indentation
        self.add_group(
            group_content, group_id=segment_id, group_class=segment_class, level=2
        )

    def add_donut_segment(
        self, config: SVGNodeConfig, start_angle_deg: float, end_angle_deg: float
    ) -> None:
        """
        Add a donut segment to the SVG.

        Args:
            config (SVGNodeConfig): Configuration for the donut segment.
            start_angle_deg (float): Start angle of the segment in degrees.
            end_angle_deg (float): End angle of the segment in degrees.
        """
        cx, cy = config.x, config.y
        inner_radius, outer_radius = config.width, config.height
        color = config.fill if config.fill else self.config.default_color

        if color is None:
            color = self.config.default_color
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
        large_arc_flag = "1" if end_angle_deg - start_angle_deg >= 180 else "0"

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
        escaped_title = html.escape(config.title)  # Escape special characters

        title_element = f"<title>{escaped_title}</title>"

        # Combine path and title into one string without adding indentation here
        group_content = f"{path_element}{title_element}"

        # Check if the segment should be shown as a popup
        if config.show_as_popup:
            # Add JavaScript to handle popup logic
            onclick_action = f"onclick=\"showPopup('{config.url}', evt)\""
            group_content = f"<g {onclick_action}>{group_content}</g>"
        elif config.url:
            # Regular link behavior
            group_content = (
                f'<a xlink:href="{config.url}" target="_blank">{group_content}</a>'
            )

        # Use add_group to add the pie segment with proper indentation
        self.add_group(
            group_content,
            group_id=config.id,
            group_class=config.element_class,
            level=2,
            comment=config.comment,
        )

    def get_java_script(self) -> str:
        popup_script = """
    <script>
         function showPopup(url, evt) {
            var popup = document.getElementById('dcm-svg-popup');
            var iframe = document.getElementById('popup-iframe');
            var svgRect = evt.target.getBoundingClientRect();
            var svg = document.querySelector('svg');
            var svgPoint = svg.createSVGPoint();
            svgPoint.x = evt.clientX - svgRect.left;
            svgPoint.y = evt.clientY - svgRect.top;
        
            // Position the popup near the click event
            popup.setAttribute('x', svgPoint.x);
            popup.setAttribute('y', svgPoint.y);
            // Set the iframe src and make the popup visible
            iframe.setAttribute('src', url);
            popup.setAttribute('visibility', 'visible');
        }
        
        function closePopup() {
            var popup = document.getElementById('dcm-svg-popup');
            popup.setAttribute('visibility', 'hidden');
        }
    </script>
    """
        return popup_script

    def get_svg_markup(self, with_java_script: bool = True) -> str:
        """
        Generate the complete SVG markup.

        Args:
            with_java_script(bool): if True(default) the javascript code is included otherwise
            it's available via the get_java_script function

        Returns:
            str: String containing the complete SVG markup.
        """
        header = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.width}" height="{self.config.total_height}">\n'
        )
        popup = """
        <!-- Add a foreignObject for the popup -->
<foreignObject id="dcm-svg-popup" class="popup" width="500" height="354" x="150" y="260" visibility="hidden">
    <body xmlns="http://www.w3.org/1999/xhtml">
        <!-- Content of your popup goes here -->
        <div class="popup" style="background-color: white; border: 1px solid black; padding: 10px; box-sizing: border-box; width: 500px; height: 354px; position: relative;">
            <span onclick="closePopup()" class="close-btn">ⓧ</span>
            <iframe id="popup-iframe" width="100%" height="100%" frameborder="0"></iframe>
        </div>
    </body>
</foreignObject>
"""

        styles = self.get_svg_style()
        body = "".join(self.elements)
        footer = "</svg>"
        java_script = self.get_java_script() if with_java_script else ""
        svg_markup = f"{header}{java_script}{styles}{body}{popup}{footer}"
        return svg_markup

    def save(self, filename: str):
        """
        Save the SVG markup to a file.

        Args:
            filename (str): Filename to save the SVG markup.
        """
        with open(filename, "w") as file:
            file.write(self.get_svg_markup())
