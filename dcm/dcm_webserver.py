"""
Created on 2023-11-06

@author: wf
"""
import os
from typing import Optional
from urllib.parse import urlparse

from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from ngwidgets.file_selector import FileSelector
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, app, ui
from pydantic import BaseModel

from dcm.dcm_core import CompetenceTree, DynamicCompetenceMap, Learner
from dcm.dcm_sela import SelfAssessment
from dcm.svg import SVG, SVGConfig
from dcm.version import Version


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
        copy_right = "(c)2023-2024 Wolfgang Fahl"
        config = WebserverConfig(
            copy_right=copy_right, version=Version(), default_port=8885
        )
        return config

    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(
            self, config=DynamicCompentenceMapWebServer.get_config()
        )
        self.examples = DynamicCompetenceMap.get_examples(markup="yaml")
        self.dcm=None

        @app.post("/svg/")
        async def render_svg(svg_render_request: SVGRenderRequest) -> HTMLResponse:
            """
            render the given request
            """
            return await self.render_svg(svg_render_request)

        @app.get("/description/{example_name}/{aspect_id}/{facet_id}")
        async def get_description_for_facet(
            example_name: str, aspect_id: str = None, facet_id: str = None
        ) -> HTMLResponse:
            """
            Endpoints to get the description of a competence element (competence tree, aspect, or facet).

            Args:
                example_name (str): Name of the example.
                aspect_id (str, optional): ID of the aspect. Defaults to None.
                facet_id (str, optional): ID of the facet. Defaults to None.

            Returns:
                HTMLResponse: HTML content of the description.
            """
            return await self.show_description(example_name, aspect_id, facet_id)

        @app.get("/description/{example_name}/{aspect_id}")
        async def get_description_with_aspect(
            example_name: str, aspect_id: str
        ) -> HTMLResponse:
            return await self.show_description(example_name, aspect_id)

        @app.get("/description/{example_name}")
        async def get_tree_description_with_example(example_name: str) -> HTMLResponse:
            return await self.show_description(example_name)

    async def show_description(
        self, example_name: str, aspect_id: str = None, facet_id: str = None
    ) -> HTMLResponse:
        """
        Show the HTML description of a specific facet of a competence aspect from an example.

        Args:
            example_name (str): The name of the example from which to retrieve the facet description.
            aspect_id (str): The identifier of the competence aspect.
            facet_id (str): The identifier of the competence facet.

        Returns:
            HTMLResponse: The response object containing the HTML-formatted description.

        Raises:
            HTTPException: If the example name provided does not exist in the examples collection.
        """
        if example_name in self.examples:
            example = self.examples[example_name]
            element = example.lookup(aspect_id, facet_id)
            if element:
                content = element.as_html()
                return HTMLResponse(content=content)
            else:
                content = (
                    f"No element found for {aspect_id}/{facet_id} in {example_name}"
                )
                return HTMLResponse(content=content, status_code=404)
        else:
            msg = f"unknown example {example_name}"
            raise HTTPException(status_code=404, detail=msg)

    async def render_svg(self, svg_render_request: SVGRenderRequest) -> HTMLResponse:
        """
        render the given request
        """
        r = svg_render_request
        dcm = DynamicCompetenceMap.from_definition_string(
            r.name, r.definition, content_class=CompetenceTree, markup=r.markup
        )
        svg_markup = dcm.generate_svg_markup(config=r.config, with_java_script=True)
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
                markup = "json" if input_source.endswith(".json") else "yaml"
                if "learner_id" in definition:
                    content_class = Learner
                else:
                    content_class = CompetenceTree
                item = DynamicCompetenceMap.from_definition_string(
                    name, definition, content_class=content_class, markup=markup
                )
                if isinstance(item, DynamicCompetenceMap):
                    self.dcm=item
                    self.sela_button.enable()
                    svg = self.dcm.generate_svg_markup(with_java_script=False)
                    # Use the new get_java_script method to get the JavaScript
                    self.svg_view.content = svg
                else:
                    self.self_assess(item)
        except BaseException as ex:
            self.handle_exception(ex, self.do_trace)

    async def home(self, _client: Client):
        """Generates the home page with a selection of examples and
        svg display
        """
        svg = SVG()
        java_script = svg.get_java_script()

        # Add the script using ui.add_head_html()
        ui.add_head_html(java_script)

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
                    with ui.row() as self.button_row:
                        self.tool_button(
                            tooltip="reload", icon="refresh", handler=self.reload_file
                        )
                        self.sela_button=self.tool_button(
                            tooltip="self assessment",icon="query_stats",handler=self.new_self_assess)
                        self.sela_button.disable()
                        if self.is_local:
                            self.tool_button(
                                tooltip="open", icon="file_open", handler=self.open_file
                            )
                with splitter.after:
                    self.svg_view = ui.html("")
        await self.setup_footer()
        
    def new_self_assess(self):
        """
        run a self assessment for a new learner
        """
        learner=Learner(learner_id="?")
        self.sela = SelfAssessment(
            self, competence_tree=self.dcm.competence_tree, learner=learner
        )

    def self_assess(self, learner: Learner,tree_id:str=None):
        """
        run a self assessment for the given learner
        
        Args:
            learner(Learner): the learner to get the self assessment for
            tree_id(str): the identifier for the competence tree
        """
        if tree_id is None:
            tree_ids = learner.get_competence_tree_ids()
            if len(tree_ids) != 1:
                raise Exception(
                    f"There must be exactly one competence tree referenced but there are: {tree_ids}"
                )
            tree_id = tree_ids[0]
        if not tree_id in self.examples:
            raise Exception(f"invalid competence tree_id {tree_id}")
        dcm = self.examples[tree_id]
        self.sela = SelfAssessment(
            self, competence_tree=dcm.competence_tree, learner=learner
        )

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
