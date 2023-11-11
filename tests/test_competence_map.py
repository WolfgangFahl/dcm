'''
Created on 2023-11-06

@author: wf
'''
from ngwidgets.basetest import Basetest
from dcm.dcm_core import DynamicCompetenceMap,CompetenceAspect,CompetenceElement,CompetenceFacet
from tests.markup_check import MarkupCheck
from dcm.svg import SVGConfig

class TestDynamicCompetenceMap(Basetest):
    """
    test the dynamic competence map
    """
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.examples = DynamicCompetenceMap.get_examples()
  
    def testDefaultColor(self):
        """
        test the default Color
        """
        element = CompetenceElement(name="Element 1")
        aspect = CompetenceAspect(name="Aspect 1")
        facet = CompetenceFacet(name="Facet 1")
        
        # Printing the color_code attribute for each instance
        if self.debug:
            print(f"default color code is: {element.color_code}")  # Output: "#C0C0C0"
        self.assertEqual(element.color_code,aspect.color_code)   # Output: "#C0C0C0"
        self.assertEqual(element.color_code,facet.color_code)    # Output: "#C0C0C0"
        
    def testCompetenceMap(self):
        """
        test the competence map
        """
        for example_name, dcm in self.examples.items():   
            # Now you can perform assertions to verify that the data was loaded correctly
            self.assertIsNotNone(dcm.competence_tree)
            svg_config=SVGConfig()
            svg_config.legend_height=40*len(dcm.competence_tree.competence_levels)
            svg_file=f"/tmp/{example_name}_competence_map.svg"
            dcm.generate_svg(svg_file,config=svg_config)
            markup_check=MarkupCheck(self,dcm)
            markup_check.check_markup(svg_file=svg_file,svg_config=svg_config) 