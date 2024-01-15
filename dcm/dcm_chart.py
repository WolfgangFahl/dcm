"""
Created on 2024-01-12

@author: wf
"""
from dataclasses import dataclass
from typing import List, Optional

from dcm.dcm_core import (
    CompetenceElement,
    CompetenceFacet,
    CompetenceTree,
    DynamicCompetenceMap,
    Learner,
)
from dcm.svg import SVG, DonutSegment, SVGConfig


class DcmChart:
    """
    a Dynamic competence map chart
    """

    def __init__(self, dcm: DynamicCompetenceMap):
        """
        Constructor
        """
        self.dcm = dcm

    def generate_svg(
        self,
        filename: Optional[str] = None,
        learner: Optional[Learner] = None,
        config: Optional[SVGConfig] = None,
    ) -> str:
        """
        Generate the SVG markup and optionally save it to a file. If a filename is given, the method
        will also save the SVG to that file. The SVG is generated based on internal state not shown here.

        Args:
            filename (str, optional): The path to the file where the SVG should be saved. Defaults to None.
            learner(Learner): the learner to show the achievements for
            config (SVGConfig, optional): The configuration for the SVG canvas and legend. Defaults to default values.

        Returns:
            str: The SVG markup.
        """
        if config is None:
            config = SVGConfig()  # Use default configuration if none provided
        svg_markup = self.generate_svg_markup(
            self.dcm.competence_tree, learner=learner, config=config
        )
        if filename:
            self.save_svg_to_file(svg_markup, filename)
        return svg_markup

    def generate_donut_segment_for_element(
        self,
        svg: SVG,
        element: CompetenceElement,
        learner: Learner,
        segment: DonutSegment,
    ):
        """
        generate a donut segment for a given element of
        the CompetenceTree
        """
        # Add the element segment as a donut segment
        element_url = (
            element.url
            if element.url
            else f"{self.lookup_url}/description/{element.path}"
            if self.lookup_url is not None
            else None
        )
        show_as_popup = element.url is None
        element_config = element.to_svg_node_config(
            url=element_url,
            show_as_popup=show_as_popup,
            x=self.cx,
            y=self.cy,
        )
        # check learner achievements
        if learner:
            achievement = learner.achievements_by_path.get(element.path, None)
            if achievement and achievement.level:
                element_config.element_class = "selected"
        svg.add_donut_segment(config=element_config, segment=segment)

    def generate_pie_elements(
        self,
        level: int,
        svg: SVG,
        parent_element: CompetenceElement,
        learner: Learner,
        segment: DonutSegment,
    ):
        """
        generate the pie elements (donut segments) for the subelements
        of the given parent_element at the given level
        e.g. aspects, areas or facets - taking the learner
        achievements into account if a corresponding achievement
        is found. The segment limits the area in which the generation may operate
        """
        sub_element_name = self.levels[level]
        # get the elements to be displayed
        elements = getattr(parent_element, sub_element_name)
        total = len(elements)
        # are there any elements to be shown?
        if total > 0:
            angle_per_element = (segment.end_angle - segment.start_angle) / total
            start_angle = segment.start_angle
            for element in elements:
                end_angle = start_angle + angle_per_element
                sub_segment = DonutSegment(
                    segment.outer_radius,
                    segment.outer_radius + self.tree_radius*2,
                    start_angle,
                    end_angle,
                )
                self.generate_donut_segment_for_element(
                    svg, element, learner, segment=sub_segment
                )
                start_angle = end_angle
                if level + 1 < len(self.levels):
                    self.generate_pie_elements(
                        level=level + 1,
                        svg=svg,
                        parent_element=element,
                        learner=learner,
                        segment=sub_segment,
                    )

    def generate_svg_markup(
        self,
        competence_tree: CompetenceTree = None,
        learner: Learner = None,
        config: SVGConfig = None,
        with_java_script: bool = True,
        lookup_url: str = "",
    ) -> str:
        """
        generate the SVG markup for the given CompetenceTree and learner

        Args:

        """
        if competence_tree is None:
            competence_tree = self.dcm.competence_tree

        svg = SVG(config)
        self.svg = svg
        config = svg.config
        # center of circle
        self.cx = config.width // 2
        self.cy = (config.total_height - config.legend_height) // 2
        self.levels = ["aspects", "areas", "facets"]
        self.tree_radius = config.width / 2 / 8

        self.lookup_url = (
            competence_tree.lookup_url if competence_tree.lookup_url else lookup_url
        )

        circle_config = competence_tree.to_svg_node_config(
            x=self.cx, 
            y=self.cy, 
            width=self.tree_radius
        )
        svg.add_circle(config=circle_config)

        segment = DonutSegment(
            inner_radius=0, 
            outer_radius=self.tree_radius
        )
        self.generate_pie_elements(
            level=0,
            svg=svg,
            parent_element=competence_tree,
            learner=learner,
            segment=segment,
        )
        if config.legend_height > 0:
            competence_tree.add_legend(svg)

        return svg.get_svg_markup(with_java_script=with_java_script)

    def save_svg_to_file(self, svg_markup: str, filename: str):
        """
        Save the SVG content to a file
        """
        with open(filename, "w") as file:
            file.write(svg_markup)
