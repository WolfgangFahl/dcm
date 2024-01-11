"""
Created on 2023-06-11

@author: wf
"""
import json
import os
from dataclasses import dataclass, field
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import quote

import markdown2
import yaml
from dataclasses_json import dataclass_json
from ngwidgets.yamlable import YamlAble

from dcm.svg import SVG, SVGConfig, SVGNodeConfig


@dataclass_json
@dataclass
class CompetenceElement:
    """
    A base class representing a generic competence element with common properties.

    Attributes:
        name (str): The name of the competence element.
        id (Optional[str]): An optional identifier for the competence element will be set to the name if id is None.
        url (Optional[str]): An optional URL for more information about the competence element.
        description (Optional[str]): An optional description of the competence element.
        color_code (str): A string representing a color code associated with the competence element.
    """

    name: str
    id: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    color_code: Optional[str] = None

    def as_html(self) -> str:
        """
        convert me to html

        Returns:
            str: html markup
        """
        html = f"<h2>{self.name}</h2>"
        if self.description:
            desc_html = markdown2.markdown(
                self.description, extras=["fenced-code-blocks", "tables", "spoiler"]
            )
            html = html + "\n" + desc_html
        return html

    def to_svg_node_config(self, url: str = None, **kwargs) -> SVGNodeConfig:
        """
        convert me to an SVGNode Configuration

        Args:
            url(str): the url to use for clicking this svg node - if None use
            my configured url
        """
        if url is None:
            url = self.url
        element_type = f"{self.__class__.__name__}"
        comment = f"{element_type}:{self.description}"
        svg_node_config = SVGNodeConfig(
            element_type=f"{element_type}",
            id=f"{self.id}",
            url=url,
            fill=self.color_code,
            title=self.name,
            comment=comment,
            **kwargs,
        )
        return svg_node_config


@dataclass_json
@dataclass
class CompetenceFacet(CompetenceElement):
    """
    Represents a specific facet of a competence aspect, inheriting from CompetenceElement.

    This class can include additional properties or methods specific to a competence facet.
    """

    def __post_init__(self):
        # Set the id to the name if id is None
        if self.id is None:
            self.id = self.name


@dataclass_json
@dataclass
class CompetenceAspect(CompetenceElement):
    """
    Represents a broader category of competence, which includes various facets.

    Attributes:
        facets (List[CompetenceFacet]): A list of CompetenceFacet objects representing individual facets of this aspect.
    """

    facets: List[CompetenceFacet] = field(default_factory=list)
    credits: Optional[int] = None


@dataclass_json
@dataclass
class CompetenceLevel(CompetenceElement):
    """
    Defines a specific level of competence within the framework.

    Attributes:
        level (int): level number starting from 1 as the lowest and going up to as many level as defined for the CompetenceTree
        icon(str): the name of an icon to be shown for this level
    """

    level: int = 1
    icon: Optional[str] = None


@dataclass_json
@dataclass
class CompetenceTree(CompetenceElement, YamlAble["CompetenceTree"]):
    """
    Represents the entire structure of competencies, including various aspects and levels.

    Attributes:
        competence_aspects (Dict[str, CompetenceAspect]): A dictionary mapping aspect IDs to CompetenceAspect objects.
        competence_levels (List[CompetenceLevel]): A list of CompetenceLevel objects representing the different levels in the competence hierarchy.
        element_names (Dict[str, str]): A dictionary holding the names for tree, aspects, facets, and levels.  The key is the type ("tree", "aspect", "facet", "level").
    """

    lookup_url: Optional[str] = None
    competence_aspects: Dict[str, CompetenceAspect] = field(default_factory=dict)
    competence_levels: List[CompetenceLevel] = field(default_factory=list)
    element_names: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        # prepare yaml dumping
        for aspect_id, aspect in self.competence_aspects.items():
            if aspect.id is None:
                aspect.id = aspect_id

    @classmethod
    def required_keys(cls) -> Tuple:
        keys = {"name", "id", "url", "description", "element_names"}
        return keys

    def lookup_by_path(
        self, path: str, lenient: bool = True
    ) -> Optional[CompetenceElement]:
        """
        Look up and return a competence element (tree,aspect of facet)
        based on the given path.

        The path is expected to be in the format "tree_id/aspect_id/facet_id".
        This method parses the path and retrieves the corresponding competence aspect or facet.

        Args:
            path (str): The path in the format "tree_id/aspect_id/facet_id".

            lenient(bool): if not lenient raise Exceptions for invalid paths and ids
        Returns:
            Optional[CompetenceElement]: The competence aspect or facet corresponding to the given path.
        """

        def handle_error(msg):
            if not lenient:
                raise ValueError(msg)

        parts = path.split("/")
        if len(parts) < 1:
            return None

        tree_id = parts[0]
        if tree_id != self.id:
            handle_error(f"invalid tree_id for lookup {tree_id}")
            return None
        if len(parts) == 1:
            return self
        if len(parts) > 1:
            aspect_id = parts[1]
            # Retrieve the aspect
            aspect = self.competence_aspects.get(aspect_id, None)
        if aspect:
            if len(parts) == 2:
                return aspect
            if len(parts) > 2:
                facet_id = parts[2]
                # Retrieve the facet within the aspect
                for facet in aspect.facets:
                    if facet.id == facet_id:
                        return facet
        handle_error(f"invalid path for lookup {path}")
        return None

    def to_pretty_json(self):
        """
        Converts the CompetenceTree object to a pretty JSON string, handling null values.
        """
        json_str = self.to_json()
        json_dict = json.loads(json_str)

        def remove_none_values(data):
            """
            Recursively removes keys with None values from a dictionary, list, or nested structure.
            """
            if isinstance(data, dict):
                return {
                    k: remove_none_values(v) for k, v in data.items() if v is not None
                }
            elif isinstance(data, list):
                return [remove_none_values(item) for item in data]
            return data

        none_free_dict = remove_none_values(json_dict)
        null_free_json_str = json.dumps(none_free_dict, indent=2)
        return null_free_json_str

    def add_legend(self, svg: SVG) -> None:
        """
        Add a legend to the SVG explaining the color codes for levels and aspects.
        Args:
            svg (SVG): The SVG object to which the legend will be added.
        """
        # Starting x position for the legends, starting 10 pixels from the left edge
        x_start = 10
        # y position for the legends, starting 20 pixels from the bottom edge
        y = svg.config.total_height - svg.config.legend_height + 20
        # Width and height of each legend color box
        box_width, box_height = 30, 20
        # Padding between legend items and between the color box and the text
        padding = 5

        # Add the competence level legend
        level_items = [
            (level.color_code, level.name) for level in self.competence_levels
        ]
        svg.add_legend_column(
            level_items,
            self.element_names.get("level", "Level"),
            x_start,
            y,
            box_width,
            box_height,
        )

        # Calculate the x position for the aspect legend based on the width of the level legend
        x_aspect_start = (
            x_start
            + box_width
            + padding
            + max(svg.get_text_width(level.name) for level in self.competence_levels)
            + padding
        )

        # Add the competence aspect legend
        aspect_items = [
            (aspect.color_code, aspect.name)
            for aspect in self.competence_aspects.values()
        ]
        svg.add_legend_column(
            aspect_items,
            self.element_names.get("aspect", "Aspect"),
            x_aspect_start,
            y,
            box_width,
            box_height,
        )


@dataclass_json
@dataclass
class Achievement:
    """
    Class representing an individual's achievement level for a specific competence facet.

    Attributes:
        path (str): The path in the CompetenceTree, used to derive tree_id, aspect_id, and facet_id.
        level (int): The achieved level for this facet.
        score (float): How well the achievement was reached.
        score_unit (str): Unit of the score, default is "%".
        evidence (Optional[str]): Optional evidence supporting the achievement.
        date_assessed (Optional[str]): Optional date when the achievement was assessed (ISO-Format).
    """

    path: str
    level: int = None
    score: float = None
    score_unit: Optional[str] = "%"
    evidence: Optional[str] = None
    date_assessed_iso: Optional[str] = None

    @property
    def tree_id(self):
        parts = self.path.split("/")
        return parts[0] if parts else None

    @property
    def aspect_id(self):
        parts = self.path.split("/")
        return parts[1] if len(parts) > 1 else None

    @property
    def facet_id(self):
        parts = self.path.split("/")
        return parts[2] if len(parts) > 2 else None


@dataclass_json
@dataclass
class Learner:
    """
    A learner with achievements.
    Attributes:
        learner_id (str): Identifier for the learner.
        achievements (Dict[str, List[Achievement]]):
            A dictionary where each key is a competence element identifier
            and the value is a list of Achievement instances for that tree.
    """

    learner_id: str
    achievements: Optional[List[Achievement]] = field(default=None)

    @classmethod
    def required_keys(cls):
        keys = {"achievements"}
        return keys

    @property
    def main_id(self):
        main_id = self.learner_id
        return main_id

    def get_competence_tree_ids(self) -> List[str]:
        """
        Get all unique competence tree IDs of my achievements.

        Returns:
            List[str]: A list of unique competence tree IDs.
        """
        # Assuming that the learner's achievements are stored in a list called self.achievements
        # You can modify this part according to your actual data structure.

        # Create a set to store unique competence tree IDs
        unique_tree_ids = set()

        # Iterate through the learner's achievements
        for achievement in self.achievements:
            # Assuming each achievement has a tree_id attribute
            tree_id = achievement.tree_id

            # Add the tree_id to the set
            unique_tree_ids.add(tree_id)

        # Convert the set to a list and return
        return list(unique_tree_ids)


class DynamicCompetenceMap:
    """
    a visualization of a competence map
    """

    def __init__(self, competence_tree: CompetenceTree):
        """
        constructor
        """
        self.competence_tree = competence_tree
        self.svg = None

    @property
    def main_id(self):
        main_id = self.competence_tree.id
        return main_id

    def lookup(
        self, aspect_id: str = None, facet_id: str = None
    ) -> Optional[CompetenceElement]:
        """
        Look up an element of the competence tree by aspect ID and facet ID.
        - Returns the entire competence tree if both aspect_id and facet_id are None.
        - Returns a specific aspect if only aspect_id is provided.
        - Returns a specific facet within an aspect if both aspect_id and facet_id are provided.

        Args:
            aspect_id (str, optional): The ID of the aspect to search within.
            facet_id (str, optional): The ID of the facet to find within the specified aspect.

        Returns:
            Optional[CompetenceElement]: The found competence aspect, facet, or the entire competence tree.
        """
        ct = self.competence_tree
        if aspect_id is None:
            return ct
        aspect = ct.competence_aspects.get(aspect_id)
        if aspect is None:
            for ct_aspect in ct.competence_aspects.values():
                if aspect.id == aspect_id:
                    aspect = ct_aspect
        if aspect:
            if facet_id is None:
                return aspect
            for facet in aspect.facets:
                if facet.id == facet_id:
                    return facet
        return None

    @classmethod
    def examples_path(cls) -> str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), "../dcm_examples")
        path = os.path.abspath(path)
        return path

    @classmethod
    def get_example_dcm_definitions(
        cls,
        markup: str = "json",
        required_keys: Optional[Tuple] = None,
        as_text: bool = True,
    ) -> dict:
        """
        Retrieve example Dynamic Competence Map (DCM) definitions from files in the specified markup format (either JSON or YAML).

        Args:
            markup (str): The markup format of the input files. Defaults to 'json'. Supported values are 'json' and 'yaml'.
            required_keys (Optional[Tuple]): A tuple of keys required to validate the data. If not provided, all keys will be considered valid.
            as_text (bool): If True, returns the file content as text; if False, returns parsed data. Defaults to True.

        Returns:
            dict: A dictionary where each key is the prefix of the file name and the value is the file content as text or parsed data, depending on the value of 'as_text'.

        Raises:
            Exception: If there's an error in reading or parsing the file, or if the file does not meet the required validation criteria.
        """
        example_dcm_defs = {}
        file_ext = f".{markup}"
        examples_path = cls.examples_path()
        for dirpath, _dirnames, filenames in os.walk(examples_path):
            for filename in filenames:
                if filename.endswith(file_ext):
                    filepath = os.path.join(dirpath, filename)
                    with open(filepath, "r") as definition_file:
                        file_prefix = filename.replace(file_ext, "")
                        definition_text = definition_file.read()
                        try:
                            definition_data = cls.parse_markup(definition_text, markup)
                            if cls.is_valid_definition(definition_data, required_keys):
                                if as_text:
                                    example_dcm_defs[file_prefix] = definition_text
                                else:
                                    example_dcm_defs[file_prefix] = definition_data
                        except Exception as ex:
                            cls.handle_markup_issue(filename, definition_text, ex)
        return example_dcm_defs

    @classmethod
    def parse_markup(cls, text: str, markup: str) -> Union[dict, list]:
        """
        Parse the given text as JSON or YAML based on the specified markup type.

        Args:
            text (str): The string content to be parsed.
            markup (str): The type of markup to use for parsing. Supported values are 'json' and 'yaml'.

        Returns:
            Union[dict, list]: The parsed data, which can be either a dictionary or a list, depending on the content.

        Raises:
            ValueError: If an unsupported markup format is specified.
        """
        if markup == "json":
            return json.loads(text)
        elif markup == "yaml":
            return yaml.safe_load(text)
        else:
            raise ValueError(f"Unsupported markup format: {markup}")

    @classmethod
    def handle_markup_issue(cls, name: str, definition_string: str, ex, markup):
        if isinstance(ex, JSONDecodeError):
            lines = definition_string.splitlines()  # Split the string into lines
            err_line = lines[ex.lineno - 1]  # JSONDecodeError gives 1-based lineno
            pointer = (
                " " * (ex.colno - 1) + "^"
            )  # Create a pointer string to indicate the error position
            error_message = (
                f"{name}:JSON parsing error on line {ex.lineno} column {ex.colno}:\n"
                f"{err_line}\n"
                f"{pointer}\n"
                f"{ex.msg}"
            )
            raise ValueError(error_message)  # Raise a new exception with this message
        else:
            error_message = f"error in {name}: {str(ex)}"
            raise ValueError(error_message)

    @classmethod
    def is_valid_definition(cls, definition_data, required_keys: Tuple):
        return all(key in definition_data for key in required_keys)

    @classmethod
    def get_examples(cls, content_class=CompetenceTree, markup: str = "json") -> dict:
        examples = {}
        for name, definition_string in cls.get_example_dcm_definitions(
            required_keys=content_class.required_keys(), markup=markup
        ).items():
            example = cls.from_definition_string(
                name, definition_string, content_class, markup=markup
            )
            # check the type of the example
            example_id = example.main_id
            examples[example_id] = example
        return examples

    @classmethod
    def from_definition_string(
        cls, name: str, definition_string: str, content_class, markup: str = "json"
    ) -> Any:
        """
        Load a DynamicCompetenceMap or Learner instance from a definition string (either JSON or YAML).

        Args:
            name (str): A name identifier for the data source.
            definition_string (str): The string content of the definition.
            content_class (dataclass_json): The class which will be instantiated with the parsed data.
            markup (str): The markup format of the data. Defaults to 'json'. Supported values are 'json' and 'yaml'.

        Returns:
            DynamicCompetenceMap: An instance of DynamicCompetenceMap loaded with the parsed data.

        Raises:
            ValueError: If there's an error in parsing the data.
        """
        try:
            data = cls.parse_markup(definition_string, markup)
            content = content_class.from_dict(data)
            if isinstance(content, CompetenceTree):
                return DynamicCompetenceMap(content)
            else:
                return content
        except Exception as ex:
            cls.handle_markup_issue(name, definition_string, ex, markup)

    def generate_svg(
        self, filename: Optional[str] = None, config: Optional[SVGConfig] = None
    ) -> str:
        """
        Generate the SVG markup and optionally save it to a file. If a filename is given, the method
        will also save the SVG to that file. The SVG is generated based on internal state not shown here.

        Args:
            filename (str, optional): The path to the file where the SVG should be saved. Defaults to None.
            config (SVGConfig, optional): The configuration for the SVG canvas and legend. Defaults to default values.

        Returns:
            str: The SVG markup.
        """
        if config is None:
            config = SVGConfig()  # Use default configuration if none provided
        svg_markup = self.generate_svg_markup(self.competence_tree, config)
        if filename:
            self.save_svg_to_file(svg_markup, filename)
        return svg_markup

    def generate_svg_markup(
        self,
        competence_tree: CompetenceTree = None,
        config: SVGConfig = None,
        with_java_script: bool = True,
        lookup_url: str = "",
    ) -> str:
        """
        Generate SVG markup based on the provided competence tree and configuration.

        Args:
            competence_tree (CompetenceTree): The competence tree structure containing the necessary data.
            config (SVGConfig): The configuration for the SVG canvas and legend.
            lookup_url(str): the lookup_url to use if there is none defined in the CompetenceTree

        Returns:
            str: The generated SVG markup.
        """
        if competence_tree is None:
            competence_tree = self.competence_tree
        lookup_url = (
            competence_tree.lookup_url if competence_tree.lookup_url else lookup_url
        )
        competence_aspects = competence_tree.competence_aspects
        # Instantiate the SVG class
        svg = SVG(config)
        self.svg = svg
        # use default config incase config was None
        config = svg.config

        # Center of the donut
        # Center of the donut chart should be in the middle of the main SVG area, excluding the legend
        cx = svg.width // 2
        cy = (config.total_height - config.legend_height) // 2  # Adjusted for legend

        # Calculate the radius for the central circle (10% of the width)
        tree_radius = cx / 9

        # Add the central circle representing the CompetenceTree
        circle_config = competence_tree.to_svg_node_config(
            x=cx, y=cy, width=tree_radius
        )
        svg.add_circle(config=circle_config)

        facet_radius = min(cx, cy) * 0.9  # Leave some margin
        aspect_radius = facet_radius / 3  # Choose a suitable inner radius

        # Total number of facets
        total_facets = sum(len(aspect.facets) for aspect in competence_aspects.values())

        # Starting angle for the first aspect
        aspect_start_angle = 0

        for aspect_code, aspect in competence_aspects.items():
            num_facets_in_aspect = len(aspect.facets)

            # Skip aspects with no facets
            if num_facets_in_aspect == 0:
                continue
            aspect_angle = (num_facets_in_aspect / total_facets) * 360

            aspect_url = (
                aspect.url
                if aspect.url
                else f"{lookup_url}/description/{quote(competence_tree.id)}/{quote(aspect_code)}"
                if lookup_url is not None
                else None
            )
            show_as_popup = aspect.url is None

            aspect_config = aspect.to_svg_node_config(
                url=aspect_url,
                show_as_popup=show_as_popup,
                x=cx,
                y=cy,
                width=tree_radius,  # inner radius
                height=aspect_radius,  # outer radius
            )
            # fix id
            aspect_config.id = aspect_code
            # Draw the aspect segment as a donut segment
            svg.add_donut_segment(
                config=aspect_config,
                start_angle_deg=aspect_start_angle,
                end_angle_deg=aspect_start_angle + aspect_angle,
            )

            facet_start_angle = (
                aspect_start_angle  # Facets start where the aspect starts
            )
            angle_per_facet = (
                aspect_angle / num_facets_in_aspect
            )  # Equal angle for each facet

            for facet in aspect.facets:
                # Add the facet segment as a donut segment
                facet_url = (
                    facet.url
                    if facet.url
                    else f"{lookup_url}/description/{quote(competence_tree.id)}/{quote(aspect_code)}/{quote(str(facet.id))}"
                    if lookup_url is not None
                    else None
                )
                show_as_popup = facet.url is None
                facet_config = facet.to_svg_node_config(
                    url=facet_url,
                    show_as_popup=show_as_popup,
                    x=cx,
                    y=cy,
                    width=aspect_radius,  # inner radius
                    height=facet_radius,  # outer radius
                )
                svg.add_donut_segment(
                    config=facet_config,
                    start_angle_deg=facet_start_angle,
                    end_angle_deg=facet_start_angle + angle_per_facet,
                )
                facet_start_angle += angle_per_facet

            aspect_start_angle += aspect_angle

        # optionally add legend
        if config.legend_height > 0:
            self.competence_tree.add_legend(svg)

        # Return the SVG markup
        return svg.get_svg_markup(with_java_script=with_java_script)

    def save_svg_to_file(self, svg_markup: str, filename: str):
        # Save the SVG content to a file
        with open(filename, "w") as file:
            file.write(svg_markup)
