"""
Created on 2023-11-06

@author: wf
"""
import os
from typing import List, Optional
from urllib.parse import urlparse

from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from ngwidgets.file_selector import FileSelector
from ngwidgets.input_webserver import InputWebserver
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, app, ui
from pydantic import BaseModel

from dcm.dcm_assessment import Assessment
from dcm.dcm_chart import DcmChart
from dcm.dcm_core import CompetenceTree, DynamicCompetenceMap, Learner
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
        self.dcm = None
        self.assessment = None
        self.text_mode="none"

        @app.post("/svg/")
        async def render_svg(svg_render_request: SVGRenderRequest) -> HTMLResponse:
            """
            render the given request
            """
            return await self.render_svg(svg_render_request)

        @app.get("/description/{tree_id}/{aspect_id}/{area_id}/{facet_id}")
        async def get_description_for_facet(
            tree_id: str,
            aspect_id: str = None,
            area_id: str = None,
            facet_id: str = None,
        ) -> HTMLResponse:
            """
            Endpoints to get the description of a competence facet


            Args:
                tree_id (str): ID of the tree
                area_id (str): ID of the area
                aspect_id (str, optional): ID of the aspect. Defaults to None.
                facet_id (str, optional): ID of the facet. Defaults to None.

            Returns:
                HTMLResponse: HTML content of the description.
            """
            path = f"{tree_id}/{aspect_id}/{area_id}/{facet_id}"
            return await self.show_description(path)

        @app.get("/description/{tree_id}/{aspect_id}/{area_id}")
        async def get_description_for_area(
            tree_id: str, aspect_id: str = None, area_id: str = None
        ) -> HTMLResponse:
            """
            Endpoints to get the description of a
            competence area

            Args:
                tree_id (str): ID of the tree
                area_id (str): ID of the area
                aspect_id (str, optional): ID of the aspect. Defaults to None.

            Returns:
                HTMLResponse: HTML content of the description.
            """
            path = f"{tree_id}/{aspect_id}/{area_id}"
            return await self.show_description(path)

        @app.get("/description/{tree_id}/{aspect_id}")
        async def get_description_for_aspect(
            tree_id: str, aspect_id: str = None
        ) -> HTMLResponse:
            """
            Endpoint to get the description of a competence aspect

            Args:
                tree_id (str): ID of the tree
                area_id (str): ID of the area

            Returns:
                HTMLResponse: HTML content of the description.
            """
            path = f"{tree_id}/{aspect_id}"
            return await self.show_description(path)

        @app.get("/description/{tree_id}")
        async def get_description_for_tree(tree_id: str) -> HTMLResponse:
            """
            Endpoint to get the description of a competence tree

            Args:
                tree_id (str): ID of the tree

            Returns:
                HTMLResponse: HTML content of the description.
            """
            path = f"{tree_id}"
            return await self.show_description(path)

    async def show_description(self, path: str = None) -> HTMLResponse:
        """
        Show the HTML description of a specific
        competence element given by the path

        Args:
            path(str): the path identifying the element

        Returns:
            HTMLResponse: The response object containing the HTML-formatted description.

        Raises:
            HTTPException: If the example name provided does not exist in the examples collection.
        """
        path_parts = path.split("/")
        tree_id = path_parts[0]
        if tree_id in self.examples:
            example = self.examples[tree_id]
            element = example.competence_tree.lookup_by_path(path)
            if element:
                content = element.as_html()
                return HTMLResponse(content=content)
            else:
                content = f"No element found for {path} in {tree_id}"
                return HTMLResponse(content=content, status_code=404)
        else:
            msg = f"unknown competence tree {tree_id}"
            raise HTTPException(status_code=404, detail=msg)

    async def render_svg(self, svg_render_request: SVGRenderRequest) -> HTMLResponse:
        """
        render the given request
        """
        r = svg_render_request
        dcm = DynamicCompetenceMap.from_definition_string(
            r.name, r.definition, content_class=CompetenceTree, markup=r.markup
        )
        dcm_chart = DcmChart(dcm)
        svg_markup = dcm_chart.generate_svg_markup(
            config=r.config, with_java_script=True,text_mode=self.text_mode
        )
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
                with self.container:
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
                    self.render_dcm(item)
                else:
                    self.learner = item
                    self.assess(item)
        except Exception as ex:
            self.handle_exception(ex, self.do_trace)

    def render_dcm(
        self,
        dcm,
        learner: Learner = None,
        selected_paths: List = [],
        clear_assessment: bool = True,
    ):
        """
        render the dynamic competence map

        Args:
            dcm(DynamicCompetenceMap)
            selected_paths (List, optional): A list of paths that should be highlighted
            in the SVG. These paths typically represent specific competencies or
            achievements. Defaults to an empty list.

        """
        try:
            if clear_assessment and self.assessment:
                try:
                    self.assessment_row.clear()
                except Exception as ex:
                    ui.notify(str(ex))
                self.assessment = None
            self.dcm = dcm
            self.assessment_button.enable()
            dcm_chart = DcmChart(dcm)
            svg = dcm_chart.generate_svg_markup(
                learner=learner, 
                selected_paths=selected_paths, 
                with_java_script=False,
                text_mode=self.text_mode
            )
            # Use the new get_java_script method to get the JavaScript
            self.svg_view.content = svg
            self.svg_view.update()
        except Exception as ex:
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

        with ui.element("div").classes("w-full") as self.container:
            with ui.splitter() as splitter:
                with splitter.before:
                    with ui.grid(columns=2).classes("w-full") as self.left_selection:
                        extensions = {"json": ".json", "yaml": ".yaml"}
                        self.example_selector = FileSelector(
                            path=self.root_path,
                            extensions=extensions,
                            handler=self.read_and_optionally_render,
                        )
                        selection=["none","curved","horizontal","angled"]
                        self.text_mode="curved"
                        self.add_select("text", selection).bind_value(self,"text_mode")
                    with ui.grid(columns=1).classes("w-full") as self.left_grid:
                        with ui.row() as self.input_row:
                            self.input_input = ui.input(
                                value=self.input, on_change=self.input_changed
                            ).props("size=100")
                        with ui.row() as self.button_row:
                            self.tool_button(
                                tooltip="reload",
                                icon="refresh",
                                handler=self.reload_file,
                            )
                            self.assessment_button = self.tool_button(
                                tooltip="assessment",
                                icon="query_stats",
                                handler=self.new_assess,
                            )
                            self.assessment_button.disable()
                            if self.is_local:
                                self.tool_button(
                                    tooltip="open",
                                    icon="file_open",
                                    handler=self.open_file,
                                )
                with splitter.after:
                    self.svg_view = ui.html("")
        await self.setup_footer()

    def assess_learner(self, dcm, learner):
        """
        assess the given Dynamic Competence Map and learner

        Args:
            dcm(DynamicCompetenceMap): the competence map
            learner(Learner): the learner to get the self assessment for

        """
        if self.assessment is not None:
            self.assessment.reset(dcm=dcm, learner=learner)
        else:
            with self.left_grid:
                with ui.row() as self.assessment_row:
                    self.assessment = Assessment(self, dcm=dcm, learner=learner)
        self.assessment.update_achievement_view()

    def new_assess(self):
        """
        run a new  assessment for a new learner
        """
        learner = Learner(learner_id="?")
        self.assess_learner(self.dcm, learner)

    def assess(self, learner: Learner, tree_id: str = None):
        """
        run an assessment for the given learner

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
        # assess_learner will render ...
        # self.render_dcm(dcm,learner=learner)
        self.assess_learner(dcm, learner)

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
