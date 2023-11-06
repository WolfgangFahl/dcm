"""
Created on 2023-11-06

@author: wf
"""
from ngwidgets.cmd import WebserverCmd
from dcm.dcm_webserver import DynamiceCompentenceMapWebServer
import sys

class CompetenceCmd(WebserverCmd):
    """
    Command line for diagrams server
    """
    def __init__(self):
        """
        constructor
        """
        config=DynamiceCompentenceMapWebServer.get_config()
        WebserverCmd.__init__(self, config, DynamiceCompentenceMapWebServer, DEBUG)
        pass
    
def main(argv:list=None):
    """
    main call
    """
    cmd=CompetenceCmd()
    exit_code=cmd.cmd_main(argv)
    return exit_code
        
DEBUG = 0
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(main())