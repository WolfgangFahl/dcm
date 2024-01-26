"""
Created on 2024-01-24

Experience API xAPI support module
@author: wf
"""
import json
import sys

from dcm.dcm_core import Achievement, CompetenceTree, Learner


class XAPI:
    """
    Experience API xAPI support class
    """

    def __init__(self):
        self.xapi_dict = {}

    def warn(self, msg):
        print(msg, file=sys.stderr)
        pass

    def to_learner(self, competence_tree: CompetenceTree) -> Learner:
        """
        Convert xapi_dict to a Learner with Achievements.
        Args:
            competence_tree (CompetenceTree): The competence tree to align the achievements with.
        Returns:
            Learner: A learner object with achievements mapped from xapi_dict.
        """
        # Assuming each entry in xapi_dict is an xAPI statement relevant to a learning activity
        achievements = []
        actor_id = None
        learner = None
        for entry in self.xapi_dict:
            stmt = entry.get("statement")
            if stmt:
                actor = stmt.get("actor")
                if actor:
                    # Extract necessary information from the xAPI statement
                    new_actor_id = actor["account"]["name"]
                    if actor_id is None:
                        actor_id = new_actor_id
                    else:
                        if new_actor_id != actor_id:
                            self.warn(f"invalid actor_id {new_actor_id} != {actor_id}")
                competence_path = stmt["context"]["extensions"][
                    "learningObjectMetadata"
                ]["competencePath"]
                score_scaled = stmt["result"]["score"]["scaled"]
                timestamp = stmt["timestamp"]

                # Create an Achievement instance
                achievement = Achievement(
                    path=competence_path,
                    level=int(
                        score_scaled * competence_tree.total_valid_levels
                    ),  # Convert scaled score to level
                    score=stmt["result"]["score"]["raw"],
                    date_assessed_iso=timestamp,
                )
                achievements.append(achievement)

        if actor_id:
            # Create a Learner instance with these achievements
            learner = Learner(learner_id=actor_id, achievements=achievements)
        else:
            self.warn("no learner / actor defined")
        return learner

    @classmethod
    def from_json(cls, json_file_path: str):
        xapi = cls()
        # Open and read the JSON file
        with open(json_file_path, "r") as json_file:
            xapi.xapi_dict = json.load(json_file)
        return xapi
