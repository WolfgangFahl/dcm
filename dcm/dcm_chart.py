"""
Created on 2024-01-12

@author: wf
"""
import copy
from typing import List, Optional

from dcm.dcm_core import (
    CompetenceElement,
    CompetenceFacet,
    CompetenceTree,
    DynamicCompetenceMap,
    Learner,
)
from dcm.svg import SVG, DonutSegment, SVGConfig, SVGNodeConfig


class DcmChart:
    """
    a Dynamic competence map chart
    """

    def __init__(self, dcm: DynamicCompetenceMap):
        """
        Constructor
        """
        self.dcm = dcm
        self.text_mode = "none"

    def precalculate_segments(self, competence_tree: CompetenceTree) -> dict:
        """
        Pre-calculate the DonutSegment for each element in the CompetenceTree
        and store it in a dictionary by path for quick lookup.

        Args:
            competence_tree (CompetenceTree): The competence tree to precalculate the segments for.

        Returns:
            dict: A dictionary mapping paths to their corresponding DonutSegment.
        """
        segment_by_path = {}
        full_circle = 360
        aspect_angle = (
            full_circle / len(competence_tree.aspects)
            if competence_tree.aspects
            else full_circle
        )

        for aspect in competence_tree.aspects:
            start_angle_aspect = 0
            for area_index, area in enumerate(aspect.areas):
                end_angle_aspect = start_angle_aspect + aspect_angle

                # Create a DonutSegment for the area
                segment_by_path[area.path] = DonutSegment(
                    cx=self.cx,
                    cy=self.cy,
                    inner_radius=self.tree_radius,
                    outer_radius=self.tree_radius * 2,  # Modify as needed
                    start_angle=start_angle_aspect,
                    end_angle=end_angle_aspect,
                    fill="white",  # Default fill color for segments with no elements
                )

                # Calculate and store segments for sub-elements (facets)
                for facet_index, facet in enumerate(area.facets):
                    facet_angle = aspect_angle / len(area.facets)
                    start_angle_facet = start_angle_aspect + (facet_index * facet_angle)
                    end_angle_facet = start_angle_facet + facet_angle

                    segment_by_path[facet.path] = DonutSegment(
                        cx=self.cx,
                        cy=self.cy,
                        inner_radius=self.tree_radius * 2,  # Modify as needed
                        outer_radius=self.tree_radius * 3,  # Modify as needed
                        start_angle=start_angle_facet,
                        end_angle=end_angle_facet,
                        fill=facet.color_code if facet.color_code else "white",
                    )

                # Update the start angle for the next area within the same aspect.
                start_angle_aspect = end_angle_aspect

        return segment_by_path

    def generate_svg_from_segments(
        self, competence_tree: CompetenceTree, config: Optional[SVGConfig] = None
    ) -> str:
        """
        Generate the SVG markup using pre-calculated DonutSegment objects stored in segments_by_path.

        Args:
            competence_tree(CompetenceTree): a competence tree
            segments_by_path (dict): A dictionary mapping element paths to their corresponding DonutSegment objects.
            config (SVGConfig, optional): The configuration for the SVG canvas and legend. Defaults to default values.

        Returns:
            str: The SVG markup.
        """
        if config is None:
            config = SVGConfig(with_popup=True)  # Use default configuration if none provided
        svg = self.prepare_and_add_inner_circle(config, competence_tree=competence_tree)
        # Pre-calculate segments for the competence tree
        segments_by_path = self.precalculate_segments(competence_tree)
        # Iterate over the segments and add them to the SVG
        for path, segment in segments_by_path.items():
            element = competence_tree.lookup_by_path(path)
            config = self.get_element_config(element)
            svg.add_donut_segment(config, segment)
        return svg.get_svg_markup(with_java_script=True)

    def prepare_and_add_inner_circle(
        self, config, competence_tree: CompetenceTree, lookup_url: str = None
    ):
        """
        prepare the SVG markup generation and add
        the inner_circle
        """
        self.lookup_url = (
            competence_tree.lookup_url if competence_tree.lookup_url else lookup_url
        )

        svg = SVG(config)
        self.svg = svg
        config = svg.config
        # center of circle
        self.cx = config.width // 2
        self.cy = (config.total_height - config.legend_height) // 2
        self.radius_steps = competence_tree.total_levels
        self.tree_radius = config.width / 2 / self.radius_steps / 2
        self.circle_config = competence_tree.to_svg_node_config(
            x=self.cx, y=self.cy, width=self.tree_radius
        )
        svg.add_circle(config=self.circle_config)
        if self.text_mode != "none":
            svg.add_text(
                self.cx,
                self.cy,
                competence_tree.short_name,
                centered=True,
                fill="white",
            )
        return svg

    def generate_svg(
        self,
        filename: Optional[str] = None,
        learner: Optional[Learner] = None,
        config: Optional[SVGConfig] = None,
        text_mode: str = "none",
    ) -> str:
        """
        Generate the SVG markup and optionally save it to a file. If a filename is given, the method
        will also save the SVG to that file. The SVG is generated based on internal state not shown here.

        Args:
            filename (str, optional): The path to the file where the SVG should be saved. Defaults to None.
            learner(Learner): the learner to show the achievements for
            config (SVGConfig, optional): The configuration for the SVG canvas and legend. Defaults to default values.
            text_mode(str): text display mode
        Returns:
            str: The SVG markup.
        """
        if config is None:
            config = SVGConfig(with_popup=True)  # Use default configuration if none provided
        svg_markup = self.generate_svg_markup(
            self.dcm.competence_tree,
            learner=learner,
            config=config,
            text_mode=text_mode,
        )
        if filename:
            self.save_svg_to_file(svg_markup, filename)
        return svg_markup

    def get_element_config(self, element: CompetenceElement) -> SVGNodeConfig:
        """
        get a configuration for the given element

        Args:
            element(CompetenceElement): the element

        Return:
            SVGNodeConfig: an SVG Node configuration
        """
        if element is None:
            element_config = SVGNodeConfig(x=self.cx, y=self.cy, fill="white")
            return element_config
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
        return element_config

    def add_donut_segment(
        self,
        svg: SVG,
        element: CompetenceElement,
        segment: DonutSegment,
        level_color=None,
        achievement_level=None,
    ) -> DonutSegment:
        """
        create a donut segment for the
        given competence element and add it
        to the given SVG

        if level color is available an achievement
        needs to be potentially shown
        """
        element_config = self.get_element_config(element)
        # make sure we show the text on the original segment
        text_segment = copy.deepcopy(segment)

        if level_color:
            element_config.fill = level_color  # Set the color
            text_mode = "none"
        if element and element.path in self.selected_paths:
            element_config.element_class = "selected"

        if achievement_level is not None:
            total_levels = self.dcm.competence_tree.total_valid_levels
            relative_radius = (segment.outer_radius - segment.inner_radius) * (
                achievement_level / total_levels
            )
            segment.outer_radius = segment.inner_radius + relative_radius

        result = svg.add_donut_segment(config=element_config, segment=segment)
        if element and self.text_mode != "none":
            # no autofill please
            # textwrap.fill(element.short_name, width=20)
            text = element.short_name
            self.svg.add_text_to_donut_segment(
                text_segment, text, direction=self.text_mode
            )
        return result

    def generate_donut_segment_for_achievement(
        self,
        svg: SVG,
        learner: Learner,
        element: CompetenceElement,
        segment: DonutSegment,
    ) -> DonutSegment:
        """
        generate a donut segment for the
        learner's achievements
        corresponding to the given path and return it's segment definition
        """
        achievement = learner.achievements_by_path.get(element.path, None)
        result = None
        if achievement and achievement.level:
            # Retrieve the color for the achievement level
            level_color = self.dcm.competence_tree.get_level_color(achievement.level)

            if level_color:
                # set the color and radius of
                # the segment for achievement
                # make sure we don't interfere with the segment calculations
                segment = copy.deepcopy(segment)
                result = self.add_donut_segment(
                    svg, element, segment, level_color, achievement.level
                )
        return result

    def generate_donut_segment_for_element(
        self,
        svg: SVG,
        element: CompetenceElement,
        learner: Learner,
        segment: DonutSegment,
    ) -> DonutSegment:
        """
        generate a donut segment for a given element of
        the CompetenceTree
        """
        # Simply create the donut segment without considering the achievement
        result = self.add_donut_segment(svg=svg, element=element, segment=segment)
        # check learner achievements
        if learner:
            _learner_segment = self.generate_donut_segment_for_achievement(
                svg=svg, learner=learner, element=element, segment=segment
            )
        return result

    def generate_pie_elements(
        self,
        level: int,
        svg: SVG,
        parent_element: CompetenceElement,
        learner: Learner,
        segment: DonutSegment,
        symmetry_level: int = 1,
    ):
        """
        generate the pie elements (donut segments) for the subelements
        of the given parent_element at the given level
        e.g. aspects, areas or facets - taking the learner
        achievements into account if a corresponding achievement
        is found. The segment limits the area in which the generation may operate

        the symmetry level denotes at which level the rings should be symmetric
        """
        sub_element_name = self.levels[level]
        # get the elements to be displayed
        elements = getattr(parent_element, sub_element_name)
        total = len(elements)
        total_sub_elements = self.dcm.competence_tree.total_elements[sub_element_name]
        # are there any elements to be shown?
        if total == 0:
            # there are no subelements we might need a single
            # empty donut segment
            # but only if there are any other available subelements
            # on this level
            if total_sub_elements == 0:
                return
            sub_segment = DonutSegment(
                cx=self.cx,
                cy=self.cy,
                inner_radius=segment.outer_radius,
                outer_radius=segment.outer_radius + self.tree_radius * 2,
                start_angle=segment.start_angle,
                end_angle=segment.end_angle,
            )
            self.generate_donut_segment_for_element(
                svg, element=None, learner=None, segment=sub_segment
            )
        else:
            angle_per_element = (segment.end_angle - segment.start_angle) / total
            start_angle = segment.start_angle
            for element in elements:
                end_angle = start_angle + angle_per_element
                sub_segment = DonutSegment(
                    cx=self.cx,
                    cy=self.cy,
                    inner_radius=segment.outer_radius,
                    outer_radius=segment.outer_radius + self.tree_radius * 2,
                    start_angle=start_angle,
                    end_angle=end_angle,
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
        selected_paths: List = [],
        config: SVGConfig = None,
        with_java_script: bool = True,
        text_mode: str = "none",
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
            text_mode(str): text display mode
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
        self.selected_paths = selected_paths
        self.levels = ["aspects", "areas", "facets"]
        self.text_mode = text_mode

        svg = self.prepare_and_add_inner_circle(config, competence_tree, lookup_url)

        segment = DonutSegment(
            cx=self.cx, cy=self.cy, inner_radius=0, outer_radius=self.tree_radius
        )
        self.generate_pie_elements(
            level=0,
            svg=svg,
            parent_element=competence_tree,
            learner=learner,
            segment=segment,
        )
        if svg.config.legend_height > 0:
            competence_tree.add_legend(svg)

        return svg.get_svg_markup(with_java_script=with_java_script)

    def save_svg_to_file(self, svg_markup: str, filename: str):
        """
        Save the SVG content to a file
        """
        with open(filename, "w") as file:
            file.write(svg_markup)
