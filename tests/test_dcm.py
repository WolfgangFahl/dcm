'''
Created on 2024-01-16

@author: wf
'''
from dcm.dcm_core import CompetenceTree
from ngwidgets.basetest import Basetest

class TestDCM(Basetest):
    """
    general Dynamic Competence Map tests
    """
    
    def test_slugify(self):
        """
        test the slugify handling of ids
        """
        debug=self.debug
        #debug=True
        for name in ["portfolio_plus","iSAQB_CPSA-F"]:
            ct=CompetenceTree(name=name)
            if debug:
                print(ct.id)
            self.assertEqual(name,ct.id)
