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
            "GRETA": "GRETA",
            "GRETA/BerufspraktischesWissenUndKoennen": "Berufsprak",
            "GRETA/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik": "DidaktMethodik",
            "GRETA/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/GRETA-1-1-1": "DM-Lernziele",
            "GRETA/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/GRETA-1-1-2": "DM-Methoden",
            "GRETA/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/GRETA-1-1-3": "DM-Rahmenbedingungen",
            "GRETA/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/GRETA-1-1-4": "DM-Outcome",
            "GRETA/BerufspraktischesWissenUndKoennen/BeratungIndividualisierteLernunterstuetzung": "Beratung",
            "GRETA/BerufspraktischesWissenUndKoennen/BeratungIndividualisierteLernunterstuetzung/GRETA-1-2-1": "Beratung-Orientierung",
            "GRETA/BerufspraktischesWissenUndKoennen/BeratungIndividualisierteLernunterstuetzung/GRETA-1-2-2": "Beratung-Diagnostik",
            "GRETA/BerufspraktischesWissenUndKoennen/KommunikationUndInteraktion": "KommInterakt",
            "GRETA/BerufspraktischesWissenUndKoennen/KommunikationUndInteraktion/GRETA-1-3-1": "KI-Gruppen",
            "GRETA/BerufspraktischesWissenUndKoennen/KommunikationUndInteraktion/GRETA-1-3-2": "KI-Kommunikation",
            "GRETA/BerufspraktischesWissenUndKoennen/Organistion": "Organisation",
            "GRETA/BerufspraktischesWissenUndKoennen/Organistion/GRETA-1-4-1": "Org-Auftraggeber",
            "GRETA/BerufspraktischesWissenUndKoennen/Organistion/GRETA-1-4-2": "Org-Netzwerke",
            "GRETA/FachUndFeldspezifischesWissen": "FachFeldWissen",
            "GRETA/FachUndFeldspezifischesWissen/Feldbezug": "Feldbezug",
            "GRETA/FachUndFeldspezifischesWissen/Feldbezug/GRETA-2-1-1": "FB-Adressaten",
            "GRETA/FachUndFeldspezifischesWissen/Feldbezug/GRETA-2-1-2": "FB-Feldwissen",
            "GRETA/FachUndFeldspezifischesWissen/Feldbezug/GRETA-2-1-3": "FB-Curricula",
            "GRETA/ProfessionelleWerthaltungenUndUeberzeugungen": "Werthaltungen",
            "GRETA/ProfessionelleWerthaltungenUndUeberzeugungen/Berufsethos": "Berufsethos",
            "GRETA/ProfessionelleWerthaltungenUndUeberzeugungen/Berufsethos/GRETA-3-1-1": "BE-Menschenbild",
            "GRETA/ProfessionelleWerthaltungenUndUeberzeugungen/Berufsethos/GRETA-3-1-2": "BE-Wertvorstellungen",
            "GRETA/ProfessionelleWerthaltungenUndUeberzeugungen/BerufsbezogeneUeberzeugungen": "Berufsueberzeugungen",
            "GRETA/ProfessionelleWerthaltungenUndUeberzeugungen/BerufsbezogeneUeberzeugungen/GRETA-3-2-1": "BU-Rollenbewusstsein",
            "GRETA/ProfessionelleWerthaltungenUndUeberzeugungen/BerufsbezogeneUeberzeugungen/GRETA-3-2-2": "BU-Lehrannahmen",
            "GRETA/ProfessionelleSelbststeuerung": "Selbststeuerung",
            "GRETA/ProfessionelleSelbststeuerung/MotivationaleOrientierungen": "MotOrient",
            "GRETA/ProfessionelleSelbststeuerung/MotivationaleOrientierungen/GRETA-4-1-1": "MO-Selbstwirksamkeit",
            "GRETA/ProfessionelleSelbststeuerung/MotivationaleOrientierungen/GRETA-4-1-2": "MO-Enthusiasmus",
            "GRETA/ProfessionelleSelbststeuerung/Selbstregulation": "Selbstregul",
            "GRETA/ProfessionelleSelbststeuerung/Selbstregulation/GRETA-4-2-1": "SR-Feedback",
            "GRETA/ProfessionelleSelbststeuerung/Selbstregulation/GRETA-4-2-2": "SR-Engagement",
            "GRETA/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung": "BerufspraktErf",
            "GRETA/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung/GRETA-4-3-1": "BE-Reflexion",
            "GRETA/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung/GRETA-4-3-2": "BE-Weiterentwicklung",
        }

        km = greta_data["Kompetenzmodell"]
        ct = CompetenceTree(
            name="GRETA",
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
            "area": (1/9, 3/9),
            "facet": (3/9, 9/9),
        }
        # Define color codes for competence levels
        level_color_codes = {
            0: "#888888",  # Grey for level 0
            1: "#C8D575",  # Olive Green for level 1
            2: "#AEBF3F",  # Medium Green for level 2
            3: "#7D8A2C",  # Dark Green for level 3
        }
        # Define the color codes for areas:
        aspect_color_codes = ["#868378", "#aba89e", "#c9c7c0", "#e8e6e1"]

        # Define icons for competence levels (replace with actual icon names)
        utf8_icons = {0: "❓", 1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐"}
        # , 4: "⭐⭐⭐⭐"}
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
                    color_code="#ECEABE",  # Light Green for areas
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
