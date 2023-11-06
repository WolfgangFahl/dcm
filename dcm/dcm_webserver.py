"""
Created on 2023-11-06

@author: wf
"""
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from dcm.version import Version

class DynamiceCompentenceMapWebServer(InputWebserver):
    """
    server to supply Dynamic Competence Map Visualizations
    
    """
    @classmethod
    def get_config(cls)->WebserverConfig:
        copy_right="(c)2023 Wolfgang Fahl"
        config=WebserverConfig(copy_right=copy_right,version=Version(),default_port=8885)
        return config
    
    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(self,config=DynamiceCompentenceMapWebServer.get_config())
 
    
