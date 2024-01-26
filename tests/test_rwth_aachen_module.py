"""
Created on 2023-11-11

@author: wf
"""
import json
import os
from colour import Color
from ngwidgets.basetest import Basetest

from dcm.dcm_core import (
    CompetenceArea,
    CompetenceAspect,
    CompetenceElement,
    CompetenceFacet,
    CompetenceLevel,
    CompetenceTree,
    DynamicCompetenceMap,
    RingSpec
)


class TestModule(Basetest):
    """
    test RWTH Aachen Modulhandbuch
    """

    def get_name(self, json_node: dict, lang: str = "en") -> str:
        """
        Retrieves the name of a specified JSON node in the specified language.

        Args:
            json_node (dict): The JSON node from which the name is to be extracted.
            lang (str, optional): The language in which the name should be retrieved. Defaults to "en" (English).

        Returns:
            str: The name of the JSON node in the specified language. The result might be german (de) if
            there is only a single name specified in the Modulhandbuch XML input which is germany by default
        """

        names = json_node.get("NAME", [])
        name = "?"
        if isinstance(names, list):
            for lang_name in names:
                if isinstance(lang_name, dict):
                    node_lang = lang_name.get("@LANG", None)
                    if node_lang and node_lang == lang:
                        name = lang_name.get("#text", "?")
        else:
            # what's up here?
            # might be german now ..
            name = names["#text"]
            pass
        return name

    def create_competence_element(
        self, parent: CompetenceElement, json_node: dict, url: str
    ):
        """
        convert the given json node to a competence element based on the level
        1: CompetenceTree
        2: CompetenceAspect
        3: CompetenceFacet

        Args:
            parent(CompetenceElement): the parent element - None for the tree
            json_node(dict): the current node to convert
            url(str): the base_url for the node
        """
        competence_element = None
        lvl = json_node.get("@LVL", "?")
        credits_str = json_node.get("@CREDITS", None)
        credits = int(credits_str) if credits_str else None
        level = int(lvl)
        nr = json_node.get("@NR")
        desc = None
        name = self.get_name(json_node)
        if lvl == "1":
            tree = CompetenceTree(
                name=name, id=nr, url=url, description=desc, color_code=None
            )
            competence_element = tree
        elif lvl == "2":
            # Level 2 - CompetenceAspects
            aspect = CompetenceAspect(name=name, id=nr, url=url, credits=credits)
            parent.aspects.append(aspect)
            competence_element = aspect
        elif lvl == "3":
            # Level 3 - CompetenceAreas
            area = CompetenceArea(name=name, id=nr, url=url)
            parent.areas.append(area)
            competence_element = area
        if level < 3:
            for subnode in json_node["STP_KNOTEN"]:
                if isinstance(subnode, dict):
                    self.create_competence_element(competence_element, subnode, url)
                else:
                    # what's up here?
                    pass
        return competence_element

    def create_competence_tree(self, json_node: dict, url: str):
        """
        convert the given json_node to a Competence Tree

        Args:
            json_node(dict): the root node
            url(str): the base url to use
        """
        tree = self.create_competence_element(parent=None, json_node=json_node, url=url)
        tree.levels = [
            CompetenceLevel(name="1,0 - ≥95%", level=11),
            CompetenceLevel(name="1,3 - ≥90%", level=10),
            CompetenceLevel(name="1,7 - ≥85%", level=9),
            CompetenceLevel(name="2,0 - ≥80%", level=8),
            CompetenceLevel(name="2,3 - ≥75%", level=7),
            CompetenceLevel(name="2,7 - ≥70%", level=6),
            CompetenceLevel(name="3,0 - ≥65%", level=5),
            CompetenceLevel(name="3,3 - ≥60%", level=4),
            CompetenceLevel(name="3,7 - ≥55%", level=3),
            CompetenceLevel(name="4,0 - ≥50%", level=2),
            CompetenceLevel(name=" ❌ - <50%", level=1,color_code="#FF0000"),
        ]
        orange=Color("orange")
        green=Color("green")
        for ci,color in enumerate(green.range_to(orange, 10)):
            print (f"{ci}:{color}")
            tree.levels[ci].color_code=str(color)
        pass
        tree.element_names = {
            "tree": "Study plan",
            "aspect": "Study area",
            "area": "Module",
            "facet": "Module element",
            "level": "Grade",
        }

        return tree

    def test_master_informatik(self):
        """
        Modulhandbuch Master Informatik 2023 RWTH Aachen
        """
        file_name = "MHBXMLRAW_Master_1_Fach_Informatik_2023.json"
        url = "https://sc.informatik.rwth-aachen.de/de/studium/master/informatik/"
        description="RWTH Aachen Master Informatik"
        short_name="RWTH Master CS"
        home_dir = os.path.expanduser("~")
        base_path = os.path.join(home_dir, ".dcm/rwth_aachen/")
        file_path = f"{base_path}/{file_name}"
        if os.path.isfile(file_path):
            # Load the JSON data
            with open(file_path, "r") as file:
                mh_data = json.load(file)
            self.assertTrue("MODULHANDBUCH" in mh_data)
            # Adjust the path to the array based on your actual JSON structure
            competence_elements = mh_data["MODULHANDBUCH"]["STRUKTUR"]["STP_KNOTEN"]

            # Create the competence tree
            competence_tree = self.create_competence_tree(competence_elements, url=url)
            competence_tree.description=description
            competence_tree.short_name=short_name
            competence_tree.update_paths()
            competence_tree.ring_specs = {
                "tree": RingSpec(
                    inner_ratio=0.0, 
                    outer_ratio=1 / 10, 
                    text_mode="horizontal"
                ),
                "aspect": RingSpec(
                    text_mode="curved", 
                    inner_ratio=1 / 10, 
                    outer_ratio=3 / 10
                ),
                "area": RingSpec(
                    text_mode="angled",
                    inner_ratio=3/10, 
                    outer_ratio=10/10),
                "facet": RingSpec(
                    inner_ratio=0.0, 
                    outer_ratio=0.0
                ),
            }
        
            # Pretty print the JSON with specified indentation
            # pretty_json = competence_tree.to_pretty_json()
            yaml_str = competence_tree.to_yaml()
            debug = self.debug
            debug = True
            if debug:
                print(yaml_str)
            with open("/tmp/rwth_aachen_master_informatik.yaml", "w") as yaml_file:
                yaml_file.write(yaml_str)
            dcm = DynamicCompetenceMap.from_definition_string(
                name="RWTH Aachen Master Informatik",
                definition_string=yaml_str,
                content_class=CompetenceTree,
                markup="yaml",
                debug=debug,
            )
            self.assertIsNotNone(dcm)
