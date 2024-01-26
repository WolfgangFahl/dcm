"""
Created on 2024-01-24

@author: wf
"""
import json
import os

from ngwidgets.basetest import Basetest

from dcm.dcm_core import CompetenceTree
from dcm.xapi import XAPI


class TestxApi(Basetest):
    """
    test https://en.wikipedia.org/wiki/Experience_API xAPI
    statement handling
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.competence_tree = self.load_competence_tree()

    def load_competence_tree(self) -> CompetenceTree:
        # Define the path to the YAML file
        yaml_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "dcm_examples",
            "greta.yaml",
        )
        # Ensure the YAML file exists
        self.assertTrue(os.path.exists(yaml_file_path))
        # Load the CompetenceTree from the YAML file
        competence_tree = CompetenceTree.load_from_yaml_file(yaml_file_path)
        return competence_tree

    def get_xApi_example(self) -> XAPI:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Specify the relative path to the JSON file
        json_file_path = os.path.join(
            script_dir, "..", "greta", "greta_xapi_example1.json"
        )
        # Check if the JSON file exists
        self.assertTrue(os.path.exists(json_file_path))
        xapi = XAPI.from_json(json_file_path)
        return xapi

    def test_example(self):
        """
        def test the GRETA xAPI example
        """
        xapi = self.get_xApi_example()
        debug = self.debug
        # debug = True
        if debug:
            print(json.dumps(xapi.xapi_dict, indent=2))
        learner = xapi.to_learner(self.competence_tree)
        self.assertIsNotNone(learner)
        json_str = learner.to_json(indent=2)
        with open("/tmp/greta_learner_xapi_example1.json", "w") as json_file:
            json_file.write(json_str)
        if debug:
            print(json_str)
