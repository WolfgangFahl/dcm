"""
Created on  2024-01-20

@author: wf
"""
import json
import os

from linkml_runtime.dumpers.rdf_dumper import RDFDumper
from linkml_runtime.loaders.json_loader import JSONLoader
from ngwidgets.basetest import Basetest
from rdflib import Graph

# from dcm.dcm_core import Learner
from dcm.linkml.dcm_model import Learner


class TestTriplify(Basetest):
    """
    test triplifying the dcm core classes
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        # Path to the JSON file
        scriptdir = os.path.dirname(__file__)
        topdir = os.path.dirname(scriptdir)
        self.json_file_path = os.path.join(topdir, "dcm_examples/arch_student_123.json")
        self.linkml_map_path = os.path.join(topdir, "dcm/linkml/dcm_schema.yaml")
        self.json_ld_context = os.path.join(topdir, "dcm/linkml/dcm.context.jsonld")

    def getLearner(self) -> Learner:
        # Read the JSON file as a dict
        with open(self.json_file_path, "r") as file:
            json_data = json.load(file)

        # Load JSON data into a Learner instance
        json_loader = JSONLoader()
        json_data["@type"] = "Learner"
        learner = json_loader.load(json_data, Learner)

        return learner

    def testLearner(self):
        """
        test the learner example
        """
        learner = self.getLearner()
        self.assertIsInstance(learner, Learner)
        pass

        # Serialize Learner instance to RDF
        rdf_dumper = RDFDumper()

        g = rdf_dumper.as_rdf_graph(learner, self.json_ld_context)
        debug = self.debug
        debug = True
        if debug:
            # Serialize the graph to a string in Turtle format for inspection
            rdf_str = g.serialize(format="turtle")
            print(rdf_str)
        for subj, pred, obj in g:
            print(f"Subject: {subj}, Predicate: {pred}, Object: {obj}")

        # Your assertions to validate the RDF triples
        # For example, you could assert the number of triples or specific content
        assert len(g) > 0  # Example assertion: there should be at least one triple

        # use linkml and rdflib to convert to triples
        #
