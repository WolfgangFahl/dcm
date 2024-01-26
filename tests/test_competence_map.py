"""
Created on 2023-11-06

@author: wf
"""
import os

from ngwidgets.basetest import Basetest

from dcm.dcm_chart import DcmChart
from dcm.dcm_core import (
    Achievement,
    CompetenceAspect,
    CompetenceElement,
    CompetenceFacet,
    CompetenceTree,
    DynamicCompetenceMap,
    Learner,
)
from dcm.svg import SVGConfig
from tests.markup_check import MarkupCheck


class TestDynamicCompetenceMap(Basetest):
    """
    test the dynamic competence map
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.example_definitions = {}
        for markup in ["yaml"]:
            self.example_definitions[markup] = DynamicCompetenceMap.get_examples(
                CompetenceTree, markup
            )

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
        self.assertEqual(element.color_code, aspect.color_code)  # Output: "#C0C0C0"
        self.assertEqual(element.color_code, facet.color_code)  # Output: "#C0C0C0"

    def test_element_lookup(self):
        """
        test looking up an element
        """
        examples = DynamicCompetenceMap.get_examples(markup="yaml")
        example_name = "greta_v2_0_1"
        self.assertTrue(example_name in examples)
        example = examples[example_name]
        path = f"{example_name}/ProfessionelleSelbststeuerung/MotivationaleOrientierungen/Enthusiasmus"
        ct = example.competence_tree
        self.assertEqual(4, ct.total_valid_levels)
        facet = ct.lookup_by_path(path)
        self.assertIsNotNone(facet)
        self.assertIsInstance(facet, CompetenceFacet)
        html = facet.as_html()
        debug = self.debug
        # debug=True
        if debug:
            print(html)
        self.assertIn("Kompetenzanforderungen", html)
        self.assertIn("<li>Freude", html)

    def test_learner_examples(self):
        """
        test the Learner markup handling
        """
        _learner = Learner(learner_id="test_id")
        learner_examples = DynamicCompetenceMap.get_examples(content_class=Learner)
        self.assertEqual(2, len(learner_examples))
        for learner_example in learner_examples.values():
            self.assertIsInstance(learner_example, Learner)
            self.assertTrue(len(learner_example.achievements) > 0)
            self.assertIsInstance(learner_example.achievements[0], Achievement)
        pass

    def test_convert_to_yaml(self):
        """
        test json to yaml conversion
        """
        debug = self.debug
        # debug = True
        for markup in ["json"]:
            json_definitions = DynamicCompetenceMap.get_examples(CompetenceTree, markup)
        for _def_id, definition in json_definitions.items():
            ct = definition.competence_tree
            yaml_str = ct.to_yaml()
            if debug:
                print(yaml_str)
            self.assertTrue("competence_levels:" in yaml_str)
            pass

    def test_path(self):
        """
        test that the path properties are available
        """
        debug = self.debug
        debug = True
        for _markup, examples in self.example_definitions.items():
            for _example_name, dcm in examples.items():
                ct = dcm.competence_tree
                if debug:
                    print(f"competence_tree: {ct.id}:{ct.path}")
                    print(ct.total_elements)
                self.assertEqual(ct.id, ct.path)
                for aspect in ct.aspects:
                    if debug:
                        print(f"aspect: {aspect.id}:{aspect.path}")
                    self.assertTrue(ct.id in aspect.path)
                    for area in aspect.areas:
                        if debug:
                            print(f"area: {area.id}:{area.path}")
                        self.assertTrue(aspect.path in area.path)
                        for facet in area.facets:
                            if debug:
                                print(f"facet: {facet.id}:{facet.path}")
                            self.assertTrue(area.path in facet.path)

    def testCompetenceMap(self):
        """
        test the competence map
        """
        for markup, examples in self.example_definitions.items():

            for example_name, dcm in examples.items():
                # Now you can perform assertions to verify that the data was loaded correctly
                self.assertIsNotNone(dcm.competence_tree)
                svg_config = SVGConfig(with_popup=True)
                svg_config.legend_height = 40 * len(dcm.competence_tree.levels)
                svg_path = "/tmp/dcm-test"
                os.makedirs(svg_path, exist_ok=True)
                for text_mode in ["curved", "horizontal", "angled", "empty"]:
                    svg_file = f"{svg_path}/{example_name}_competence_map_{markup}_{text_mode}.svg"
                    dcm_chart = DcmChart(dcm)
                    dcm_chart.generate_svg(
                        svg_file, config=svg_config, text_mode=text_mode
                    )
                    markup_check = MarkupCheck(self, dcm)
                    markup_check.check_markup(svg_file=svg_file, svg_config=svg_config)
