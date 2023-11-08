"""
Created on 2023-11-08

@author: wf
"""
from ngwidgets.webserver_test import WebserverTest
from dcm.dcm_webserver import DynamiceCompentenceMapWebServer
from dcm.dcm_cmd import CompetenceCmd
from dcm.dcm_core import DynamicCompetenceMap
from tests.markup_check import MarkupCheck

class TestAPI(WebserverTest):
    """
    test the dcm RESTFul API
    """
    
    def setUp(self, debug=False, profile=True):
        server_class=DynamiceCompentenceMapWebServer
        cmd_class=CompetenceCmd
        WebserverTest.setUp(self, debug=debug, profile=profile,server_class=server_class,cmd_class=cmd_class)
        self.example_jsons = DynamicCompetenceMap.get_example_json_strings()
 
    def get_html_for_post(self,path:str,data)->str:
        """
        get the html content for the given path by posting the given data
        """
        response=self.client.post(path,json=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content is not None)
        html=response.content.decode()
        if self.debug:
            print(html)
        return html
    
    def test_svg_render(self):
        """
        test the rendering
        """
        path="/svg"
        #self.debug=True
        for name,json_string in self.example_jsons.items():
            data = {
                "name": name,
                "json_string": json_string
            }
            svg_markup=self.get_html_for_post(path, data)
            dcm=DynamicCompetenceMap.from_json(name, json_string)
            markup_check=MarkupCheck(self,dcm)
            markup_check.check_markup(svg_content=svg_markup)