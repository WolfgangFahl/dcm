'''
Created on 2023-11-06

@author: wf
'''
from ngwidgets.basetest import Basetest
from dcm.dcm_core import DynamicCompetenceMap
from tests.markup_check import MarkupCheck

class TestDynamicCompetenceMap(Basetest):
    """
    test the dynamic competence map
    """
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.examples = DynamicCompetenceMap.get_examples()
  
    def testCompetenceMap(self):
        """
        test the competence map
        """
        for example_name, dcm in self.examples.items():   
            # Now you can perform assertions to verify that the data was loaded correctly
            self.assertIsNotNone(dcm.competence_tree)
            self.assertTrue(any(key in dcm.competence_tree.competence_aspects for key in ["BPWK", "DandP"]))
            
            svg_file=f"/tmp/{example_name}_competence_map.svg"
            dcm.generate_svg(svg_file)
            markup_check=MarkupCheck(self,dcm)
            markup_check.check_markup(svg_file=svg_file) 