"""
Created on 2024-01-16

@author: wf
"""
from ngwidgets.basetest import Basetest

from dcm.dcm_core import CompetenceTree


class TestDCM(Basetest):
    """
    general Dynamic Competence Map tests
    """

    def test_slugify(self):
        """
        test the slugify handling of ids
        """
        debug = self.debug
        # debug=True
        for name in ["portfolio_plus", "iSAQB_CPSA-F", "greta_v2_0"]:
            ct = CompetenceTree(name=name)
            if debug:
                print(ct.id)
            self.assertEqual(name, ct.id)
