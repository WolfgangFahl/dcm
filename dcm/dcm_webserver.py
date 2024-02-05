"""
Created on 2023-11-06

@author: wf
"""
import os
import uuid
from typing import List, Optional
from urllib.parse import urlparse

from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from ngwidgets.file_selector import FileSelector
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.webserver import WebserverConfig
from nicegui import Client, app, ui
from pydantic import BaseModel

from dcm.dcm_assessment import Assessment
from dcm.dcm_chart import DcmChart
from dcm.dcm_core import CompetenceTree, DynamicCompetenceMap, Learner
from dcm.dcm_web import RingSpecsView
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
    text_mode: Optional[str] = "empty"
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
        copy_right = ""
        config = WebserverConfig(
            short_name="dcm",
            copy_right=copy_right,
            version=Version(),
            default_port=8885,
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = DcmSolution
        return server_config

    def __init__(self):
        """Constructs all the necessary attributes for the WebServer object."""
        InputWebserver.__init__(
            self, config=DynamicCompentenceMapWebServer.get_config()
        )
        self.examples = DynamicCompetenceMap.get_examples(markup="yaml")

        # FastAPI endpoints
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

        # nicegui RESTFul endpoints
        @ui.page("/learner/{learner_slug}")
        async def show_learner(client: Client, learner_slug: str):
            return await self.page(
                client, DcmSolution.assess_learner_by_slug, learner_slug
            )

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
            config=r.config, with_java_script=True, text_mode=r.text_mode
        )
        response = HTMLResponse(content=svg_markup)
        return response

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

    def configure_run(self):
        """
        configure the allowed urls
        """
        InputWebserver.configure_run(self)
        self.allowed_urls = [
            # "https://raw.githubusercontent.com/JuanIrache/DJI_SRT_Parser/master/samples/",
            # "https://raw.githubusercontent.com/JuanIrache/dji-srt-viewer/master/samples/",
            # "https://cycle.travel/gpx/",
            # "https://cycle.travel/map/journey/",
            DynamicCompetenceMap.examples_path(),
            self.root_path,
        ]
        pass


class DcmSolution(InputWebSolution):
    """
    the Dynamic Competence Map solution
    """

    def __init__(self, webserver: DynamicCompentenceMapWebServer, client: Client):
        """
        Initialize the solution

        Calls the constructor of the base solution
        Args:
            webserver (DynamicCompotenceMapWebServer): The webserver instance associated with this context.
            client (Client): The client instance this context is associated with.
        """
        super().__init__(webserver, client)  # Call to the superclass constructor
        self.dcm = None
        self.learner = None
        self.assessment = None
        self.text_mode = "empty"

    def get_basename_without_extension(self, url) -> str:
        # Parse the URL to get the path component
        path = urlparse(url).path
        # Extract the base name (e.g., "example.html" from "/dir/example.html")
        basename = os.path.basename(path)
        # Split the base name and extension and return just the base name
        return os.path.splitext(basename)[0]

    def save_session_state(self) -> None:
        """
        Save the current session state to app.storage.user.
        """
        learner_id = self.learner.learner_id if self.learner else None
        app.storage.user["learner_id"] = learner_id
        app.storage.user["assessment"] = self.assessment is not None

    def get_learner_file_path(self, learner_slug: str) -> str:
        """
        Get the file path for a learner's JSON file based on the learner's slug.

        Args:
            learner_slug (str): The unique slug of the learner.

        Returns:
            str: The file path for the learner's JSON file.
        """
        return os.path.join(self.config.storage_path, f"{learner_slug}.json")

    def load_learner(self, learner_slug: str) -> None:
        """
        Load a learner from a JSON file based on the learner's slug.

        Args:
            learner_slug (str): The unique slug of the learner.

        Raises:
            FileNotFoundError: If the learner file does not exist.
        """
        learner_file = self.get_learner_file_path(learner_slug)
        if not os.path.exists(learner_file):
            raise FileNotFoundError(f"Learner file not found: {learner_file}")
        self.learner = Learner.load_from_json_file(learner_file)
        self.save_session_state()

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
                with self.content_div:
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
                self.render_item(item)
        except Exception as ex:
            self.handle_exception(ex)

    def render_item(self, item):
        if isinstance(item, DynamicCompetenceMap):
            self.render_dcm(item)
        else:
            self.learner = item
            self.save_session_state()
            self.assess(item)

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
                self.learner = None
            self.dcm = dcm
            self.ringspecs_view.update_rings(dcm.competence_tree)
            self.assess_state()
            dcm_chart = DcmChart(dcm)
            svg_markup = dcm_chart.generate_svg_markup(
                learner=learner,
                selected_paths=selected_paths,
                config=self.svg.config,
                with_java_script=False,
                text_mode=self.text_mode,
            )
            # Use the new get_java_script method to get the JavaScript
            self.svg_view.content = (svg_markup,)
            self.svg_view.update()
        except Exception as ex:
            self.handle_exception(ex)

    def prepare_ui(self):
        """
        prepare the user interface
        """
        self.user_id = app.storage.browser["id"]
        self.prepare_svg()

    def prepare_svg(self):
        """
        prepare the SVG / javascript display
        """
        config = SVGConfig(with_popup=True)
        self.svg = SVG(config=config)
        java_script = self.svg.get_java_script()

        # Add the script using ui.add_head_html()
        ui.add_head_html(java_script, shared=True)

    def show_ui(self):
        """
        show the ui
        """
        with self.content_div:
            with ui.splitter() as splitter:
                with splitter.before:
                    with ui.grid(columns=2).classes("w-full") as self.left_selection:
                        extensions = {"json": ".json", "yaml": ".yaml"}
                        self.example_selector = FileSelector(
                            path=self.webserver.root_path,
                            extensions=extensions,
                            handler=self.read_and_optionally_render,
                        )
                        self.ringspecs_view = RingSpecsView(self)
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
                            if self.is_local:
                                self.tool_button(
                                    tooltip="open",
                                    icon="file_open",
                                    handler=self.open_file,
                                )
                            self.download_button = self.tool_button(
                                tooltip="download",
                                icon="download",
                                handler=self.download,
                            )
                with splitter.after:
                    self.svg_view = ui.html("")

    async def home(
        self,
    ):
        """Generates the home page with a selection of examples and
        svg display
        """
        await self.setup_content_div(self.show_ui)
        self.assess_state()

    def assess_learner(self, dcm, learner):
        """
        assess the given Dynamic Competence Map and learner

        Args:
            dcm(DynamicCompetenceMap): the competence map
            learner(Learner): the learner to get the self assessment for

        """
        if not self.content_div:
            return
        with self.content_div:
            if self.assessment is not None:
                self.assessment.reset(dcm=dcm, learner=learner)
            else:
                with self.left_grid:
                    with ui.row() as self.assessment_row:
                        self.assessment = Assessment(self, dcm=dcm, learner=learner)
            self.assessment.step(0)

    def new_assess(self):
        """
        run a new  assessment for a new learner
        """
        try:
            learner_id = f"{uuid.uuid4()}"
            self.learner = Learner(learner_id)
            self.save_session_state()
            self.assess_learner(self.dcm, self.learner)
        except Exception as ex:
            self.handle_exception(ex)

    async def assess_learner_by_slug(self, learner_slug: str):
        """
        Assess a learner based on the slug of the id

        Args:
            learner_slug (str): The unique slug of the learner.

        Raises:
            HTTPException: If the learner file does not exist or an error occurs.
        """

        def show():
            try:
                self.show_ui()
                self.load_learner(learner_slug)
                self.assess(self.learner)
            except Exception as ex:
                self.handle_exception(ex)

        await self.setup_content_div(show)

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
        if not tree_id in self.webserver.examples:
            raise Exception(f"invalid competence tree_id {tree_id}")
        dcm = self.webserver.examples[tree_id]
        # assess_learner will render ...
        # self.render_dcm(dcm,learner=learner)
        self.assess_learner(dcm, learner)

    def on_update_ringspecs(self):
        if self.learner:
            self.render_item(self.learner)
        else:
            self.render_item(self.dcm)

    def assess_state(self):
        """
        save the session state and reflect
        in the UI
        """
        self.save_session_state()
        if self.dcm and self.learner is None:
            # allow creating a new learner
            self.assessment_button.enable()
        else:
            # the assessment is already on
            self.assessment_button.disable()
        if self.assessment is not None:
            # downloading is possible
            self.download_button.enable()
        else:
            # downloading is not possible - we have n learner
            self.download_button.disable()

    async def download(self, _args):
        """
        allow downloading the assessment result
        """
        try:
            with self.content_div:
                if not self.assessment:
                    ui.notify("no active learner assessment")
                    return
                json_path = self.assessment.store()
                ui.notify(f"downloading {json_path}")
                ui.download(json_path)
        except Exception as ex:
            self.handle_exception(ex)
