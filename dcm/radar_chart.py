'''
Created on 2024-02-05

@author: wf
'''
import math
from typing import List, Optional, Tuple
from dcm.svg import SVG, SVGNodeConfig, Polygon


class RadarChart:
    """
    a radar chart
    """
    
    def __init__(self,svg:SVG,max_score:float=100.0):
        self.svg=svg
        self.radius = self.svg.config.width / 2
        self.center_x = self.radius
        self.center_y = self.radius
        self.max_score=max_score
    
    def add_scale_circles(self, 
        num_circles: int = 10, 
        stroke_width: float = 1.0, 
        stroke_color: str = "black"):
        """
        Add concentric circles to the SVG based on the SVG's configuration.
        
        Args:
            num_circles (int): The number of concentric circles to draw.
            stroke_width (float): The stroke width of the circle lines.
            stroke_color (str): The color of the circle lines.
        """     
        for i in range(1, num_circles + 1):
            circle_radius = (self.radius * i) / num_circles
            self.svg.add_circle(
                SVGNodeConfig(
                    x=self.center_x,
                    y=self.center_y,
                    width=circle_radius,
                    stroke_width=stroke_width,
                    color=stroke_color,
                    fill="none"  # Ensure circles are not filled
                )
            )
    
    def calculate_radar_chart_points(self,
        scores: List[float]) -> List[Tuple[float, float]]:
        """
        Calculate the points for the radar chart based on the given scores.

        Args:
            scores (List[float]): The scores to be represented on the radar chart.

        Returns:
            List[Tuple[float, float]]: The list of points for the radar chart.
        """
        num_axes = len(scores)
        angle_per_axis = 2 * math.pi / num_axes  # Angle between each axis in radians

        points = []
        for i, score in enumerate(scores):
            angle = angle_per_axis * i  # Angle for this axis
            # Calculate the distance from the center for this point
            distance = (score / self.max_score) * self.radius
            x = self.center_x + distance * math.cos(angle)
            y = self.center_y + distance * math.sin(angle)
            points.append((x, y))

        return points
    
    def add_scores(self,
        scores: List[float],
        config: Optional[SVGNodeConfig] = None) -> None:
        """
        Add the scores to the radar chart as a polygon.

        Args:
            scores (List[float]): The scores to be represented on the radar chart.
            config (SVGNodeConfig, optional): The configuration for the polygon representing the scores.
        """    # Use the function to calculate points for the scores
        radar_points = self.calculate_radar_chart_points(
            scores
        )
        if config is None:
            config=SVGNodeConfig(
                color="blue",
                fill="none",
                stroke_width=2.0,
                opacity=0.5
            )

        # Create a Polygon for the radar chart
        radar_chart_polygon = Polygon(
            points=radar_points,
            fill=config.fill,
            stroke_width=config.stroke_width,
            color=config.color,
            opacity=config.opacity,
        )
        self.svg.add_polygon(radar_chart_polygon)
