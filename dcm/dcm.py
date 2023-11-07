"""
Created on 2023-06-11

@author: wf
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from dataclasses_json import dataclass_json
from dcm.svg import SVG

@dataclass_json
@dataclass
class CompetenceAspect:
    full_name: str
    color_code: str
    facets: List[str]
    url: Optional[str] = None  # Optional URL attribute


@dataclass_json
@dataclass
class CompetenceTree:
    competence_aspects: Dict[str, CompetenceAspect]
    competence_levels: List[str]

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
    def from_json(json_string: str) -> 'DynamicCompetenceMap':
        """
        Load a DynamicCompetenceMap instance from a JSON string.
        """
        competence_tree = CompetenceTree.from_json(json_string)
        return DynamicCompetenceMap(competence_tree)

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
                aspect_name=aspect.full_name,
                aspect_id=aspect_code,
                aspect_url=aspect.url  # This is optional and can be omitted
            )
            
            # Increment the start angle for the next slice
            start_angle += angle
        
        # Save the SVG content to a file
        svg.save(filename)
