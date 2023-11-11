from typing import Optional
import xml.etree.ElementTree as ET
import unittest
from dcm.dcm_core import DynamicCompetenceMap
from dcm.svg import SVGConfig

class MarkupCheck:
    """
    This class provides methods to check the integrity of SVG markups based on given criteria
    from a Dynamic Competence Map (DCM).

    Attributes:
        test_case (unittest.TestCase): The instance of the test case using this class, 
                                       which provides access to the assert methods.
        dcm (DynamicCompetenceMap): An instance of the DynamicCompetenceMap containing the competence tree.
    """

    def __init__(self, test_case: unittest.TestCase, dcm: DynamicCompetenceMap):
        """
        Initialize the MarkupCheck with a test case instance and a DynamicCompetenceMap.

        Args:
            test_case (unittest.TestCase): An instance of the test case.
            dcm (DynamicCompetenceMap): An instance of the DynamicCompetenceMap.
        """
        self.test_case = test_case
        self.dcm = dcm

    def parse_svg(self, svg_content: Optional[str] = None, svg_file: Optional[str] = None) -> ET.Element:
        """
        Parse the SVG content from a string or file.

        Args:
            svg_content (str, optional): The SVG content as a text string.
            svg_file (str, optional): The file path of the SVG file to parse.

        Returns:
            ET.Element: The root element of the SVG content.

        Raises:
            ValueError: If neither svg_content nor svg_file is provided, or if both are provided.
        """
        if svg_content and svg_file:
            raise ValueError("Please provide either SVG content or file path, not both.")

        if svg_content:
            root = ET.fromstring(svg_content)
        elif svg_file:
            tree = ET.parse(svg_file)
            root = tree.getroot()
        else:
            raise ValueError("No SVG content or file path provided.")

        self.test_case.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg', 
                                   "The root element of the SVG is not 'svg'.")
        return root

    def check_svg_root(self, svg_file: str) -> ET.Element:
        """
        Check that the SVG root element is correct.

        Args:
            svg_file (str): The file path of the SVG file to parse.

        Returns:
            ET.Element: The root element of the SVG file.
        """
        tree = ET.parse(svg_file)
        root = tree.getroot()

        self.test_case.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg', 
                                   "The root element of the SVG is not 'svg'.")
        return root

    def check_svg_elements(self, root: ET.Element) -> None:
        """
        Check SVG elements against the competence aspects in the DCM.

        Args:
            root (ET.Element): The root element of the SVG file.
        """
        namespaces = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

        for aspect_id, aspect in self.dcm.competence_tree.competence_aspects.items():
            # ignore aspects without facets ..
            if len(aspect.facets)==0:
                continue
            element = root.find(f"svg:g[@id='{aspect_id}']", namespaces=namespaces)
            self.test_case.assertIsNotNone(element, f"Aspect with ID '{aspect_id}' not found in SVG.")

            link = element.find("svg:a", namespaces=namespaces)
            if aspect.url:
                self.test_case.assertIsNotNone(link, f"Link element for aspect with ID '{aspect_id}' not found in SVG.")
                self.test_case.assertEqual(link.get('{http://www.w3.org/1999/xlink}href'), aspect.url,
                                           f"URL for aspect with ID '{aspect_id}' is incorrect.")

    def check_svg_titles(self, root: ET.Element) -> None:
        """
        Optionally check for the presence of titles within the SVG.

        Args:
            root (ET.Element): The root element of the SVG file.
        """
        titles = root.findall(".//{{http://www.w3.org/2000/svg}}title")
        for title in titles:
            self.test_case.assertIn(title.text, [aspect.name for aspect in self.dcm.competence_tree.competence_aspects.values()],
                                    "A title element has an unexpected text.")
    
    def check_svg_config(self, root: ET.Element, expected_config: Optional[SVGConfig] = None) -> None:
        """
        Check if the SVG root has the correct width and height as specified in the SVGConfig.

        Args:
            root (ET.Element): The root element of the SVG content.
            expected_config (SVGConfig, optional): The expected SVG configuration.
        """
        if expected_config:
            # Check if the 'width' and 'height' of the SVG match the expected configuration
            svg_width = root.get('width')
            svg_height = root.get('height')
            self.test_case.assertEqual(svg_width, str(expected_config.width),
                                       f"SVG width is {svg_width} but expected {expected_config.width}")
            self.test_case.assertEqual(svg_height, str(expected_config.total_height),
                                       f"SVG height is {svg_height} but expected {expected_config.height}")

    def check_markup(self, svg_content: Optional[str] = None, svg_file: Optional[str] = None,
                 svg_config: Optional[SVGConfig] = None) -> None:
        """
        Conduct all checks on the SVG content, including configuration checks.

        Args:
            svg_content (str, optional): The SVG content as a text string.
            svg_file (str, optional): The file path of the SVG file to parse.
            svg_config (SVGConfig, optional): The expected SVG configuration.
        """
        root = self.parse_svg(svg_content=svg_content, svg_file=svg_file)
        self.check_svg_elements(root)
        self.check_svg_titles(root)
        self.check_svg_config(root, svg_config)  # Include the config check