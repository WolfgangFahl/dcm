"""
Created on 2024-01-12

@author: wf
"""
from dataclasses import dataclass
from dcm.dcm_core import CompetenceTree, DynamicCompetenceMap, Learner
from dcm.svg import SVG,SVGConfig
from typing import Optional
from urllib.parse import quote

@dataclass
class DcmChartConfig(object):
    """
    Dynamic competence map chart
    """
    cx: float
    cy: float
    tree_radius: float
    aspect_radius: float
    facet_radius: float
    

class DcmChart():
    """
    a Dynamic competence map chart
    """
    
    def __init__(self,dcm:DynamicCompetenceMap):
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

    def generate_svg_markup(
        self,
        competence_tree: CompetenceTree = None,
        learner: Learner = None,
        config: SVGConfig = None,
        with_java_script: bool = True,
        lookup_url: str = "",
    ) -> str:
        """
        Generate SVG markup based on the provided competence tree and configuration.

        Args:
            competence_tree (CompetenceTree): The competence tree structure containing the necessary data.
            learner(Learner): the learner to show the achievements for
            config (SVGConfig): The configuration for the SVG canvas and legend.
            lookup_url(str): the lookup_url to use if there is none defined in the CompetenceTree

        Returns:
            str: The generated SVG markup.
        """
        if competence_tree is None:
            competence_tree = self.dcm.competence_tree
        lookup_url = (
            competence_tree.lookup_url if competence_tree.lookup_url else lookup_url
        )
        competence_aspects = competence_tree.competence_aspects
        # Instantiate the SVG class
        svg = SVG(config)
        self.svg = svg
        # use default config incase config was None
        config = svg.config

        # Center of the donut
        # Center of the donut chart should be in the middle of the main SVG area, excluding the legend
        cx = svg.width // 2
        cy = (config.total_height - config.legend_height) // 2  # Adjusted for legend

        # Calculate the radius for the central circle (10% of the width)
        tree_radius = cx / 9

        # Add the central circle representing the CompetenceTree
        circle_config = competence_tree.to_svg_node_config(
            x=cx, y=cy, width=tree_radius
        )
        svg.add_circle(config=circle_config)

        facet_radius = min(cx, cy) * 0.9  # Leave some margin
        aspect_radius = facet_radius / 3  # Choose a suitable inner radius

        # Total number of facets
        total_facets = sum(len(aspect.facets) for aspect in competence_aspects.values())

        # Starting angle for the first aspect
        aspect_start_angle = 0

        for aspect_code, aspect in competence_aspects.items():
            num_facets_in_aspect = len(aspect.facets)

            # Skip aspects with no facets
            if num_facets_in_aspect == 0:
                continue
            aspect_angle = (num_facets_in_aspect / total_facets) * 360

            aspect_url = (
                aspect.url
                if aspect.url
                else f"{lookup_url}/description/{quote(competence_tree.id)}/{quote(aspect_code)}"
                if lookup_url is not None
                else None
            )
            show_as_popup = aspect.url is None

            aspect_config = aspect.to_svg_node_config(
                url=aspect_url,
                show_as_popup=show_as_popup,
                x=cx,
                y=cy,
                width=tree_radius,  # inner radius
                height=aspect_radius,  # outer radius
            )
            # fix id
            aspect_config.id = aspect_code
            # Draw the aspect segment as a donut segment
            svg.add_donut_segment(
                config=aspect_config,
                start_angle_deg=aspect_start_angle,
                end_angle_deg=aspect_start_angle + aspect_angle,
            )

            facet_start_angle = (
                aspect_start_angle  # Facets start where the aspect starts
            )
            angle_per_facet = (
                aspect_angle / num_facets_in_aspect
            )  # Equal angle for each facet

            for facet in aspect.facets:
                # Add the facet segment as a donut segment
                facet_url = (
                    facet.url
                    if facet.url
                    else f"{lookup_url}/description/{quote(competence_tree.id)}/{quote(aspect_code)}/{quote(str(facet.id))}"
                    if lookup_url is not None
                    else None
                )
                show_as_popup = facet.url is None
                facet_config = facet.to_svg_node_config(
                    url=facet_url,
                    show_as_popup=show_as_popup,
                    x=cx,
                    y=cy,
                    width=aspect_radius,  # inner radius
                    height=facet_radius,  # outer radius
                )
                # check learner achievements
                if learner:
                    achievement = learner.achievements_by_path.get(facet.path, None)
                    if achievement and achievement.level:
                        facet_config.element_class = "selected"

                svg.add_donut_segment(
                    config=facet_config,
                    start_angle_deg=facet_start_angle,
                    end_angle_deg=facet_start_angle + angle_per_facet,
                )
                facet_start_angle += angle_per_facet

            aspect_start_angle += aspect_angle

        # optionally add legend
        if config.legend_height > 0:
            competence_tree.add_legend(svg)

        # Return the SVG markup
        return svg.get_svg_markup(with_java_script=with_java_script)

    def save_svg_to_file(self, svg_markup: str, filename: str):
        """
        Save the SVG content to a file
        """
        with open(filename, "w") as file:
            file.write(svg_markup)
