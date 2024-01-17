"""
Created on 2024-01-15

@author: wf
"""
import json
import os

from ngwidgets.basetest import Basetest

from dcm.dcm_core import (
    CompetenceArea,
    CompetenceAspect,
    CompetenceFacet,
    CompetenceLevel,
    CompetenceTree,
)


class TestGreta(Basetest):
    """
    test converting the Greta competence Json Model to
    DCM yaml
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    def test_greta_json(self):
        """
        Read the Greta model from 'greta_kompetenzmodell_2-0.json'
        """
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Specify the relative path to the JSON file
        json_file_path = os.path.join(
            script_dir, "..", "greta", "greta_kompetenzmodell_2-0.json"
        )

        # Check if the JSON file exists
        self.assertTrue(os.path.exists(json_file_path))
        # Open and read the JSON file
        with open(json_file_path, "r") as json_file:
            greta_data = json.load(json_file)
        km = greta_data["Kompetenzmodell"]
        ct = CompetenceTree(
            name="GRETA",
            description=km["Name"],
            url="https://www.greta-die.de/webpages/greta-interaktiv",
        )
        ct.element_names = {
            "tree": "Kompetenzbilanz",
            "aspect": "Kompetenzaspekt",
            "area": "Kompetenzbereich",
            "facet": "Kompetenzfacette",
            "level": "Lernfortschritt",
        }
        # Define color codes for competence levels
        color_codes = {
            0: "#888888",  # Grey for level 0
            1: "#FF5733",  # Red for level 1
            2: "#FFAB33",  # Orange for level 2
            3: "#FFE333",  # Yellow for level 3
            4: "#33FF5B",  # Green for level 4
        }

        # Define icons for competence levels (replace with actual icon names)
        utf8_icons = {0: "❓", 1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐"}
        for level in range(5):
            cl = CompetenceLevel(
                name=f"Level{level}",
                level=level,
                utf8_icon=utf8_icons[level],
                color_code=color_codes[level],
            )
            ct.levels.append(cl)

        for a_index, g_aspect in enumerate(km["Kompetenzaspekte"]):
            aspect = CompetenceAspect(id=f"{a_index+1}", name=g_aspect["Name"])
            ct.aspects.append(aspect)
            for g_index, g_area in enumerate(g_aspect["Kompetenzbereiche"]):
                if self.debug:
                    print(json.dumps(g_area, indent=2))
                area = CompetenceArea(id=f"{g_index+1}", name=g_area["Name"])
                aspect.areas.append(area)
                for f_index, g_facet in enumerate(g_area["Kompetenzfacetten"]):
                    description = """**Kompetenzanforderungen**:\n\n"""
                    for req in g_facet["Kompetenzanforderungen"]:
                        description += f"- {req}\n"
                    pass
                    facet = CompetenceFacet(
                        id=f"{f_index+1}", name=g_facet["Name"], description=description
                    )

                    area.facets.append(facet)
        yaml_str = ct.to_yaml()
        if self.debug:
            print(yaml_str)
        with open("/tmp/greta.yaml", "w") as yaml_file:
            yaml_file.write(yaml_str)
