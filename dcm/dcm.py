"""
Created on 2023-06-11

@author: wf
"""
from dataclasses import dataclass
from typing import Dict, List
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CompetenceAspect:
    full_name: str
    color_code: str
    facets: List[str]


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
