'''
Created on 2023-11-11

@author: wf
'''
import json
import os
from ngwidgets.basetest import Basetest
from dcm.dcm_core import CompetenceTree, CompetenceAspect, CompetenceFacet, CompetenceElement

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

        names=json_node.get("NAME",[])
        name="?"
        if isinstance(names,list):
            for lang_name in names:
                if isinstance(lang_name,dict):
                    node_lang=lang_name.get("@LANG",None)
                    if node_lang and node_lang==lang:
                        name=lang_name.get("#text","?")
        else:
            # what's up here?
            # might be german now ..
            name=names["#text"]
            pass
        return name
      
    def create_competence_element(self,parent:CompetenceElement,json_node:dict,url:str):
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
        competence_element=None
        lvl = json_node.get("@LVL","?")
        credits_str =json_node.get("@CREDITS",None)
        credits=int(credits_str) if credits_str else None
        level = int(lvl)
        nr = json_node.get("@NR")
        desc=None
        name=self.get_name(json_node)
        if lvl=="1":
            tree = CompetenceTree(
                name=name,  
                id=nr,
                url=url,
                description=desc,
                color_code=None  
            ) 
            competence_element=tree
        elif lvl == "2":
            # Level 2 - CompetenceAspects
            aspect = CompetenceAspect(name=name, id=nr,url=url,credits=credits)
            parent.competence_aspects[name] = aspect
            competence_element=aspect
        elif lvl == "3":
            # Level 3 - CompetenceFacets
            facet = CompetenceFacet(name=name, id=nr, url=url)
            parent.facets.append(facet)
            competence_element=facet
        if level<3:
            for subnode in json_node["STP_KNOTEN"]:
                if isinstance(subnode,dict):
                    self.create_competence_element(competence_element, subnode, url)
                else:
                    # what's up here?
                    pass
        return competence_element
    
    def create_competence_tree(self,json_node:dict,url:str):
        """
        convert the given json_node to a Competence Tree
        
        Args:
            json_node(dict): the root node 
            url(str): the base url to use
        """
        tree=self.create_competence_element(parent=None,json_node=json_node, url=url)
        return tree
    
    def test_master_informatik(self):
        """
        Modulhandbuch Master Informatik 2023 RWTH Aachen
        """
        file_name="MHBXMLRAW_Master_1_Fach_Informatik_2023.json"
        url="https://sc.informatik.rwth-aachen.de/de/studium/master/informatik/"
        home_dir = os.path.expanduser("~")
        base_path = os.path.join(home_dir, ".dcm/rwth_aachen/")
        file_path=f"{base_path}/{file_name}"
        if os.path.isfile(file_path):
            #Load the JSON data
            with open(file_path, 'r') as file:
                mh_data = json.load(file)
            self.assertTrue("MODULHANDBUCH" in mh_data)
            # Adjust the path to the array based on your actual JSON structure
            competence_elements = mh_data['MODULHANDBUCH']['STRUKTUR']['STP_KNOTEN']

            # Create the competence tree
            competence_tree = self.create_competence_tree(competence_elements,url=url)
            # Pretty print the JSON with specified indentation
            pretty_json = competence_tree.to_pretty_json()
            debug=self.debug
            #debug=True
            if debug:
                print(pretty_json)