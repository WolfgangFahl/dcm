"""
Created on 2024-01-23

@author: wf
"""
import os
import tempfile

import yaml
from ngwidgets.basetest import Basetest

from dcm.dcm_webserver import ServerConfig

class TestServerConfig(Basetest):
    """
    Test cases for the ServerConfig class.
    """
    
    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    def test_server_config(self):
        # Create a temporary YAML config file for testing
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
            # Example configuration data
            config_data = {
                "storage_secret": "test_secret",
                "storage_path": "/tmp/test_storage",
            }
            yaml.dump(config_data, tmp_file)
            tmp_file_path = tmp_file.name

        try:
            # Load the configuration using the ServerConfig class
            config = ServerConfig.from_config_yaml(tmp_file_path)

            # Check if the configuration is loaded correctly
            self.assertEqual(config.storage_secret, "test_secret")
            self.assertEqual(config.storage_path, "/tmp/test_storage")

        finally:
            # Clean up: Remove the temporary file
            os.remove(tmp_file_path)
            
    def test_server_config_default(self):
        """
        test the server configuration with default yaml path
        """
        server_config=ServerConfig.from_config_yaml(yaml_path=None)
        if self.debug:
            print(server_config.to_yaml())
