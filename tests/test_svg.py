"""
Created on 2024-01-18

@author: wf
"""
import os
from typing import Tuple

from ngwidgets.basetest import Basetest

from dcm.svg import SVG, Arc, DonutSegment, SVGNodeConfig


class TestSVG(Basetest):
    """
    test svg module
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.tmp_directory = "/tmp/svg-module-test"
        os.makedirs(self.tmp_directory, exist_ok=True)
        self.write_results = True

    def save(self, svg: SVG, file_name: str):
        """
        save the given svg to the given filename
        """
        if self.write_results:
            svg_path = f"{self.tmp_directory}/{file_name}"
            svg.save(svg_path)

    def test_text_rotation(self):
        """
        Test the get_text_rotation method to ensure it returns the correct
        rotation angles for text in a circular chart. Text should be upright
        and readable regardless of its position on the chart.
        """
        # Define test cases as tuples of (input_angle, expected_output_angle)
        test_cases: Tuple[Tuple[float, float], ...] = (
            (45, 45),  # Top-right quadrant, no change
            (135, -45),  # Bottom-right quadrant, should rotate 180 degrees
            (225, 45),  # Bottom-left quadrant, should rotate 180 degrees
            (315, 315),  # Top-left quadrant, no change
        )
        svg = SVG()
        # Iterate through test cases and assert expected outcomes
        for input_angle, expected_output_angle in test_cases:
            adjusted_angle = svg.get_text_rotation(input_angle)
            self.assertAlmostEqual(
                adjusted_angle,
                expected_output_angle,
                places=1,
                msg=f"Failed for input angle: {input_angle}",
            )

    def test_multiline_text(self):
        """
        test mulitline handling
        """
        svg = SVG()
        # Add multiline text to the SVG
        multiline_text = "This is line 1.\nThis is line 2.\nThis is line 3."
        svg.add_text(x=100, y=100, text=multiline_text, fill="black")

        # Get the complete SVG markup
        svg_markup = svg.get_svg_markup()
        debug = self.debug
        if debug:
            print(svg_markup)
        self.save(svg, "multiline_svg_text.svg")

    def test_get_donut_path(self):
        """
        Test the get_donut_path method to ensure it returns the correct
        SVG path commands for the donut segment and the middle arc based on a DonutSegment.
        """
        # Create an SVG instance with default configuration
        svg = SVG()

        # Define a test DonutSegment
        test_segment = DonutSegment(
            cx=300.0,
            cy=300.0,
            inner_radius=100.0,
            outer_radius=150.0,
            start_angle=0.0,
            end_angle=180.0,
        )

        # Define the expected SVG path command for the test segment
        expected_path_commands = {
            False: (
                "M 400.0 300.0 "
                "L 450.0 300.0 "
                "A 150.0 150.0 0 1 1 150.0 300.0 "
                "L 200.0 300.0 "
                "A 100.0 100.0 0 1 0 400.0 300.0 Z"
            ),
            True: (
                "M 425.0 300.0 "  # Calculated start point (cx + r*cos(0), cy + r*sin(0))
                "A 125.0 125.0 0 1 1 175.0 300.0"  # Arc command
            ),
        }
        debug = self.debug
        # debug=True
        for middle_arc, expected_path_command in expected_path_commands.items():
            # Get the actual SVG path command from the method
            actual_path_command = svg.get_donut_path(
                test_segment, middle_arc=middle_arc
            )
            if debug:
                print(actual_path_command)
            # Check if the actual path command matches the expected one
            self.assertEqual(
                actual_path_command,
                expected_path_command,
                msg=f"Expected path command does not match the actual path command.",
            )

    def test_get_arc(self):
        """
        Test the get_arc method to ensure it calculates the correct coordinates and radius of an arc.
        """
        debug = self.debug
        debug = True
        # Create a DonutSegment instance
        segment = DonutSegment(
            start_angle=0,
            end_angle=90,
            inner_radius=50,
            outer_radius=100,
            cx=150,
            cy=150,
        )

        # Test cases with different radial offsets, adjusted for SVG context
        test_cases = {
            0.0: Arc(
                radius=50.0, start_x=200.0, start_y=150.0, end_x=150.0, end_y=200.0
            ),  # Inner arc
            0.5: Arc(
                radius=75.0, start_x=225.0, start_y=150.0, end_x=150.0, end_y=225.0
            ),  # Middle arc
            1.0: Arc(
                radius=100.0, start_x=250.0, start_y=150.0, end_x=150.0, end_y=250.0
            ),  # Outer arc
        }

        for offset, expected_arc in test_cases.items():
            actual_arc = segment.get_arc(radial_offset=offset)
            expected_arc.middle_x = actual_arc.middle_x
            expected_arc.middle_y = actual_arc.middle_y
            if debug:
                print(
                    f"Debug - Offset {offset}: Expected {expected_arc}, got {actual_arc}"
                )
            self.assertEqual(
                actual_arc, expected_arc, f"Failed for radial offset: {offset}"
            )

    def test_curved_text_on_donut_segment(self):
        """
        Test the placement of curved text on a donut segment.
        """
        for start_angle in [0, 90, 180, 270]:
            svg = SVG()
            segment = DonutSegment(
                cx=150,
                cy=150,
                inner_radius=50,
                outer_radius=100,
                start_angle=start_angle,
                end_angle=start_angle + 90,
            )

            # Add a donut segment to the SVG
            svg.add_donut_segment(
                SVGNodeConfig(
                    segment.cx,
                    y=segment.cy,
                    fill="#A0A0A0",
                ),
                segment,
            )

            # Add curved text to the donut segment
            curved_text = f"{start_angle}\nCurved\nText\n"
            svg.add_text_to_donut_segment(
                segment, curved_text, direction="curved", color="white"
            )

            # Save SVG to visually inspect the result
            svg_file_name = f"curved_text_on_donut_segment_{start_angle}.svg"
            self.save(svg, svg_file_name)

            # Optionally, print SVG markup for debugging
            debug = self.debug
            debug = True
            if debug:
                svg_markup = svg.get_svg_markup()
                print(svg_markup)
