"""
Created on 2024-01-12

@author: wf
"""
from typing import List, Optional
import copy

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
    
    def add_donut_segment(self, 
            svg: SVG, 
            element: CompetenceElement, 
            segment: DonutSegment, 
            level_color=None, 
            achievement_level=None
        )->DonutSegment:
        """
        create a donut segment for the 
        given competence element and add it to the given SVG
        """
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
    
        if level_color:
            element_config.fill = level_color  # Set the color
        if element.path in self.selected_paths:
            element_config.element_class = "selected"
            
        if achievement_level is not None:
            total_levels = self.dcm.competence_tree.total_valid_levels
            relative_radius = (segment.outer_radius - segment.inner_radius) * (achievement_level / total_levels)
            segment.outer_radius = segment.inner_radius + relative_radius
    
        result=svg.add_donut_segment(config=element_config, segment=segment)
        return result
    
    def generate_donut_segment_for_achievement(
        self,
        svg: SVG,
        learner: Learner,
        element: CompetenceElement,
        segment: DonutSegment,
    )->DonutSegment:
        """
        generate a donut segment for the 
        learner's achievements
        corresponding to the given path and return it's segment definition
        """
        achievement = learner.achievements_by_path.get(element.path, None)
        result=None
        if achievement and achievement.level:
            # Retrieve the color for the achievement level
            level_color = self.dcm.competence_tree.get_level_color(achievement.level)
    
            if level_color:
                # set the color and radius of 
                # the segment for achievement
                # make sure we don't interfere with the segment calculations
                segment=copy.deepcopy(segment)
                result=self.add_donut_segment(svg, element, segment, level_color, achievement.level)
        return result    

    def generate_donut_segment_for_element(
        self,
        svg: SVG,
        element: CompetenceElement,
        learner: Learner,
        segment: DonutSegment,
    )->DonutSegment:
        """
        generate a donut segment for a given element of
        the CompetenceTree
        """
        # Simply create the donut segment without considering the achievement
        result=self.add_donut_segment(
            svg=svg, 
            element=element,
            segment=segment
        )
        # check learner achievements
        if learner:
            _learner_segment=self.generate_donut_segment_for_achievement(
                svg=svg,
                learner=learner,
                element=element,
                segment=segment
            )
        return result   
     
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
                    svg, 
                    element, 
                    learner, 
                    segment=sub_segment
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
        selected_paths: List=[],
        config: SVGConfig = None,
        with_java_script: bool = True,
        lookup_url: str = "",
    ) -> str:
        """
    Generate the SVG markup for the given CompetenceTree and Learner. This method 
    creates an SVG representation of the competence map, which visualizes the 
    structure and levels of competencies, along with highlighting the learner's 
    achievements if provided.

    Args:
        competence_tree (CompetenceTree, optional): The competence tree structure 
            to be visualized. If None, the competence tree of the DcmChart instance 
            will be used. Defaults to None.
        learner (Learner, optional): The learner whose achievements are to be 
            visualized on the competence tree. If None, no learner-specific 
            information will be included in the SVG. Defaults to None.
        selected_paths (List, optional): A list of paths that should be highlighted 
            in the SVG. These paths typically represent specific competencies or 
            achievements. Defaults to an empty list.
        config (SVGConfig, optional): Configuration for the SVG canvas and legend. 
            If None, default configuration settings are used. Defaults to None.
        with_java_script (bool, optional): Indicates whether to include JavaScript 
            in the SVG for interactivity. Defaults to True.
        lookup_url (str, optional): Base URL for linking to detailed descriptions 
            or information about the competence elements. If not provided, links 
            will not be generated. Defaults to an empty string.

    Returns:
        str: A string containing the SVG markup for the competence map.

    Raises:
        ValueError: If there are inconsistencies or issues with the provided data
            that prevent the creation of a valid SVG.
    """
        if competence_tree is None:
            competence_tree = self.dcm.competence_tree
        self.selected_paths=selected_paths
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
