'''
Created on 2023-11-06

@author: wf
'''
from ngwidgets.basetest import Basetest
from dcm.dcm import DynamicCompetenceMap
import os

class TestDynamicCompetenceMap(Basetest):
    """
    test the dynamic competence map
    """
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.resources_path = os.path.join(os.path.dirname(__file__), 'resources')
        self.competence_tree_examples = {}
        for filename in os.listdir(self.resources_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.resources_path, filename)
                with open(filepath, 'r') as json_file:
                    file_prefix=filename.replace(".json","")
                    self.competence_tree_examples[file_prefix] =json_file.read()
 
    def testCompetenceMap(self):
        """
        test the competence map
        """
        for example_name, competence_tree_json in self.competence_tree_examples.items():
            dcm = DynamicCompetenceMap.from_json(example_name,competence_tree_json)
    
            # Now you can perform assertions to verify that the data was loaded correctly
            self.assertIsNotNone(dcm.competence_tree)
            self.assertTrue(any(key in dcm.competence_tree.competence_aspects for key in ["BPWK", "DandP"]))
            
            svg_file=f"/tmp/{example_name}_competence_map.svg"
            dcm.generate_svg(svg_file)
        