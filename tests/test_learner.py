"""
Created on 2024-01-11

@author: wf
"""
import json

from ngwidgets.basetest import Basetest

from dcm.dcm_core import DynamicCompetenceMap, Learner


class TestLearner(Basetest):
    """
    test Learner handling
    """

    def test_learner_competence_trees(self):
        """
        test that the competence trees for a learner are
        available
        """
        debug = self.debug
        # debug = True
        ex_path = DynamicCompetenceMap.examples_path()
        json_path = f"{ex_path}/arch_student_123.json"
        with open(json_path, "r") as json_file:
            learner_dict = json.load(json_file)
            if debug:
                print(json.dumps(learner_dict, indent=2))
            learner = Learner.from_dict(learner_dict)
            self.assertTrue(len(learner.achievements) > 0)
            tree_ids = learner.get_competence_tree_ids()
            if debug:
                print(tree_ids)
            self.assertEqual(1, len(tree_ids))
            self.assertEqual("architecture", tree_ids[0])
            for achievement in learner.achievements:
                self.assertTrue(achievement.path in learner.achievements_by_path)
