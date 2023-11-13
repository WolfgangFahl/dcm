"""
Created on 2023-06-11

@author: wf
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from dataclasses_json import dataclass_json
from dcm.svg import SVG, SVGConfig
from json.decoder import JSONDecodeError
import json
    
@dataclass_json
@dataclass
class CompetenceElement:
    """
    A base class representing a generic competence element with common properties.

    Attributes:
        name (str): The name of the competence element.
        id (Optional[str]): An optional identifier for the competence element.
        url (Optional[str]): An optional URL for more information about the competence element.
        description (Optional[str]): An optional description of the competence element.
        color_code (str): A string representing a color code associated with the competence element.
    """

    name: str
    id: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    color_code: Optional[str] = None

@dataclass_json
@dataclass
class CompetenceFacet(CompetenceElement):
    """
    Represents a specific facet of a competence aspect, inheriting from CompetenceElement.

    This class can include additional properties or methods specific to a competence facet.
    """
    # Since all properties are inherited, no additional properties are defined here.

@dataclass_json
@dataclass
class CompetenceAspect(CompetenceElement):
    """
    Represents a broader category of competence, which includes various facets.

    Attributes:
        facets (List[CompetenceFacet]): A list of CompetenceFacet objects representing individual facets of this aspect.
    """
    facets: List[CompetenceFacet] = field(default_factory=list)
    credits: Optional[int]=None

@dataclass_json
@dataclass
class CompetenceLevel(CompetenceElement):
    """
    Defines a specific level of competence within the framework.

    Attributes:
        level (int): level number starting from 1 as the lowest and going up to as many level as defined for the CompetenceTree
    """
    level: int = 1

@dataclass_json
@dataclass
class CompetenceTree(CompetenceElement):
    """
    Represents the entire structure of competencies, including various aspects and levels.

    Attributes:
        competence_aspects (Dict[str, CompetenceAspect]): A dictionary mapping aspect IDs to CompetenceAspect objects.
        competence_levels (List[CompetenceLevel]): A list of CompetenceLevel objects representing the different levels in the competence hierarchy.
        element_names (Dict[str, str]): A dictionary holding the names for tree, aspects, facets, and levels.  The key is the type ("tree", "aspect", "facet", "level").
    """
    competence_aspects: Dict[str, CompetenceAspect] = field(default_factory=dict)
    competence_levels: List[CompetenceLevel] = field(default_factory=list)
    element_names: Dict[str, str] = field(default_factory=dict)
    
    def to_pretty_json(self):
        """
        Converts the CompetenceTree object to a pretty JSON string, handling null values.
        """
        json_str = self.to_json()
        json_dict = json.loads(json_str)

        def remove_none_values(data):
            """
            Recursively removes keys with None values from a dictionary, list, or nested structure.
            """
            if isinstance(data, dict):
                return {k: remove_none_values(v) for k, v in data.items() if v is not None}
            elif isinstance(data, list):
                return [remove_none_values(item) for item in data]
            return data

        none_free_dict = remove_none_values(json_dict)
        null_free_json_str=json.dumps(none_free_dict, indent=2)
        return null_free_json_str
    
    def add_legend(self, svg: SVG) -> None:
        """
        Add a legend to the SVG explaining the color codes for levels and aspects.
        Args:
            svg (SVG): The SVG object to which the legend will be added.
        """
        # Starting x position for the legends, starting 10 pixels from the left edge
        x_start = 10
        # y position for the legends, starting 20 pixels from the bottom edge
        y = svg.config.total_height - svg.config.legend_height + 20
        # Width and height of each legend color box
        box_width, box_height = 30, 20
        # Padding between legend items and between the color box and the text
        padding = 5
    
        # Add the competence level legend
        level_items = [
            (level.color_code, level.name) for level in self.competence_levels
        ]
        svg.add_legend_column(
            level_items,
            self.element_names.get("level", "Level"),
            x_start,
            y,
            box_width,
            box_height,
        )
    
        # Calculate the x position for the aspect legend based on the width of the level legend
        x_aspect_start = (
            x_start
            + box_width
            + padding
            + max(svg.get_text_width(level.name) for level in self.competence_levels)
            + padding
        )
    
        # Add the competence aspect legend
        aspect_items = [
            (aspect.color_code, aspect.name)
            for aspect in self.competence_aspects.values()
        ]
        svg.add_legend_column(
            aspect_items,
            self.element_names.get("aspect", "Aspect"),
            x_aspect_start,
            y,
            box_width,
            box_height,
        )
        
@dataclass_json
@dataclass
class Achievement:
    """
    Class representing an individual's achievement level for a specific competence facet.
    
    Attributes:
        facet_id (str): Identifier for the competence facet.
        level (int): The achieved level for this facet.
        percent(float): how well was the achievement reached?
        evidence (Optional[str]): Optional evidence supporting the achievement.
        date_assessed (Optional[str]): Optional date when the achievement was assessed (ISO-Format).
    """
    
    facet_id: str
    level: int
    percent: float
    evidence: Optional[str] = None
    date_assessed: Optional[str] = None
    
@dataclass
@dataclass_json
class Student:
    """
    A student with their achievements.
    Attributes:
        student_id (str): Identifier for the student.
        achievements (Dict[str, List[Achievement]]): A dictionary where each key is a competence tree identifier
                                                     and the value is a list of Achievement instances for that tree.
    """
    student_id: str
    achievements: Dict[str, List[Achievement]]
    
class DynamicCompetenceMap:
    """
    a visualization of a competence map
    """
    
    def __init__(self, competence_tree: CompetenceTree):
        """
        constructor
        """
        self.competence_tree = competence_tree
    
    @classmethod
    def examples_path(cls) -> str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), "../dcm_examples")
        path = os.path.abspath(path)
        return path
    
    @classmethod
    def get_example_json_strings(cls) -> dict:
        """
        get example json strings
        """
        example_jsons = {}
        examples_path = cls.examples_path()
        for filename in os.listdir(examples_path):
            if filename.endswith(".json"):
                filepath = os.path.join(examples_path, filename)
                with open(filepath, "r") as json_file:
                    file_prefix = filename.replace(".json", "")
                    json_text = json_file.read()
                    try:
                        json_data = json.loads(json_text)
                        if cls.is_valid_json(json_data):
                            example_jsons[file_prefix] = json_text
                    except Exception as ex:
                        cls.handle_json_issue(filename,json_text,ex)
        return example_jsons
    
    @classmethod
    def is_valid_json(cls,json_data):
        required_keys = {"name", "id", "url", "description", "element_names"}
        return all(key in json_data for key in required_keys)
    
    @classmethod
    def get_examples(cls) -> dict:
        examples = {}
        for name, json_string in cls.get_example_json_strings().items():
            dcm = DynamicCompetenceMap.from_json(name, json_string)
            examples[name] = dcm
        return examples
    
    @classmethod
    def from_json(cls,name:str, json_string: str) -> "DynamicCompetenceMap":
        """
        Load a DynamicCompetenceMap instance from a JSON string.
        """
        try:
            competence_tree = CompetenceTree.from_json(json_string)
            return DynamicCompetenceMap(competence_tree)
        except Exception as ex:
            cls.handle_json_issue(name,json_string,ex)
            
    @classmethod
    def handle_json_issue(cls,name:str,json_string:str,ex):
        if isinstance(ex,JSONDecodeError):
            lines = json_string.splitlines()  # Split the string into lines
            err_line = lines[ex.lineno - 1]  # JSONDecodeError gives 1-based lineno
            pointer = (
                " " * (ex.colno - 1) + "^"
            )  # Create a pointer string to indicate the error position
            error_message = (
                f"{name}:JSON parsing error on line {ex.lineno} column {ex.colno}:\n"
                f"{err_line}\n"
                f"{pointer}\n"
                f"{ex.msg}"
            )
            raise ValueError(error_message)  # Raise a new exception with this message
        else:
            error_message = f"error in {name}.json: {str(ex)}"
            raise ValueError(error_message)
    
    def generate_svg(
        self, filename: Optional[str] = None, config: Optional[SVGConfig] = None
    ) -> str:
        """
        Generate the SVG markup and optionally save it to a file. If a filename is given, the method
        will also save the SVG to that file. The SVG is generated based on internal state not shown here.
    
        Args:
            filename (str, optional): The path to the file where the SVG should be saved. Defaults to None.
            config (SVGConfig, optional): The configuration for the SVG canvas and legend. Defaults to default values.
    
        Returns:
            str: The SVG markup.
        """
        if config is None:
            config = SVGConfig()  # Use default configuration if none provided
        svg_markup = self.generate_svg_markup(self.competence_tree, config)
        if filename:
            self.save_svg_to_file(svg_markup, filename)
        return svg_markup
    
    def generate_svg_markup(
        self, competence_tree: CompetenceTree = None, config: SVGConfig = None
    ) -> str:
        """
        Generate SVG markup based on the provided competence tree and configuration.
    
        Args:
            competence_tree (CompetenceTree): The competence tree structure containing the necessary data.
            config (SVGConfig): The configuration for the SVG canvas and legend.
    
        Returns:
            str: The generated SVG markup.
        """
        if competence_tree is None:
            competence_tree = self.competence_tree
        competence_aspects = competence_tree.competence_aspects
        # Instantiate the SVG class
        svg = SVG(config)
        # use default config incase config was None
        config = svg.config
    
        # Center of the donut
        # Center of the donut chart should be in the middle of the main SVG area, excluding the legend
        cx = svg.width // 2
        cy = (config.total_height - config.legend_height) // 2  # Adjusted for legend
    
        outer_radius = min(cx, cy) * 0.9  # Leave some margin
        inner_radius = outer_radius * 0.33  # Choose a suitable inner radius
    
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
            # Draw the aspect segment as a donut segment
            svg.add_donut_segment(
                cx=cx,
                cy=cy,
                inner_radius=0,
                outer_radius=inner_radius,
                start_angle_deg=aspect_start_angle,
                end_angle_deg=aspect_start_angle + aspect_angle,
                color=aspect.color_code,
                segment_name=aspect.name,
                segment_id=aspect_code,
                segment_url=aspect.url,
            )
    
            facet_start_angle = (
                aspect_start_angle  # Facets start where the aspect starts
            )
            angle_per_facet = (
                aspect_angle / num_facets_in_aspect
            )  # Equal angle for each facet
    
            for facet in aspect.facets:
                # Add the facet segment as a donut segment
                svg.add_donut_segment(
                    cx=cx,
                    cy=cy,
                    inner_radius=inner_radius,
                    outer_radius=outer_radius,
                    start_angle_deg=facet_start_angle,
                    end_angle_deg=facet_start_angle + angle_per_facet,
                    color=facet.color_code,
                    segment_name=facet.name,
                    segment_id=facet.id,
                    segment_url=facet.url,
                )
                facet_start_angle += angle_per_facet
    
            aspect_start_angle += aspect_angle
    
        # optionally add legend
        if config.legend_height > 0:
            self.competence_tree.add_legend(svg)
    
        # Return the SVG markup
        return svg.get_svg_markup()
    
    def save_svg_to_file(self, svg_markup: str, filename: str):
        # Save the SVG content to a file
        with open(filename, "w") as file:
            file.write(svg_markup)
