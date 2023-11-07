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

    def generate_svg(self, filename: str,width:int=600, height:int=600):
        competence_aspects = self.competence_tree.competence_aspects
        
        # Instantiate the SVG class
        svg = SVG(width=width, height=height)
        
        # Center of the pie
        cx, cy = svg.width // 2, svg.height // 2
        facet_radius = min(cx, cy) 
        aspect_radius=facet_radius//2 # smaller radius for aspects

        # Total number of facets
        total_facets = sum(len(aspect.facets) for aspect in competence_aspects.values())

        # Starting angle for the first aspect
        aspect_start_angle = 0

        for aspect_code, aspect in competence_aspects.items():
            num_facets_in_aspect = len(aspect.facets)
            aspect_angle = (num_facets_in_aspect / total_facets) * 360

            # Draw the aspect segment on top of the facets
            svg.add_pie_segment(
                cx=cx,
                cy=cy,
                radius=aspect_radius,
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
                # Add the facet segment to the SVG
                svg.add_pie_segment(
                    cx=cx,
                    cy=cy,
                    radius=facet_radius,  # Slightly larger radius for facets
                    start_angle_deg=facet_start_angle,
                    end_angle_deg=facet_start_angle + angle_per_facet,
                    color=facet.color_code,
                    segment_name=facet.name,
                    segment_id=facet.id,
                    segment_url=facet.url  # This is optional and can be omitted
                )
                facet_start_angle += angle_per_facet

            aspect_start_angle += aspect_angle

        # Save the SVG content to a file
        svg.save(filename)


