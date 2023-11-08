"""
Created on 2023-11-06

@author: wf
"""
from ngwidgets.cmd import WebserverCmd
from dcm.dcm_webserver import DynamiceCompentenceMapWebServer
import sys
from dcm.dcm_core import DynamicCompetenceMap
from argparse import ArgumentParser

class CompetenceCmd(WebserverCmd):
    """
    Command line for diagrams server
    """
    
    def getArgParser(self,description:str,version_msg)->ArgumentParser:
        """
        override the default argparser call
        """        
        parser=super().getArgParser(description, version_msg)
        parser.add_argument("-v", "--verbose", action="store_true", help="show verbose output [default: %(default)s]")
        parser.add_argument("-rp", "--root_path",default=DynamicCompetenceMap.examples_path(),help="path to example json files [default: %(default)s]")
        return parser
    
def main(argv:list=None):
    """
    main call
    """
    cmd=CompetenceCmd(config=DynamiceCompentenceMapWebServer.get_config(),webserver_cls=DynamiceCompentenceMapWebServer)
    exit_code=cmd.cmd_main(argv)
    return exit_code
        
DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())