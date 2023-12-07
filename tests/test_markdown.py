"""
Created on 2023-12-07

@author: wf
"""

import markdown2
from ngwidgets.basetest import Basetest

class TestMarkdown2(Basetest):
    """
    test the markdown 2 html converter
    """
    
    def test_markdown2(self):
        """
        """
        markdown_text = """
        # Your Markdown Here
        * Example
        * GitHub-Flavored
        * Markdown
        """
        
        # Convert Markdown to HTML using markdown2
        html = markdown2.markdown(markdown_text, extras=["fenced-code-blocks", "tables", "spoiler"])
        if self.debug:
            print(html)
