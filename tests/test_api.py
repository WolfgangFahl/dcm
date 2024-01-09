"""
Created on 2023-11-08

@author: wf
"""
from ngwidgets.webserver_test import WebserverTest

from dcm.dcm_cmd import CompetenceCmd
from dcm.dcm_core import CompetenceTree, DynamicCompetenceMap
from dcm.dcm_webserver import DynamicCompentenceMapWebServer
from dcm.svg import SVGConfig
from tests.markup_check import MarkupCheck


class TestAPI(WebserverTest):
    """
    test the dcm RESTFul API
    """

    def setUp(self, debug=False, profile=True):
        server_class = DynamicCompentenceMapWebServer
        cmd_class = CompetenceCmd
        WebserverTest.setUp(
            self,
            debug=debug,
            profile=profile,
            server_class=server_class,
            cmd_class=cmd_class,
        )
        self.example_definitions = {}
        for markup in ["json", "yaml"]:
            self.example_definitions[
                markup
            ] = DynamicCompetenceMap.get_example_dcm_definitions(
                markup=markup, required_keys=CompetenceTree.required_keys()
            )

    def test_svg_render(self):
        """
        test the rendering
        """
        path = "/svg"
        svg_config = SVGConfig(width=666, height=666)
        for markup, examples in self.example_definitions.items():
            for name, definition in examples.items():
                data = {
                    "name": name,
                    "definition": definition,
                    "markup": markup,
                    "config": svg_config.__dict__,
                }
                svg_markup = self.get_html_for_post(path, data)
                dcm = DynamicCompetenceMap.from_definition_string(
                    name, definition, content_class=CompetenceTree, markup=markup
                )
                markup_check = MarkupCheck(self, dcm)
                markup_check.check_markup(svg_content=svg_markup, svg_config=svg_config)

    def test_element_description(self):
        """
        Test the element description endpoint
        """
        example_name = "portfolio_plus"
        aspect_id = "PSS"
        facet_id = "enthusiasm"
        test_cases = [
            # Test case for a specific facet
            (
                f"/description/{example_name}/{aspect_id}/{facet_id}",
                ["Kompetenzanforderungen:", "<li>Freude"],
            ),
            # Test case for a whole aspect
            (
                f"/description/{example_name}/{aspect_id}",
                ["<h2>Professionelle Selbststeuerung</h2>"],
            ),
            # Test case for the whole tree
            (f"/description/{example_name}", ["<h2>PortfolioPlus</h2>"]),
        ]

        debug = self.debug
        # debug=True
        for path, expected_contents in test_cases:
            html = self.get_html(path)
            if debug:
                print(f"{path}:\n{html}")
            for expected_content in expected_contents:
                self.assertIn(expected_content, html)
