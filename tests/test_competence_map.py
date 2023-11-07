'''
Created on 2023-11-06

@author: wf
'''
from ngwidgets.basetest import Basetest
from dcm.dcm import DynamicCompetenceMap

class TestDynamicCompetenceMap(Basetest):
    """
    test the dynamic competence map
    """
    
    def testCompetenceMap(self):
        """
        test the competence map
        """
        competence_tree_json="""{
  "competence_aspects": {
    "BPWK": {
      "full_name": "Berufspraktisches Wissen und Können",
      "color_code": "#B5B0A8",
      "facets": [
        "Lerninhalte und -ziele",
        "Methoden, Medien und Lernmaterialien",
        "Rahmenbedingungen und Lernumgebungen",
        "Outcomeorientierung",
        "Teilnehmendenorientierung",
        "Diagnostik und Lernberatung",
        "Moderation und Steuerung von Gruppen",
        "Professionelle Kommunikation",
        "Kooperation mit den Auftraggebenden/Arbeitgebenden",
        "Kollegiale Zusammenarbeit/Netzwerken"
      ]
    },
    "FFW": {
      "full_name": "Fach- und feldspezifisches Wissen",
      "color_code": "#D1CFC7",
      "facets": [
        "Adressatinnen und Adressaten",
        "Feldspezifisches Wissen",
        "Curriculare und institutionelle Rahmenbedingungen"
      ]
    },
    "PWAU": {
      "full_name": "Professionelle Werthaltungen und Überzeugungen",
      "color_code": "#EBE8E5",
      "facets": [
        "Menschenbilder",
        "Wertvorstellungen",
        "Berufliche Weiterentwicklung",
        "Subjektive Annahmen über das Lehren und Lernen"
      ]
    },
    "PSS": {
      "full_name": "Professionelle Selbststeuerung",
      "color_code": "#918F82",
      "facets": [
        "Selbstwirksamkeitsüberzeugungen",
        "Enthusiasmus",
        "Eigenes Rollenbewusstsein",
        "Reflexion des eigenen Lehrhandelns",
        "Umgang mit Feedback und Kritik",
        "Engagement und Distanz"
      ]
    }
  },
  "competence_levels": [
    "Basisstufe",
    "Ausbaustufe",
    "Nicht erfasst"
  ]
}
"""
        dcm = DynamicCompetenceMap.from_json(competence_tree_json)

        # Now you can perform assertions to verify that the data was loaded correctly
        self.assertIsNotNone(dcm.competence_tree)
        self.assertTrue("BPWK" in dcm.competence_tree.competence_aspects)
        svg_file="/tmp/competence_map.svg"
        dcm.generate_svg(svg_file)
        