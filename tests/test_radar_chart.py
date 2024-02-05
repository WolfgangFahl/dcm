"""
Created on 2024-02-01

@author: wf
"""
import os

from ngwidgets.basetest import Basetest

from dcm.radar_chart import RadarChart
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
        # Create an SVG instance 
        svg = SVG(SVGConfig(width=600, height=600))

        radar_chart = RadarChart(svg,max_score=100.0)
        radar_chart.add_scale_circles()
        radar_chart.add_scores(self.scores)
  
        # Save the SVG to a file or inspect the SVG markup
        svg_file_name = "radar_chart.svg"
        self.save(svg, svg_file_name)

        # Optionally, print the SVG markup for debugging
        if self.debug:
            svg_markup = svg.get_svg_markup()
            print(svg_markup)

        self.assertTrue("""<polygon points="600.0""" in svg_markup)
