"""
Created on 2024-01-16

@author: wf
"""
from ngwidgets.basetest import Basetest

from dcm.dcm_core import CompetenceTree, RingSpec


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
            
    def test_get_symmetry_spec(self):
        """
        test the symmetry spec handling
        """
        test_cases=[
            ("aspect","count",None),
            ("facet","score",None),
            ("area","time",None),
            ("aspect","invalid_mode","Invalid symmetry mode invalid_mode - must be count, score or time")
        ]
        index=0
        for test_level,test_mode,err_msg in test_cases:
            ct = CompetenceTree(name=f"test{index}")
            if index==0:
                ct.ring_specs={}
                test_level="facet"
                test_mode="count"
            else:
                ct.ring_specs = {
                    test_level: RingSpec(symmetry_mode=test_mode),
                    # Other ring specs without symmetry_mode set
                }
            index+=1
            try:
                # Call the method
                symmetry_level, symmetry_mode = ct.get_symmetry_spec()
                
                # Verify the results
                self.assertEqual(test_mode, symmetry_mode)
                self.assertEqual(test_level, symmetry_level)
            except Exception as ex:
                self.assertEqual(str(ex),err_msg) 
