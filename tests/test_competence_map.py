'''
Created on 2023-11-06

@author: wf
'''
from ngwidgets.basetest import Basetest
from dcm.dcm_core import DynamicCompetenceMap
import os
import xml.etree.ElementTree as ET

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
            
            # Check that the SVG file was created
            self.assertTrue(os.path.isfile(svg_file), f"SVG file {svg_file} does not exist.")

            # Parse the SVG file and verify its contents
            tree = ET.parse(svg_file)
            root = tree.getroot()

            # Check that the SVG root element is correct
            self.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg', "The root element of the SVG is not 'svg'.")

            namespaces = {
                'svg': 'http://www.w3.org/2000/svg',
                'xlink': 'http://www.w3.org/1999/xlink'
            }
            
            for aspect_id, aspect in dcm.competence_tree.competence_aspects.items():
                # Find the group element by aspect ID using the SVG namespace
                element = root.find(f"svg:g[@id='{aspect_id}']", namespaces=namespaces)
                self.assertIsNotNone(element, f"Aspect with ID '{aspect_id}' not found in SVG.")
                
                # Find the <a> element within the group using the SVG and xlink namespaces
                link = element.find("svg:a", namespaces=namespaces)
                
                # If the aspect should have a URL, check that the <a> element exists and has the correct href attribute
                if aspect.url:
                    self.assertIsNotNone(link, f"Link element for aspect with ID '{aspect_id}' not found in SVG.")
                    self.assertEqual(link.get('{http://www.w3.org/1999/xlink}href'), aspect.url, f"URL for aspect with ID '{aspect_id}' is incorrect.")
                
                # Optionally, check for the presence of titles within the SVG
                titles = root.findall(".//{{http://www.w3.org/2000/svg}}title")
                for title in titles:
                    self.assertIn(title.text, [aspect.name for aspect in dcm.competence_tree.competence_aspects.values()],
                                  "A title element has an unexpected text.")