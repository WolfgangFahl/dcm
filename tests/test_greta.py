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
    RingSpec
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
            script_dir, "..", "greta", "greta_kompetenzmodell_2-0_1.json"
        )

        # Check if the JSON file exists
        self.assertTrue(os.path.exists(json_file_path))
        # Open and read the JSON file
        with open(json_file_path, "r") as json_file:
            greta_data = json.load(json_file)
        
        km = greta_data["Kompetenzmodell"]
        greta_id=km["ID"]
        greta_short_names = {
            f"{greta_id}": "GRETA",
            f"{greta_id}/BerufspraktischesWissenUndKoennen": "Berufsprak",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik": "DidaktMethodik",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/LerninhalteUndZiele": "DM-Lernziele",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/MethodenMedienUndLernmaterialien": "DM-Methoden",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/RahmenbedingungenUndLernumgebungen": "DM-Rahmenbedingungen",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/DidaktikUndMethodik/Outcomeorientierung": "DM-Outcome",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/BeratungIndividualisierteLernunterstuetzung": "Beratung",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/BeratungIndividualisierteLernunterstuetzung/Teilnehmendenorientierung": "Beratung-Orientierung",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/BeratungIndividualisierteLernunterstuetzung/DiagnostikUndLernberatung": "Lernberatung",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/KommunikationUndInteraktion": "KommInterakt",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/KommunikationUndInteraktion/ModerationUndSteuerungVonGruppen": "KI-Gruppen",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/KommunikationUndInteraktion/ProfessionelleKommunikation": "KI-Kommunikation",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/Organisation": "Organisation",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/Organisation/KooperationMitDenAuftraggebendenArbeitgebenden": "Org-Auftraggeber",
            f"{greta_id}/BerufspraktischesWissenUndKoennen/Organisation/KollegialeZusammenarbeitNetzwerken": "Org-Netzwerke",
            f"{greta_id}/FachUndFeldspezifischesWissen": "FachFeldWissen",
            f"{greta_id}/FachUndFeldspezifischesWissen/Feldbezug": "Feldbezug",
            f"{greta_id}/FachUndFeldspezifischesWissen/Feldbezug/AdressatinnenUndAdressaten": "FB-Adressaten",
            f"{greta_id}/FachUndFeldspezifischesWissen/Feldbezug/FeldspezifischesWissen": "FB-Feldwissen",
            f"{greta_id}/FachUndFeldspezifischesWissen/Feldbezug/CurriculareUndInstitutionelleRahmenbedingungen": "FB-Curricula",
            f"{greta_id}/ProfessionelleWerthaltungenUndUeberzeugungen": "Werthaltungen",
            f"{greta_id}/ProfessionelleWerthaltungenUndUeberzeugungen/Berufsethos": "Berufsethos",
            f"{greta_id}/ProfessionelleWerthaltungenUndUeberzeugungen/Berufsethos/Menschenbilder": "BE-Menschenbild",
            f"{greta_id}/ProfessionelleWerthaltungenUndUeberzeugungen/Berufsethos/Wertvorstellungen": "BE-Wertvorstellungen",
            f"{greta_id}/ProfessionelleWerthaltungenUndUeberzeugungen/BerufsbezogeneUeberzeugungen": "Berufsueberzeugungen",
            f"{greta_id}/ProfessionelleWerthaltungenUndUeberzeugungen/BerufsbezogeneUeberzeugungen/EigenesRollenbewusstsein": "BU-Rollenbewusstsein",
            f"{greta_id}/ProfessionelleWerthaltungenUndUeberzeugungen/BerufsbezogeneUeberzeugungen/SubjektiveAnnahmenUeberDasLehrenUndLernen": "BU-Lehrannahmen",
            f"{greta_id}/ProfessionelleSelbststeuerung": "Selbststeuerung",
            f"{greta_id}/ProfessionelleSelbststeuerung/MotivationaleOrientierungen": "MotOrient",
            f"{greta_id}/ProfessionelleSelbststeuerung/MotivationaleOrientierungen/Selbstwirksamkeitsueberzeugungen": "MO-Selbstwirksamkeit",
            f"{greta_id}/ProfessionelleSelbststeuerung/MotivationaleOrientierungen/Enthusiasmus": "MO-Enthusiasmus",
            f"{greta_id}/ProfessionelleSelbststeuerung/Selbstregulation": "Selbstregul",
            f"{greta_id}/ProfessionelleSelbststeuerung/Selbstregulation/UmgangMitFeedbackUndKritik": "SR-Feedback",
            f"{greta_id}/ProfessionelleSelbststeuerung/Selbstregulation/EngagementUndDistanz": "SR-Engagement",
            f"{greta_id}/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung": "BerufspraktErf",
            f"{greta_id}/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung/ReflexionDesEigenenLehrhandelns": "BE-Reflexion",
            f"{greta_id}/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung/BeruflicheWeiterentwicklung": "BE-Weiterentwicklung",
        }

       
        ct = CompetenceTree(
            name="GRETA",
            id=greta_id,
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
        ct.ring_specs = {
            "tree": RingSpec(
                inner_ratio=0.0, 
                outer_ratio=1/10),
            "aspect": RingSpec(
                text_mode="curved",
                inner_ratio=9/10, 
                outer_ratio=10/10),
            "area": RingSpec(
                inner_ratio=0.0, 
                outer_ratio=0.0
                ),
            "facet": RingSpec(
                text_mode="angled",
                inner_ratio=1 / 10, 
                outer_ratio=9 / 10),
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
        ok=True
        for path, element in ct.elements_by_path.items():
            if not path in greta_short_names:
                parts=path.split("/")
                print(f"missing short_name for {json.dumps(parts,indent=2)}")
                ok=False
                continue
            element.short_name = greta_short_names[path]
            element.border_color = "white"
        self.assertTrue(ok)
        yaml_str = ct.to_yaml()
        if self.debug:
            print(yaml_str)
        with open("/tmp/greta.yaml", "w") as yaml_file:
            yaml_file.write(yaml_str)
