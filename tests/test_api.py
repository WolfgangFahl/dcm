"""
Created on 2023-11-08

@author: wf
"""
from ngwidgets.webserver_test import WebserverTest
from dcm.dcm_webserver import DynamicCompentenceMapWebServer
from dcm.dcm_cmd import CompetenceCmd
from dcm.dcm_core import DynamicCompetenceMap, CompetenceTree
from tests.markup_check import MarkupCheck
from dcm.svg import SVGConfig

class TestAPI(WebserverTest):
    """
    test the dcm RESTFul API
    """
    
    def setUp(self, debug=False, profile=True):
        server_class=DynamicCompentenceMapWebServer
        cmd_class=CompetenceCmd
        WebserverTest.setUp(self, debug=debug, profile=profile,server_class=server_class,cmd_class=cmd_class)
        self.example_definitions = {}
        for markup in ["json","yaml"]:
            self.example_definitions[markup] = DynamicCompetenceMap.get_example_dcm_definitions(markup=markup,required_keys=CompetenceTree.required_keys())
       
    def test_svg_render(self):
        """
        test the rendering
        """
        path="/svg"
        svg_config=SVGConfig(width=666,height=666)
        for markup, examples in self.example_definitions.items():
            for name, definition in examples.items():
                data = {
                    "name": name,
                    "definition": definition,
                    "markup": markup,
                    "config": svg_config.__dict__ 
                }
                svg_markup = self.get_html_for_post(path, data)
                dcm = DynamicCompetenceMap.from_definition_string(name, definition, content_class=CompetenceTree, markup=markup)
                markup_check=MarkupCheck(self,dcm)
                markup_check.check_markup(svg_content=svg_markup,svg_config=svg_config)
                
    def test_aspect_description(self):
        """
        Test the aspect description endpoint
        """
        example_name = "portfolio_plus"  # Replace with an actual example name
        aspect_id = "Enthusiasmus"  # Example aspect ID for testing
        path = f"/description/{example_name}/{aspect_id}"
        
        response = self.get_html(path)
        # Here, we expect a specific content in the response.
        # This expected content will be based on what you intend to implement in the endpoint.
        expected_content = "Expected description for Enthusiasmus in example some_example"
        self.assertIn(expected_content, response)