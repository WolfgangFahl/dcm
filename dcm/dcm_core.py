"""
Created on 2023-06-11

@author: wf
"""
import json
import os
from dataclasses import dataclass, field
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Tuple, Union

import markdown2
import yaml
from dataclasses_json import dataclass_json
from ngwidgets.yamlable import YamlAble, lod_storable
from slugify import slugify

from dcm.svg import SVG, SVGNodeConfig


@dataclass_json
@dataclass
class RingSpec:
    """
    Specification of rings of the donut chart.

    Attributes:
        text_mode (Optional[str]): The mode of text display on the ring. Default is None.
        inner_ratio (Optional[float]): The inner radius of the ring, relative to the chart size.
        outer_ratio (Optional[float]): The outer radius of the ring, relative to the chart size.
    """

    text_mode: Optional[str] = "empty"
    inner_ratio: Optional[float] = None
    outer_ratio: Optional[float] = None

    @property
    def empty(self) -> bool:
        empty = (
            self.inner_ratio is None
            or self.outer_ratio is None
            or (self.inner_ratio + self.outer_ratio) == 0.0
        )
        return empty


@dataclass_json
@dataclass
class CompetenceElement:
    """
    A base class representing a generic competence element with common properties.

    Attributes:
        name (str): The name of the competence element.
        short_name(Optional[str]): the label to be displayed
        id (Optional[str]): An optional identifier for the competence element will be set to the name if id is None.
        url (Optional[str]): An optional URL for more information about the competence element.
        description (Optional[str]): An optional description of the competence element.
        color_code (str): A string representing a (fill) color code associated with the competence element.
        border_color (str): A string representing the border color to be used e.g. "black" or "#ffffff"
    """

    name: str
    short_name: Optional[str] = None
    id: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    color_code: Optional[str] = None
    border_color: Optional[str] = None

    def __post_init__(self):
        # Set the id to the the slug of the name if id is None
        if self.id is None:
            # https://pypi.org/project/python-slugify/
            self.id = slugify(self.name, lowercase=False, regex_pattern=r"[^\w\s\-]")
        if self.short_name is None:
            self.short_name = self.name[:10]

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
            color=self.border_color,
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
    time: Optional[float] = None
    time_unit: Optional[str] = "h"
    max_score: Optional[float] = 100.0
    score_unit: Optional[str] = "%"
    
@dataclass_json
@dataclass
class CompetenceArea(CompetenceElement):
    """
    Represents a specific area within a competence aspect, containing various facets.

    Attributes:
        facets (List[CompetenceFacet]): A list of CompetenceFacet objects representing individual facets of this area.
    """

    facets: List[CompetenceFacet] = field(default_factory=list)


@dataclass_json
@dataclass
class CompetenceAspect(CompetenceElement):
    """
    Represents a broader category of competence, which includes various areas.

    Attributes:
        areas (List[CompetenceArea]): A list of CompetenceArea objects representing individual areas of this aspect.
    """

    areas: List[CompetenceArea] = field(default_factory=list)
    credits: Optional[int] = None


@dataclass_json
@dataclass
class CompetenceLevel(CompetenceElement):
    """
    Defines a specific level of competence within the framework.

    Attributes:
        level (int): level number starting from 1 as the lowest and going up to as many level as defined for the CompetenceTree
        icon(str): the name of a google mdi icon to be shown for this level
        utf8_icon(str): utf-8 char string to be used as icon
    """

    level: int = 1
    icon: Optional[str] = None
    utf8_icon: Optional[str] = None


@dataclass_json
@dataclass
class CompetenceTree(CompetenceElement, YamlAble["CompetenceTree"]):
    """
    Represents the entire structure of competencies, including various aspects and levels.

    Attributes:
        lookup_url (Optional[str]): Optional URL for additional information.
        total_levels (int): Total number of levels in the competence hierarchy.
        stacked_levels (Optional[bool]): Indicates whether the levels are stacked.
        aspects (List[CompetenceAspect]): A list of CompetenceAspect objects.
        levels (List[CompetenceLevel]): A list of CompetenceLevel objects.
        element_names (Dict[str, str]): A dictionary holding the names for tree, aspects, facets, and levels.  The key is the type ("tree", "aspect", "facet", "level").
        ring_specs (Dict[str, RingSpec]): Specifications for the rings in the donut chart.
        total_elements (Dict[str, int]): A dictionary holding the total number of elements for each type (aspects, areas, facets).
    """

    lookup_url: Optional[str] = None
    total_levels: int = field(init=False)
    stacked_levels: Optional[bool] = False
    aspects: List[CompetenceAspect] = field(default_factory=list)
    levels: List[CompetenceLevel] = field(default_factory=list)
    element_names: Dict[str, str] = field(default_factory=dict)
    ring_specs: Dict[str, RingSpec] = field(default_factory=dict)
    total_elements: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """
        initalize the path variables of my hierarchy
        """
        super().__post_init__()
        self.total_elements = {"aspects": 0, "areas": 0, "facets": 0}
        self.update_paths()
        self.calculate_ring_specs("empty")

    def calculate_ring_specs(self, text_mode: str):
        """
        calculate the ring specifications
        """
        inner_ratio = 0.0
        circle_ratio = 1 / (self.total_levels * 2 + 1)
        outer_ratio = circle_ratio
        if not "tree" in self.ring_specs:
            self.ring_specs["tree"] = RingSpec(
                text_mode=text_mode, inner_ratio=0.0, outer_ratio=circle_ratio
            )
        # loop over ring levels
        for rl in ["aspect", "area", "facet"]:
            inner_ratio = outer_ratio
            outer_ratio = outer_ratio + circle_ratio * 2
            if not rl in self.ring_specs:
                self.ring_specs[rl] = RingSpec(
                    text_mode=text_mode,
                    inner_ratio=inner_ratio,
                    outer_ratio=outer_ratio,
                )

    def update_paths(self):
        """
        update my paths
        """
        self.path = self.id
        self.total_levels = 1
        self.elements_by_path = {self.path: self}
        # Loop through each competence aspect and set their paths and parent references
        for aspect in self.aspects:
            aspect.competence_tree = self
            aspect.path = f"{self.id}/{aspect.id}"
            self.elements_by_path[aspect.path] = aspect
            self.total_elements["aspects"] = self.total_elements["aspects"] + 1
            self.total_levels = 2
            for area in aspect.areas:
                self.total_levels = 3
                area.competence_tree = self
                area.aspect = aspect
                area.path = f"{self.id}/{aspect.id}/{area.id}"
                self.elements_by_path[area.path] = area
                self.total_elements["areas"] = self.total_elements["areas"] + 1
                for facet in area.facets:
                    self.total_levels = 4
                    facet.competence_tree = self
                    facet.area = area
                    facet.path = f"{self.id}/{aspect.id}/{area.id}/{facet.id}"
                    self.elements_by_path[facet.path] = facet
                    self.total_elements["facets"] = self.total_elements["facets"] + 1

    @classmethod
    def required_keys(cls) -> Tuple:
        keys = {"name", "id", "url", "description", "aspects"}
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

        element = None
        if path not in self.elements_by_path:
            msg = f"invalid path {path}"
            if not lenient:
                raise ValueError(msg)
        else:
            element = self.elements_by_path.get(path)
        return element

    @property
    def total_valid_levels(self) -> int:
        """
        Calculate the total number of levels excluding
        levels with a level of 0.

        Returns:
            int: The total number of valid levels.
        """
        level_count = len([level for level in self.levels if level.level != 0])
        return level_count

    def get_level_color(self, achievement_level: int) -> Optional[str]:
        """
        Retrieve the color associated with a specific achievement level.

        Args:
            achievement_level (int): The level of achievement to get the color for.

        Returns:
            Optional[str]: The color code associated with the given level, or None if not found.
        """
        for level in self.levels:
            if level.level == achievement_level:
                return level.color_code
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
        level_items = [(level.color_code, level.name) for level in self.levels]
        svg.add_legend_column(
            level_items,
            self.element_names.get("level", "Level"),
            x_start,
            y,
            box_width,
            box_height,
        )
        max_name_width=5
        if self.levels:
            max_name_width=max(svg.get_text_width(level.name) for level in self.levels)
        # Calculate the x position for the aspect legend based on the width of the level legend
        x_aspect_start = (
            x_start
            + box_width
            + padding
            + max_name_width
            + padding
        )

        # Add the competence aspect legend
        aspect_items = [(aspect.color_code, aspect.name) for aspect in self.aspects]
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
    level: Optional[int] = None
    score: Optional[float] = None
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
    def area_id(self):
        parts = self.path.split("/")
        return parts[2] if len(parts) > 2 else None

    @property
    def facet_id(self):
        parts = self.path.split("/")
        return parts[3] if len(parts) > 3 else None


@lod_storable
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

    def __post_init__(self):
        self.achievements_by_path = {}
        if self.achievements:
            for achievement in self.achievements:
                self.achievements_by_path[achievement.path] = achievement

    @classmethod
    def required_keys(cls):
        keys = {"achievements"}
        return keys

    @property
    def main_id(self):
        main_id = self.learner_id
        return main_id

    @property
    def file_name(self):
        file_name = slugify(
            self.learner_id, lowercase=False, regex_pattern=r"[^\w\s\-]"
        )
        return file_name

    def add_achievement(self, new_achievement):
        self.achievements.append(new_achievement)
        self.achievements_by_path[new_achievement.path] = new_achievement

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

    def __init__(self, competence_tree: CompetenceTree, svg: SVG = None):
        """
        constructor
        """
        self.competence_tree = competence_tree
        self.svg = svg

    @property
    def main_id(self):
        main_id = self.competence_tree.id
        return main_id

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
                            cls.handle_markup_issue(
                                filename, definition_text, ex, markup
                            )
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
            data = json.loads(text)
            return data
        elif markup == "yaml":
            data = yaml.safe_load(text)
            return data
        else:
            raise ValueError(f"Unsupported markup format: {markup}")

    @classmethod
    def handle_markup_issue(cls, name: str, definition_string: str, ex, markup: str):
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
        cls,
        name: str,
        definition_string: str,
        content_class,
        markup: str = "json",
        debug: bool = False,
    ) -> Any:
        """
        Load a DynamicCompetenceMap or Learner instance from a definition string (either JSON or YAML).

        Args:
            name (str): A name identifier for the data source.
            definition_string (str): The string content of the definition.
            content_class (dataclass_json): The class which will be instantiated with the parsed data.
            markup (str): The markup format of the data. Defaults to 'json'. Supported values are 'json' and 'yaml'.
            debug(bool): if True supply a JSON dump of the data in /tmp/{name}.json
        Returns:
            DynamicCompetenceMap: An instance of DynamicCompetenceMap loaded with the parsed data.

        Raises:
            ValueError: If there's an error in parsing the data.
        """
        try:
            data = cls.parse_markup(definition_string, markup)
            if debug:
                # Save the parsed data to a JSON file in /tmp directory
                debug_file_path = os.path.join("/tmp", f"{name}.json")
                with open(debug_file_path, "w") as debug_file:
                    json.dump(data, debug_file, indent=2, default=str)
            content = content_class.from_dict(data)
            if isinstance(content, CompetenceTree):
                return DynamicCompetenceMap(content)
            else:
                return content
        except Exception as ex:
            cls.handle_markup_issue(name, definition_string, ex, markup)
