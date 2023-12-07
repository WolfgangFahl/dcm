'''
Created on 2023-11-06

@author: wf
'''
from ngwidgets.basetest import Basetest
from dcm.dcm_core import DynamicCompetenceMap,CompetenceTree,CompetenceAspect,CompetenceElement,CompetenceFacet, Student
from tests.markup_check import MarkupCheck
from dcm.svg import SVGConfig

class TestDynamicCompetenceMap(Basetest):
    """
    test the dynamic competence map
    """
    
    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.example_definitions = {}
        for markup in ["json","yaml"]:
            self.example_definitions[markup] = DynamicCompetenceMap.get_examples(CompetenceTree, markup)
     
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
        
    def test_element_lookup(self):
        """
        test looking up an element
        """
        examples = DynamicCompetenceMap.get_examples(markup='yaml')
        example_name="portfolio_plus"
        aspect_id="PSS"
        facet_id="enthusiasm"
        self.assertTrue(example_name in examples)
        example=examples[example_name]
        facet=example.lookup(aspect_id,facet_id)
        self.assertIsNotNone(facet)
        html=facet.as_html()
        debug=self.debug
        #debug=True
        if debug:
            print(html)
        self.assertIn("Kompetenzanforderungen:",html)
        self.assertIn("<li>Freude",html)
        
    #def testStudent(self):
    #   """
    #   test the student json handling
    #   """
    #  student_examples=DynamicCompetenceMap.get_examples(content_class=Student)
        
    def testCompetenceMap(self):
        """
        test the competence map
        """
        for markup, examples in self.example_definitions.items():
       
            for example_name, dcm in examples.items():  
                # Now you can perform assertions to verify that the data was loaded correctly
                self.assertIsNotNone(dcm.competence_tree)
                svg_config=SVGConfig()
                svg_config.legend_height=40*len(dcm.competence_tree.competence_levels)
                svg_file=f"/tmp/{example_name}_competence_map_{markup}.svg"
                dcm.generate_svg(svg_file,config=svg_config)
                markup_check=MarkupCheck(self,dcm)
                markup_check.check_markup(svg_file=svg_file,svg_config=svg_config) 