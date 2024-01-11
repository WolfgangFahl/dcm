"""
Created on 2023-11-06

@author: wf
"""
from ngwidgets.basetest import Basetest

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
        for markup in ["json", "yaml"]:
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
        example_name = "portfolio_plus"
        aspect_id = "PSS"
        facet_id = "enthusiasm"
        self.assertTrue(example_name in examples)
        example = examples[example_name]
        facet = example.lookup(aspect_id, facet_id)
        self.assertIsNotNone(facet)
        html = facet.as_html()
        debug = self.debug
        # debug=True
        if debug:
            print(html)
        self.assertIn("Kompetenzanforderungen:", html)
        self.assertIn("<li>Freude", html)

    def test_learner_examples(self):
        """
        test the Learner markup handling
        """
        _learner = Learner(learner_id="test_id")
        learner_examples = DynamicCompetenceMap.get_examples(content_class=Learner)
        self.assertEqual(1, len(learner_examples))
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

    def testCompetenceMap(self):
        """
        test the competence map
        """
        for markup, examples in self.example_definitions.items():

            for example_name, dcm in examples.items():
                # Now you can perform assertions to verify that the data was loaded correctly
                self.assertIsNotNone(dcm.competence_tree)
                svg_config = SVGConfig()
                svg_config.legend_height = 40 * len(
                    dcm.competence_tree.competence_levels
                )
                svg_file = f"/tmp/{example_name}_competence_map_{markup}.svg"
                dcm.generate_svg(svg_file, config=svg_config)
                markup_check = MarkupCheck(self, dcm)
                markup_check.check_markup(svg_file=svg_file, svg_config=svg_config)
