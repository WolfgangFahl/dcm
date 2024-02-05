"""
Created on 2024-02-01

@author: wf
"""
import os

from ngwidgets.basetest import Basetest

from dcm.dcm_chart import DcmChart
from dcm.svg import SVG, Polygon, SVGConfig, SVGNodeConfig


class TestDcmChart(Basetest):
    """
    test dcm
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.tmp_directory = "/tmp/svg-module-test"
        os.makedirs(self.tmp_directory, exist_ok=True)
        self.write_results = True
        self.scores = [
            100.0,
            100.0,
            100.0,
            100.0,
            67.0,
            0.0,
            66.5,
            100.0,
            43.7,
            85.75,
            77.83,
            100.0,
            100.0,
            58.25,
            100.0,
            100.0,
            80.0,
            25.0,
            77.83,
            66.67,
            60.0,
            60.0,
            50.0,
            77.67,
        ]

    def save(self, svg: SVG, file_name: str):
        """
        save the given svg to the given filename
        """
        if self.write_results:
            svg_path = f"{self.tmp_directory}/{file_name}"
            svg.save(svg_path)

    def test_radar_chart(self):
        """
        test radar chart creation
        """
        dcm_chart = DcmChart(None)
        # Define the center and radius for the radar chart
        center = (300, 300)  # Adjust as needed
        radius = 200  # Adjust as needed

        # Use the function to calculate points for the scores
        radar_points = dcm_chart.calculate_radar_chart_points(
            self.scores, max_score=100.0, center=center, radius=radius
        )

        # Create a Polygon for the radar chart
        radar_chart_polygon = Polygon(
            points=radar_points,
            fill="none",
            stroke_width=2.0,
            color="blue",
            opacity=0.5,
        )

        # Create an SVG instance and add the radar chart Polygon
        svg = SVG(SVGConfig(width=600, height=600))

        # Add concentric circles at every 10% interval
        for i in range(1, 11):
            circle_radius = (radius * i) / 10
            svg.add_circle(
                SVGNodeConfig(
                    x=center[0],
                    y=center[1],
                    width=circle_radius,
                    fill="none",
                    stroke_width=1.0,
                    color="black",
                )
            )
        svg.add_polygon(radar_chart_polygon)

        # Save the SVG to a file or inspect the SVG markup
        svg_file_name = "radar_chart.svg"
        self.save(svg, svg_file_name)

        # Optionally, print the SVG markup for debugging
        if self.debug:
            svg_markup = svg.get_svg_markup()
            print(svg_markup)

        self.assertTrue("""<polygon points="500.0""" in svg_markup)
