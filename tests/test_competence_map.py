'''
Created on 2023-11-06

@author: wf
'''
from ngwidgets.basetest import Basetest
from dcm.competence import DynamicCompetenceMap

class TestDynamicCompetenceMap(Basetest):
    """
    test the dynamic competence map
    """
    
    def testCompetenceMap(self):
        """
        test the competence map
        """
        dcm=DynamicCompetenceMap()
        