"""
Created on 2023-06-11

@author: wf
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from dataclasses_json import dataclass_json
from dcm.svg import SVG
from json.decoder import JSONDecodeError

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
    facets: List[CompetenceFacet]=field(default_factory=list)

@dataclass_json
@dataclass
class CompetenceLevel(CompetenceElement):
    """
    Defines a specific level of competence within the framework.

    Attributes:
        level (int): level number starting from 1 as the lowest and going up to as many level as defined for the CompetenceTree 
    """
    level: int=1

@dataclass_json
@dataclass
class CompetenceTree:
    """
    Represents the entire structure of competencies, including various aspects and levels.

    Attributes:
        competence_aspects (Dict[str, CompetenceAspect]): A dictionary mapping aspect IDs to CompetenceAspect objects.
        competence_levels (List[CompetenceLevel]): A list of CompetenceLevel objects representing the different levels in the competence hierarchy.
    """
    competence_aspects: Dict[str, CompetenceAspect]
    competence_levels: List[CompetenceLevel]


class DynamicCompetenceMap:
    """
    a visualization of a competence map
    """

    def __init__(self,competence_tree:CompetenceTree):
        """
        constructor
        """
        self.competence_tree = competence_tree
        
    @classmethod
    def examples_path(cls)->str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), '../dcm_examples')
        path = os.path.abspath(path)
        return path
    
    @classmethod
    def get_example_json_strings(cls)->dict:
        """
        get example json strings
        """
        example_jsons={}
        examples_path=cls.examples_path()
        for filename in os.listdir(examples_path):
            if filename.endswith('.json'):
                filepath = os.path.join(examples_path, filename)
                with open(filepath, 'r') as json_file:
                    file_prefix=filename.replace(".json","")
                    json_text =json_file.read()
                    example_jsons[file_prefix]=json_text
        return example_jsons            
            
    @classmethod
    def get_examples(cls)->dict:
        examples={}
        for name,json_string in cls.get_example_json_strings().items():
            dcm=DynamicCompetenceMap.from_json(name, json_string)
            examples[name]=dcm
        return examples

    @staticmethod
    def from_json(name,json_string: str) -> 'DynamicCompetenceMap':
        """
        Load a DynamicCompetenceMap instance from a JSON string.
        """
        try:
            competence_tree = CompetenceTree.from_json(json_string)
            return DynamicCompetenceMap(competence_tree)
        except JSONDecodeError as e:
            lines = json_string.splitlines()  # Split the string into lines
            err_line = lines[e.lineno - 1]  # JSONDecodeError gives 1-based lineno
            pointer = " " * (e.colno - 1) + "^"  # Create a pointer string to indicate the error position
            error_message = (
                f"{name}:JSON parsing error on line {e.lineno} column {e.colno}:\n"
                f"{err_line}\n"
                f"{pointer}\n"
                f"{e.msg}"
            )
            raise ValueError(error_message)  # Raise a new exception with this message
        except Exception as ex:
            error_message=f"error in {name}.json: {str(ex)}"
            raise ValueError(error_message)

    def generate_svg(self, filename: Optional[str] = None, width: int = 600, height: int = 600) -> str:
        """
        Generate the SVG markup and optionally save it to a file. If a filename is given, the method
        will also save the SVG to that file. The SVG is generated based on internal state not shown here.

        Args:
            filename (str, optional): The path to the file where the SVG should be saved. Defaults to None.
            width (int): The width of the SVG canvas in pixels. Defaults to 600.
            height (int): The height of the SVG canvas in pixels. Defaults to 600.

        Returns:
            str: The SVG markup.
        """
        svg_markup = self.generate_svg_markup(self.competence_tree,width, height)  # Assuming this is defined to generate the SVG content.
        if filename:
            self.save_svg_to_file(svg_markup, filename)  # Assuming this is defined to handle file saving.
        return svg_markup
    
    def generate_svg_markup(self,competence_tree=None, width: int = 600, height: int = 600) -> str:
        """
        Generate SVG markup based on the provided competence tree. The exact details of how the competence
        tree is used to generate the SVG are not shown here.

        Args:
            competence_tree (Any): The competence tree structure containing the necessary data.
            width (int): The width of the SVG canvas in pixels. Defaults to 600.
            height (int): The height of the SVG canvas in pixels. Defaults to 600.

        Returns:
            str: The generated SVG markup.
        """
        if competence_tree is None:
            competence_tree=self.competence_tree
        competence_aspects = competence_tree.competence_aspects
    
        # Instantiate the SVG class
        svg = SVG(width=width, height=height)
    
        # Center of the donut
        cx, cy = svg.width // 2, svg.height // 2
        outer_radius = min(cx, cy) * 0.8  # Leave some margin
        inner_radius = outer_radius * 0.5  # Choose a suitable inner radius
    
        # Total number of facets
        total_facets = sum(len(aspect.facets) for aspect in competence_aspects.values())
    
        # Starting angle for the first aspect
        aspect_start_angle = 0
    
        for aspect_code, aspect in competence_aspects.items():
            num_facets_in_aspect = len(aspect.facets)
            aspect_angle = (num_facets_in_aspect / total_facets) * 360
    
            # Draw the aspect segment as a donut segment
            svg.add_donut_segment(
                cx=cx,
                cy=cy,
                inner_radius=0,
                outer_radius=outer_radius,
                start_angle_deg=aspect_start_angle,
                end_angle_deg=aspect_start_angle + aspect_angle,
                color=aspect.color_code,
                segment_name=aspect.name,
                segment_id=aspect_code,
                segment_url=aspect.url
            )
    
            facet_start_angle = aspect_start_angle  # Facets start where the aspect starts
            angle_per_facet = aspect_angle / num_facets_in_aspect  # Equal angle for each facet
    
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
                    segment_url=facet.url
                )
                facet_start_angle += angle_per_facet
    
            aspect_start_angle += aspect_angle
    
        # Return the SVG markup
        return svg.get_svg_markup()

    def save_svg_to_file(self,svg_markup: str, filename: str):
        # Save the SVG content to a file
        with open(filename, 'w') as file:
            file.write(svg_markup)




