"""
Created on 2023-11-06

@author: wf
"""
import os
from urllib.parse import urlparse

from fastapi.responses import HTMLResponse
from ngwidgets.file_selector import FileSelector
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, app, ui
from pydantic import BaseModel

from dcm.dcm_core import CompetenceTree, DynamicCompetenceMap
from dcm.svg import SVGConfig
from dcm.version import Version

from typing import Optional

class SVGRenderRequest(BaseModel):
    """
    A request for rendering an SVG.

    Attributes:
        name (str): The name of the render request.
        definition (str): The string representation of the data to be rendered, in either JSON or YAML format.
        markup (str): The format of the definition ('json' or 'yaml').
        config (SVGConfig): Optional configuration for SVG rendering. Defaults to None, which uses default settings.
    """

    name: str
    definition: str
    markup: str
    config: Optional[SVGConfig] = None

class DynamicCompentenceMapWebServer(InputWebserver):
    """
    server to supply Dynamic Competence Map Visualizations
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        """
        get the configuration for this Webserver
        """
        copy_right = "(c)2023 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right, version=Version(), default_port=8885
        )
        return config

    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(
            self, config=DynamicCompentenceMapWebServer.get_config()
        )

        @app.post("/svg/")
        async def render_svg(svg_render_request: SVGRenderRequest) -> HTMLResponse:
            """
            render the given request
            """
            return await self.render_svg(svg_render_request)

    async def render_svg(self, svg_render_request: SVGRenderRequest) -> HTMLResponse:
        """
        render the given request
        """
        r = svg_render_request
        dcm = DynamicCompetenceMap.from_definition_string(
            r.name, r.definition, content_class=CompetenceTree, markup=r.markup
        )
        svg_markup = dcm.generate_svg_markup(config=r.config)
        response = HTMLResponse(content=svg_markup)
        return response

    def get_basename_without_extension(self, url) -> str:
        # Parse the URL to get the path component
        path = urlparse(url).path
        # Extract the base name (e.g., "example.html" from "/dir/example.html")
        basename = os.path.basename(path)
        # Split the base name and extension and return just the base name
        return os.path.splitext(basename)[0]

    async def render(self, _click_args=None):
        """
        Renders the json content as an SVG visualization

        Args:
            click_args (object): The click event arguments.
        """
        try:
            input_source = self.input
            if input_source:
                name = self.get_basename_without_extension(input_source)
                ui.notify(f"rendering {name}")
                definition = self.do_read_input(input_source)
                # Determine the format based on the file extension
                markup = 'json' if input_source.endswith('.json') else 'yaml'
                dcm = DynamicCompetenceMap.from_definition_string(
                    name, definition, content_class=CompetenceTree, markup=markup
                )
                svg = dcm.generate_svg_markup()
                self.svg_view.content = svg
        except BaseException as ex:
            self.handle_exception(ex, self.do_trace)

    async def home(self, _client: Client):
        """Generates the home page with a selection of examples and
        svg display
        """
        self.setup_menu()

        with ui.element("div").classes("w-full"):
            with ui.splitter() as splitter:
                with splitter.before:
                    extensions = {"json": ".json", "yaml": ".yaml"}
                    self.example_selector = FileSelector(
                        path=self.root_path,
                        extensions=extensions,
                        handler=self.read_and_optionally_render,
                    )
                    self.input_input = ui.input(
                        value=self.input, on_change=self.input_changed
                    ).props("size=100")
                    self.tool_button(
                        tooltip="reload", icon="refresh", handler=self.reload_file
                    )
                    if self.is_local:
                        self.tool_button(
                            tooltip="open", icon="file_open", handler=self.open_file
                        )
                with splitter.after:
                    self.svg_view = ui.html("")
        await self.setup_footer()

    def configure_run(self):
        """
        configure the allowed urls
        """
        self.allowed_urls = [
            # "https://raw.githubusercontent.com/JuanIrache/DJI_SRT_Parser/master/samples/",
            # "https://raw.githubusercontent.com/JuanIrache/dji-srt-viewer/master/samples/",
            # "https://cycle.travel/gpx/",
            # "https://cycle.travel/map/journey/",
            DynamicCompetenceMap.examples_path(),
            self.root_path,
        ]
