"""
Created on 2023-06-11

@author: wf
"""
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

    def generate_svg(self, filename: str):
        competence_aspects = self.competence_tree.competence_aspects
        
        # Instantiate the SVG class
        svg = SVG(width=300, height=300)
        
        # Center of the pie
        cx, cy = svg.width // 2, svg.height // 2
        radius = min(cx, cy) * 0.9  # Radius of the pie

        # Calculate total number of facets
        total_facets = sum(len(aspect.facets) for aspect in competence_aspects.values())
        
        # Starting angle for the first slice
        start_angle = 0
        
        # Create the slices of the pie chart
        for aspect_code, aspect in competence_aspects.items():
            # Calculate the angle for this slice in degrees
            num_facets = len(aspect.facets)
            angle = (num_facets / total_facets) * 360  # Angle in degrees
            
            # Add the pie segment to the SVG
            svg.add_pie_segment(
                cx=150,
                cy=150,
                radius=135,
                start_angle_deg=start_angle,
                end_angle_deg=start_angle + angle,
                color=aspect.color_code,
                aspect_description=aspect.description,
                aspect_id=aspect_code,
                aspect_url=aspect.url  # This is optional and can be omitted
            )
            
            # Increment the start angle for the next slice
            start_angle += angle
        
        # Save the SVG content to a file
        svg.save(filename)
