"""
Created on 2024-01-18

@author: wf
"""
from typing import Tuple

from ngwidgets.basetest import Basetest

from dcm.svg import SVG


class TestSVG(Basetest):
    """
    test svg module
    """

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
