"""
Created on 2024-03-01

@author: wf
"""

import os
from dataclasses import dataclass, field
from typing import List

from ngwidgets.basetest import Basetest
from ngwidgets.llm import LLM
from ngwidgets.yamlable import YamlAble, dataclass_json

from dcm.dcm_core import CompetenceTree


@dataclass_json
@dataclass
class Question:
    question: str
    options: List[str]
    correct_answer: str


@dataclass_json
@dataclass
class FacetAssessment:
    facet: str
    questions: List[Question] = field(default_factory=list)


@dataclass_json
@dataclass
class Assessment(YamlAble["Assessment"]):
    facets: List[FacetAssessment] = field(default_factory=list)


class TestLLMGreta(Basetest):
    """
    test cresting LLM based assessment questions
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Specify the relative path to the JSON file
        yaml_file_path = os.path.join(script_dir, "..", "dcm_examples", "greta.yaml")
        self.ct = CompetenceTree.load_from_yaml_file(yaml_file_path)
        self.example = """facets:
  - facet: greta_v2_0_1/ProfessionelleSelbststeuerung/BerufspraktischeErfahrung/BeruflicheWeiterentwicklung
    questions:
      - question: "Wie können Lerninhalte für Teilnehmenden angepasst werden?"
        options:
          A: "Durch Verwenden von standardisierten Lehrplänen"
          B: "Durch Integration der Teilnehmenden in die Planung"
          C: "Durch Fokussieren auf theoretische Inhalte"
        correct_answer: "B"
"""
        self.llm = LLM(model="gpt-4")

    def test_read_assessment_example(self):
        ex = Assessment.from_yaml(self.example)
        self.assertIsNotNone(ex)
        self.assertTrue(len(ex.facets) > 0)
        for af in ex.facets:
            self.assertTrue(len(af.questions) > 0)

    def test_competence_assessment_generation(self):
        """
        test generating competence assessment Questions
        """
        skip=True
        if not self.llm.available() or skip:
            return
        prompt = """Du agierst als Assessor für das GRETA Kompetenzmodell
in der Erwachsenenbildung."""
        prompt += f"Mit {len(self.ct.aspects)} Aspekten"
        for i, aspect in enumerate(self.ct.aspects, start=1):
            prompt += f"\n{i}.\n{aspect.name}"
            prompt += f"\n{len(aspect.areas)} Bereichen"
            for j, area in enumerate(aspect.areas, start=1):
                prompt += f"\n{i}.{j}.\n{area.name}"
                prompt += f"\n{len(area.facets)} Facetten"
                for k, facet in enumerate(area.facets, start=1):
                    prompt += f"\nFacette {i}.{j}.{k} {facet.path}\n{facet.name}"
        preamble = prompt
        print(preamble)
        yaml_result = ""
        for i, aspect in enumerate(self.ct.aspects, start=1):
            for j, area in enumerate(aspect.areas, start=1):
                for k, facet in enumerate(area.facets, start=1):
                    prompt = preamble
                    prompt += "\nErstelle fünf multiple choice Fragen mit 4-6 Antwortoptionen zu:"
                    prompt += f"\n{facet.description}"
                    prompt += "Beachte dabei, dass die Fragen objektiv, klar und direkt formuliert sein sollen. Verwende bekannte Informationen und vermeide Spekulationen oder Interpretationen. Die Fragen sollten auf den definierten Kompetenzanforderungen basieren."
                    prompt += "\nDas Ergebnis soll als yaml markup erstellt werden"
                    prompt += (
                        "\nund wird an ein yaml-markup wie im Beispiel unten angehängt:"
                    )
                    prompt += f"{self.example}"
                    prompt += "\nAchte darauf das yaml-Format strikt einzuhalten und vollständig für cut&paste zu liefern denn das Ergebnis wird per Software ausgewertet und muss syntaktisch korrekt und inhaltlich nützlich sein. Füge daher niemals weitere Anmerkungen, Texte oder Elemente wie ```yaml hinzu"
                    print(prompt)
                    try:
                        print(f"{i}.{j}.{k}: prompt Länge: {len(prompt)}")
                        result = self.llm.ask(prompt)
                        print(result)
                        yaml_result += result
                    except Exception as ex:
                        print(f"{i}.{j}.{k}: LLM error {str(ex)}")
        # Path for the YAML file to be saved
        file_path = "/tmp/greta_assessment.yaml"

        # Assuming 'yaml_result' contains the assembled YAML content
        with open(file_path, "w") as file:
            file.write(yaml_result)
