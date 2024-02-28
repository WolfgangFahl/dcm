"""
Created on 2024-01-12

@author: wf
"""
import copy
from typing import Dict, List, Optional, Tuple

from dcm.dcm_core import (
    CompetenceElement,
    CompetenceFacet,
    CompetenceTree,
    DynamicCompetenceMap,
    Learner,
    RingSpec,
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
        ringspec = competence_tree.ring_specs.get("tree")
        self.tree_radius = ringspec.outer_ratio * config.width / 2

        self.circle_config = competence_tree.to_svg_node_config(
            x=self.cx, y=self.cy, width=self.tree_radius
        )
        svg.add_circle(config=self.circle_config)
        if ringspec.text_mode != "empty":
            svg.add_text(
                self.cx,
                self.cy,
                competence_tree.short_name,
                text_anchor="middle",
                center_v=True,
                fill="white",
            )
        return svg

    def generate_svg(
        self,
        filename: Optional[str] = None,
        learner: Optional[Learner] = None,
        config: Optional[SVGConfig] = None,
        text_mode: str = "empty",
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
            config = SVGConfig(
                with_popup=True
            )  # Use default configuration if none provided
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

    def get_stacked_segment(
        self,
        level: int,
        total_levels: int,
        segment: DonutSegment,
        element_config: SVGNodeConfig,
    ) -> Tuple[DonutSegment, SVGNodeConfig]:
        """
        Calculate the stacked segment for a given level.

        Args:
            level (int): The current level for which to calculate the segment.
            total_levels (int): The total number of levels.
            segment (DonutSegment): The original donut Segment.
            element_config (SVGNodeConfig): The element configuration.

        Returns:
            Tuple[DonutSegment, SVGNodeConfig]:
                The calculated stacked segment and its configuration for the given level.

        """
        level_color = self.dcm.competence_tree.get_level_color(level)
        stack_element_config = copy.deepcopy(element_config)
        stack_element_config.fill = level_color
        ratio = level / total_levels
        relative_radius = (segment.outer_radius - segment.inner_radius) * ratio
        stacked_segment = copy.deepcopy(segment)
        stacked_segment.outer_radius = segment.inner_radius + relative_radius
        return stacked_segment, stack_element_config

    def add_donut_segment(
        self,
        svg: SVG,
        element: CompetenceElement,
        segment: DonutSegment,
        level_color=None,
        achievement_level=None,
        ringspec: RingSpec = None,
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
        if element and element.path in self.selected_paths:
            element_config.element_class = "selected"
            element_config.color = "blue"
        # in case we need to draw an achievement
        total_levels = self.dcm.competence_tree.total_valid_levels

        if achievement_level is None:
            result = svg.add_donut_segment(config=element_config, segment=segment)
        else:
            if not self.dcm.competence_tree.stacked_levels:
                ratio = achievement_level / total_levels
                relative_radius = (segment.outer_radius - segment.inner_radius) * ratio
                segment.outer_radius = segment.inner_radius + relative_radius
                result = svg.add_donut_segment(config=element_config, segment=segment)
            else:
                # create the stacked segments starting with the highest level
                for level in range(achievement_level, 0, -1):
                    stacked_segment, stack_element_config = self.get_stacked_segment(
                        level, total_levels, segment, element_config
                    )
                    # the result will be overriden in the loop so we'll return the innermost
                    result = svg.add_donut_segment(
                        config=stack_element_config, segment=stacked_segment
                    )
        if element:
            text_mode = "empty"
            if segment.text_mode:
                text_mode = segment.text_mode
            if text_mode != "empty":
                # no autofill please
                # textwrap.fill(element.short_name, width=20)
                text = element.short_name
                self.svg.add_text_to_donut_segment(
                    text_segment, text, direction=text_mode
                )
        # in stacked mode show the level circles
        # by drawing arcs even if no achievements
        # are available
        if ringspec and ringspec.levels_visible:
            if total_levels:
                svg.add_element(f"<!-- arcs for {element.path} -->")
                for level in range(total_levels):
                    stacked_segment, stack_element_config = self.get_stacked_segment(
                        level, total_levels, segment, element_config
                    )
                    fill = "white"  # Set the color for unachieved levels
                    donut_path = svg.get_donut_path(
                        stacked_segment, radial_offset=1, middle_arc=True
                    )  # Get the path for the stacked segment
                    svg.add_element(
                        f'<path d="{donut_path}" stroke="{fill}" fill="none" stroke-width="1.5" />'
                    )  # Draw the path in SVG

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
        ringspec: RingSpec = None,
    ) -> DonutSegment:
        """
        generate a donut segment for a given element of
        the CompetenceTree
        """
        if segment.outer_radius == 0.0:
            result = segment
        else:
            # Simply create the donut segment without considering the achievement
            result = self.add_donut_segment(
                svg=svg, element=element, segment=segment, ringspec=ringspec
            )
            # check learner achievements
            if learner:
                _learner_segment = self.generate_donut_segment_for_achievement(
                    svg=svg, learner=learner, element=element, segment=segment
                )
        return result
    
    def generate_pie_elements_for_segments(
        self,
        svg: SVG,
        ct: CompetenceTree,
        segments: Dict[str, Dict[str, DonutSegment]],
        learner: Learner
    ):
        """
        Generate pie elements for the competence tree using pre-calculated segments.
    
        This method will iterate through the provided segments dictionary, using each pre-calculated
        DonutSegment to generate and render pie elements (e.g., aspects, areas, or facets) based on
        the learner's achievements.
    
        Args:
            svg (SVG): The SVG object where the pie elements will be drawn.
            ct (CompetenceTree): The competence tree structure.
            segments (Dict[str, Dict[str, DonutSegment]]): A nested dictionary where the first key is the
                                                           level name (e.g., 'aspect', 'area', 'facet'),
                                                           and the second key is an element's path, mapping
                                                           to its corresponding DonutSegment.
            learner (Learner): The learner object containing achievement data.
        """
        for level_name, segment_dict in segments.items():
            ringspec=ct.ring_specs[level_name]
            for path, segment in segment_dict.items():
                element = ct.elements_by_path.get(path, None)
                if element:
                    self.generate_donut_segment_for_element(
                        svg, element, learner, segment=segment, ringspec=ringspec  
                    )
                    
    def create_donut_segment(self,
         parent_segment: DonutSegment,
         start_angle: float,
         end_angle: float,
         ringspec: RingSpec) -> DonutSegment:
        """
        Creates a new DonutSegment based on the specified parameters, calculating its
        inner and outer radii based on SVG configuration and ring specifications.

        Args:
            parent_segment (DonutSegment): The parent segment from which the new segment inherits its center (cx, cy).
            start_angle (float): The starting angle of the new segment.
            end_angle (float): The ending angle of the new segment.
            ringspec (RingSpec): An instance of RingSpec defining the ratios for inner and outer radii, and the text mode.

        Returns:
            DonutSegment: A new DonutSegment instance configured as specified.
        """
        # Calculate the actual inner and outer radii based on the SVG config and ringspec ratios
        inner_radius = self.svg.config.width / 2 * ringspec.inner_ratio
        outer_radius = self.svg.config.width / 2 * ringspec.outer_ratio
        # Create a new segment for this element
        segment = DonutSegment(
            cx=parent_segment.cx,
            cy=parent_segment.cy,
            inner_radius=inner_radius,
            outer_radius=outer_radius,
            start_angle=start_angle,
            end_angle=end_angle,
            text_mode=ringspec.text_mode,
        )
        return segment
                    
    def calculate_sub_segments(
        self,
        ct: CompetenceTree, 
        parent_segment: DonutSegment, 
        level_name: str,
        symmetry_mode: str,
        elements: List[CompetenceElement],
        lenient:bool=True
    ) -> Dict[str, DonutSegment]:
        """
        Calculates and returns a dictionary of DonutSegment objects for a given level in the Competence Tree.
    
        This method divides a parent segment into sub-segments based on the number of elements in the specified level,
        and assigns each sub-segment to the corresponding element's path.
    
        Args:
            ct: An instance of CompetenceTree representing the entire competence structure.
            parent_segment: A DonutSegment instance representing the parent segment within which the sub-segments will be calculated.
            level_name: The name of the level (e.g., 'aspect', 'area', 'facet') for which sub-segments are being calculated.
            symmetry_mode: The symmetry mode ('symmetric' or 'asymmetric') affecting segment calculation.
            elements: A list of CompetenceElement instances at the current level.
            lenient (bool): if True symmetry mode will be adjusted to count in case there are no values
        Returns:
            A dictionary where keys are element paths and values are DonutSegment instances representing each element's segment in the visualization.
        """
        ringspec: RingSpec = ct.ring_specs[level_name]
        sub_segments: Dict[str, DonutSegment] = {}
        attr_names={
            "time": "time",
            "score":"max_score"
        }
        if len(elements) == 0:
            return sub_segments
        num_zero_none_values = 0
    
        if symmetry_mode=="count":
            total = len(elements)
        else:
            attr_name=attr_names[symmetry_mode]
            total=0
            min_value = float('inf')  # Initialize to infinity for proper minimum comparison
    
            # Initial loop to calculate total and count 0/None values
            for element in elements:
                value = getattr(element, attr_name)
                if value in (0, None):
                    num_zero_none_values += 1
                else:
                    total += value
                    if value < min_value:
                        min_value = value
        
        if total == 0 and num_zero_none_values == len(elements):
            if not lenient:
                raise ValueError("All element values are 0 or None, cannot divide segment.")
            else:
                # robust reaction on issue
                symmetry_mode="count"
                num_zero_none_values=0
                total = len(elements)
    
        # Correct handling when all values are not 0/None 
        # and therefore  min_value was not updated
        if num_zero_none_values>0:    
            # Adjust total value for 0/None values
            # we use the min_value as a default
            total += min_value * num_zero_none_values
   
        start_angle = parent_segment.start_angle
    
        for element in elements:
            if symmetry_mode=="count":
                value=1
            else:
                value = getattr(element, attr_name) or min_value
            proportion = value / total
            angle_span = (parent_segment.end_angle - parent_segment.start_angle) * proportion
            end_angle = start_angle + angle_span
    
            segment = self.create_donut_segment(
                parent_segment, start_angle, end_angle, ringspec
            )
            sub_segments[element.path] = segment
            start_angle = end_angle
    
        return sub_segments

    
    def calculate_parent_segments(
        self,
        segments: Dict[str, DonutSegment],
        ringspec: RingSpec
    ) -> Dict[str, DonutSegment]:
        """
        Aggregates child segments into parent segments, calculating the combined start and end angles
        for each parent based on its children segments. It uses the `create_donut_segment` function to
        ensure that newly created parent segments have the correct dimensions according to the specified `ringspec`.
    
        Args:
            segments: A dictionary of child segments with paths as keys and DonutSegment objects as values.
            ringspec: A RingSpec object specifying the dimensions for the newly created parent segments.
    
        Returns:
            A dictionary of aggregated parent segments with parent paths as keys and newly created DonutSegment objects as values.
        """
        parent_segments: Dict[str, DonutSegment] = {}
    
        for path, segment in segments.items():
            # Extract the parent path
            parent_path = '/'.join(path.split('/')[:-1])
            if parent_path not in parent_segments:
                # For a new parent segment, initialize with current segment's angles
                parent_segments[parent_path] = self.create_donut_segment(
                    parent_segment=segment,  # Assuming there's logic to determine this correctly
                    start_angle=segment.start_angle,
                    end_angle=segment.end_angle,
                    ringspec=ringspec
                )
            else:
                # Update existing parent segment's angles
                parent_segment = parent_segments[parent_path]
                parent_segment.start_angle = min(segment.start_angle, parent_segment.start_angle)
                parent_segment.end_angle = max(segment.end_angle, parent_segment.end_angle)
    
        return parent_segments

    def calculate_segments(
        self, 
        ct: CompetenceTree, 
        tree_segment: DonutSegment
    ) -> Dict[str, Dict[str, DonutSegment]]:
        """
        Pre-calculate the donut segments for each level of the competence tree.
    
        Args:
            ct: A CompetenceTree instance for which segments are to be calculated.
            tree_segment: A DonutSegment instance representing the whole competence tree.
    
        Returns:
            A nested dictionary where the first-level keys are level names (e.g., 'aspect', 'area', 'facet'),
            and the second-level keys are element paths with their corresponding DonutSegment objects as values.
        """

        self.level_segments = {
            "aspect": {}, 
            "area": {}, 
            "facet": {}
        }
        
        symmetry_level, symmetry_mode = ct.get_symmetry_spec()
        symmetry_elements = ct.elements_by_level[symmetry_level]
        sub_segments=self.calculate_sub_segments(ct, tree_segment, symmetry_level, symmetry_mode,symmetry_elements)
        self.level_segments[symmetry_level]=sub_segments
        if symmetry_level=="facet":
            # work from outer level to inner
            area_segments=self.calculate_parent_segments(sub_segments, ct.ring_specs["area"])
            self.level_segments["area"]=area_segments
            aspect_segments=self.calculate_parent_segments(area_segments, ct.ring_specs["aspect"])
            self.level_segments["aspect"]=aspect_segments
        elif symmetry_level == "area":
            # work from outer level to inner
            area_segments=sub_segments
            aspect_segments=self.calculate_parent_segments(area_segments, ct.ring_specs["aspect"])
            self.level_segments["aspect"]=aspect_segments
            # work from middle level to outer
            for area_path, area_segment in area_segments.items():
                area = ct.elements_by_path[area_path]
                facet_segments = self.calculate_sub_segments(ct, area_segment, "facet", symmetry_mode, area.facets)
                self.level_segments["facet"].update(facet_segments)
        elif symmetry_level == "aspect":
            # work from inner level to outer
            for aspect_path, aspect_segment in sub_segments.items():
                aspect = ct.elements_by_path[aspect_path]
                area_segments = self.calculate_sub_segments(ct, aspect_segment, "area", symmetry_mode, aspect.areas)
                self.level_segments["area"].update(area_segments)
                for area_path, area_segment in area_segments.items():
                    area = ct.elements_by_path[area_path]
                    facet_segments = self.calculate_sub_segments(ct, area_segment, "facet", symmetry_mode, area.facets)
                    self.level_segments["facet"].update(facet_segments)
         
        else:
            raise ValueError(f"Invalid symmetry_level {symmetry_level}")
        return self.level_segments

    def generate_svg_markup(
        self,
        competence_tree: CompetenceTree = None,
        learner: Learner = None,
        selected_paths: List = [],
        config: SVGConfig = None,
        with_java_script: bool = True,
        text_mode: str = "empty",
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
            text_mode(str): text display mode
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
        self.selected_paths = selected_paths
        
        competence_tree.calculate_ring_specs(text_mode)
        svg = self.prepare_and_add_inner_circle(config, competence_tree, lookup_url)

        segment = DonutSegment(
            cx=self.cx, cy=self.cy, inner_radius=0, outer_radius=self.tree_radius
        )
        segments=self.calculate_segments(competence_tree,segment)
        self.generate_pie_elements_for_segments(svg=svg, ct=competence_tree, segments=segments, learner=learner)
        #self.generate_pie_elements(
        #    level=1,
        #    svg=svg,
        #    ct=competence_tree,
        #    parent_element=competence_tree,
        #    learner=learner,
        #    segment=segment,
        #)
        if svg.config.legend_height > 0:
            competence_tree.add_legend(svg)

        return svg.get_svg_markup(with_java_script=with_java_script)

    def save_svg_to_file(self, svg_markup: str, filename: str):
        """
        Save the SVG content to a file
        """
        with open(filename, "w") as file:
            file.write(svg_markup)
