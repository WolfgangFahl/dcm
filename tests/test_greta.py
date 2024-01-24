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

        greta_short_names = {
            "greta_v2_0": "GRETA",
            "greta_v2_0/BerufspraktischesWissenUndKoennen": "Berufsprak",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik": "DidaktMethodik",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/GRETA-1-1-1": "DM-Lernziele",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/GRETA-1-1-2": "DM-Methoden",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/GRETA-1-1-3": "DM-Rahmenbedingungen",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/GRETA-1-1-4": "DM-Outcome",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/BeratungIndividualisierteLernunterstuetzung": "Beratung",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/BeratungIndividualisierteLernunterstuetzung/GRETA-1-2-1": "Beratung-Orientierung",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/BeratungIndividualisierteLernunterstuetzung/GRETA-1-2-2": "Beratung-Diagnostik",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/KommunikationUndInteraktion": "KommInterakt",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/KommunikationUndInteraktion/GRETA-1-3-1": "KI-Gruppen",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/KommunikationUndInteraktion/GRETA-1-3-2": "KI-Kommunikation",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/Organistion": "Organisation",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/Organistion/GRETA-1-4-1": "Org-Auftraggeber",
            "greta_v2_0/BerufspraktischesWissenUndKoennen/Organistion/GRETA-1-4-2": "Org-Netzwerke",
            "greta_v2_0/FachUndFeldspezifischesWissen": "FachFeldWissen",
            "greta_v2_0/FachUndFeldspezifischesWissen/Feldbezug": "Feldbezug",
            "greta_v2_0/FachUndFeldspezifischesWissen/Feldbezug/GRETA-2-1-1": "FB-Adressaten",
            "greta_v2_0/FachUndFeldspezifischesWissen/Feldbezug/GRETA-2-1-2": "FB-Feldwissen",
            "greta_v2_0/FachUndFeldspezifischesWissen/Feldbezug/GRETA-2-1-3": "FB-Curricula",
            "greta_v2_0/ProfessionelleWerthaltungenUndUeberzeugungen": "Werthaltungen",
            "greta_v2_0/ProfessionelleWerthaltungenUndUeberzeugungen/Berufsethos": "Berufsethos",
            "greta_v2_0/ProfessionelleWerthaltungenUndUeberzeugungen/Berufsethos/GRETA-3-1-1": "BE-Menschenbild",
            "greta_v2_0/ProfessionelleWerthaltungenUndUeberzeugungen/Berufsethos/GRETA-3-1-2": "BE-Wertvorstellungen",
            "greta_v2_0/ProfessionelleWerthaltungenUndUeberzeugungen/BerufsbezogeneUeberzeugungen": "Berufsueberzeugungen",
            "greta_v2_0/ProfessionelleWerthaltungenUndUeberzeugungen/BerufsbezogeneUeberzeugungen/GRETA-3-2-1": "BU-Rollenbewusstsein",
            "greta_v2_0/ProfessionelleWerthaltungenUndUeberzeugungen/BerufsbezogeneUeberzeugungen/GRETA-3-2-2": "BU-Lehrannahmen",
            "greta_v2_0/ProfessionelleSelbststeuerung": "Selbststeuerung",
            "greta_v2_0/ProfessionelleSelbststeuerung/MotivationaleOrientierungen": "MotOrient",
            "greta_v2_0/ProfessionelleSelbststeuerung/MotivationaleOrientierungen/GRETA-4-1-1": "MO-Selbstwirksamkeit",
            "greta_v2_0/ProfessionelleSelbststeuerung/MotivationaleOrientierungen/GRETA-4-1-2": "MO-Enthusiasmus",
            "greta_v2_0/ProfessionelleSelbststeuerung/Selbstregulation": "Selbstregul",
            "greta_v2_0/ProfessionelleSelbststeuerung/Selbstregulation/GRETA-4-2-1": "SR-Feedback",
            "greta_v2_0/ProfessionelleSelbststeuerung/Selbstregulation/GRETA-4-2-2": "SR-Engagement",
            "greta_v2_0/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung": "BerufspraktErf",
            "greta_v2_0/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung/GRETA-4-3-1": "BE-Reflexion",
            "greta_v2_0/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung/GRETA-4-3-2": "BE-Weiterentwicklung",
        }

        km = greta_data["Kompetenzmodell"]
        ct = CompetenceTree(
            name="GRETA",
            id=km["ID"],
            description=km["Name"],
            url="https://www.greta-die.de/webpages/greta-interaktiv",
            stacked_levels=True,
        )
        ct.element_names = {
            "tree": "Kompetenzbilanz",
            "aspect": "Kompetenzaspekt",
            "area": "Kompetenzbereich",
            "facet": "Kompetenzfacette",
            "level": "Lernfortschritt",
        }
        ct.relative_radius = {
            "tree": (0.0, 1/9),
            "aspect": (0.0, 0.0),
            "area": (0.0, 0.0),
            "facet": (1 / 9, 9 / 9),
        }
        # Define color codes for competence levels
        level_color_codes = {
            0: "#888888",  # Grey for level 0
            1: "#ECEABE",  # Light Green for areas 1
            2: "#C8D575",  # Olive Green for level 2
            3: "#AEBF3F",  # Medium Green for level 3
            4: "#7D8A2C",  # Dark Green for level 4
        }
        # Define the color codes for areas:
        aspect_color_codes = ["#868378", "#aba89e", "#c9c7c0", "#e8e6e1"]

        # Define icons for competence levels (replace with actual icon names)
        utf8_icons = {0: "❓", 1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐"}
        for level in range(len(utf8_icons)):
            cl = CompetenceLevel(
                name=f"Level{level}",
                level=level,
                utf8_icon=utf8_icons[level],
                color_code=level_color_codes[level],
            )
            ct.levels.append(cl)

        for a_index, g_aspect in enumerate(km["Kompetenzaspekte"]):
            aspect = CompetenceAspect(
                id=g_aspect["ID"],
                name=g_aspect["Name"],
                color_code=aspect_color_codes[a_index],
            )
            ct.aspects.append(aspect)
            for g_index, g_area in enumerate(g_aspect["Kompetenzbereiche"]):
                if self.debug:
                    print(json.dumps(g_area, indent=2))
                area = CompetenceArea(
                    id=g_area["ID"],
                    name=g_area["Name"],
                )
                aspect.areas.append(area)
                for f_index, g_facet in enumerate(g_area["Kompetenzfacetten"]):
                    description = """**Kompetenzanforderungen**:\n\n"""
                    for req in g_facet["Kompetenzanforderungen"]:
                        description += f"- {req}\n"
                    pass
                    facet = CompetenceFacet(
                        id=g_facet["ID"], name=g_facet["Name"], description=description
                    )

                    area.facets.append(facet)
        ct.update_paths()
        for path, element in ct.elements_by_path.items():
            element.short_name = greta_short_names[path]
        yaml_str = ct.to_yaml()
        if self.debug:
            print(yaml_str)
        with open("/tmp/greta.yaml", "w") as yaml_file:
            yaml_file.write(yaml_str)
