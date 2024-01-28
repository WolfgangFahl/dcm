"""
Created on 2024-01-10

@author: wf
"""
import os
from datetime import datetime, timezone

from ngwidgets.progress import NiceguiProgressbar
from ngwidgets.webserver import NiceGuiWebserver
from ngwidgets.widgets import Link
from nicegui import ui

from dcm.dcm_core import (
    Achievement,
    CompetenceArea,
    CompetenceFacet,
    CompetenceTree,
    DynamicCompetenceMap,
    Learner,
)


class ButtonRow:
    """
    A button row for selecting competence levels
    to document achievements from  a CompetenceTree.
    """

    def __init__(
        self,
        assessment: "Assessment",
        competence_tree: CompetenceTree,
        achievement: Achievement = None,
    ):
        """
        Construct a button row for the competence levels of the given CompetenceTree.

        Args:
            assessment (Assessment): The Assessment instance.
            competence_tree (CompetenceTree): The Competence Tree to display buttons for.
            achievement (Achievement): The current achievement of the learner.
        """
        self.assessment = assessment
        self.competence_tree = competence_tree
        self.achievement = achievement
        self.setup_buttons()
        self.set_button_states(achievement)

    def setup_buttons(self):
        """
        Create buttons for each competence level defined in the CompetenceTree.
        """
        self.buttons = {}
        with ui.row() as self.row:
            for level in self.competence_tree.levels:
                # generate a button to represent the level
                button_label = level.name
                if level.utf8_icon:
                    button_label = f"{level.utf8_icon} {level.name}"
                button = ui.button(
                    button_label,
                    icon=level.icon,
                    color=level.color_code,
                    on_click=lambda _args, l=level.level: self.handle_selection(l),
                ).tooltip(level.description)
                self.buttons[level.level] = button

    def set_button_states(self, achievement: Achievement):
        """
        Set the state of buttons based on the given achievement.

        Args:
            achievement (Achievement): The current achievement of the learner.
        """
        # If no achievement or level is set, enable all buttons
        if achievement is None or achievement.level is None:
            for button in self.buttons.values():
                button.enable()
                button.visible = True
        else:
            # Enable only the button corresponding to the current level and disable others
            for level, button in self.buttons.items():
                if level == achievement.level:
                    button.enable()
                    button.visible = True
                else:
                    button.disable()
                    button.visible = False

    def handle_selection(self, selected_level: int):
        """
        handle the selected level

        Args:
            selected_level(int): the selected level
        """
        # Check if the same level is selected again,
        # then reset the selection
        if self.achievement.level == selected_level:
            self.achievement.level = None
        else:
            self.achievement.level = selected_level
            # Get the current time in UTC
            current_time_utc = datetime.now(timezone.utc)

            # Convert the current time to ISO format
            date_assessed_iso = current_time_utc.isoformat()

            # Assign it to self.achievement.date_assessed_iso
            self.achievement.date_assessed_iso = date_assessed_iso

        self.set_button_states(self.achievement)
        # refresh the ui
        self.row.update()
        # show achievement_view
        step = 1 if self.achievement.level else 0
        self.assessment.step(step)


class Assessment:
    """
    Assessment for CompetenceTree
    """

    def __init__(
        self,
        webserver: NiceGuiWebserver,
        dcm: DynamicCompetenceMap,
        learner: Learner,
        debug: bool = False,
    ):
        """
        initialize the assessment

        Args:
            webserver(NiceguiWebServer): the webserver context
            dcm(DynamicCompetenceMap): the competence map
            learner(Learner): the learner to get the self assessment for
            debug(bool): if True show debugging information
        """
        self.webserver = webserver
        self.debug = debug
        self.reset(dcm=dcm, learner=learner)
        self.setup_ui()

    def store(self) -> str:
        """
        Store the current state of
        the learner's achievements.

        Returns(str): the path to the file
        """
        file_path = None
        try:
            # Serialize the learner object to JSON
            learner_data_json = self.learner.to_json(indent=2)

            # Determine the file path for storing the learner's data
            filename = self.learner.file_name + ".json"
            file_path = os.path.join(
                self.webserver.server_config.storage_path, filename
            )

            # Write the serialized data to the file
            with open(file_path, "w") as file:
                file.write(learner_data_json)

            if self.debug:
                print(f"Learner data stored in {file_path}")

        except Exception as ex:
            self.webserver.handle_exception(ex, self.webserver.do_trace)
        return file_path

    def reset(
        self,
        dcm: DynamicCompetenceMap,
        learner: Learner,
    ):
        """
            (re)set the assessment

        Args:
            webserver(NiceguiWebServer): the webserver context
            dcm(DynamicCompetenceMap): the competence map
            learner(Learner): the learner to get the self assessment for
        """
        self.dcm = dcm
        self.competence_tree = dcm.competence_tree
        self.learner = learner
        self.achievement_index = 0
        # do we need setup the achievements?
        if self.learner.achievements is None:
            self.learner.achievements = []
            self.setup_achievements()
        self.total = len(self.learner.achievements)

    def clear(self):
        """
        clear the ui
        """
        self.container.clear()

    @property
    def current_achievement(self) -> Achievement:
        if self.achievement_index < 0 or self.achievement_index > len(
            self.learner.achievements
        ):
            raise ValueError(f"invalid achievement index {self.achievement_index}")
        achievement = self.learner.achievements[self.achievement_index]
        return achievement

    def setup_achievements(self):
        """
        Setup achievements based on the competence tree.

        This method iterates over the competence aspects and their facets,
        constructs a path for each facet, and creates an Achievement instance
        based on the path. These achievements are then added to the learner's
        achievements list.
        """
        for aspect in self.competence_tree.aspects:
            for area in aspect.areas:
                self.add_achievement(area.path)
                for facet in area.facets:
                    # Construct the path for the facet
                    self.add_achievement(facet.path)

    def add_achievement(self, path):
        # Create a new Achievement instance with the constructed path
        new_achievement = Achievement(
            path=path,
        )
        self.learner.add_achievement(new_achievement)

    def get_index_str(self) -> str:
        """
        get the current achievement index
        """
        index_str = f"{self.achievement_index+1:2}/{self.total:2}"
        return index_str

    def setup_ui(self):
        """
        display my competence Tree elements
        """
        with ui.grid(columns=1).classes("w-full") as self.container:
            self.progress_bar = NiceguiProgressbar(
                total=self.total, desc="self assessment", unit="facets"
            )
            self.progress_bar.reset()
            facet_element_name = (
                self.competence_tree.element_names.get("facet") or "facet"
            )
            area_element_name = self.competence_tree.element_names.get("area") or "area"

            with ui.row() as self.navigation_row:
                ui.button(
                    "", icon="first_page", on_click=lambda _args: self.goto(0)
                ).tooltip("to first")
                ui.button(
                    "", icon="fast_rewind", on_click=lambda _args: self.step_area(-1)
                ).tooltip(f"previous {area_element_name}")
                ui.button(
                    "", icon="arrow_back", on_click=lambda _args: self.step(-1)
                ).tooltip(f"previous {facet_element_name}")
                ui.button(
                    "", icon="arrow_forward", on_click=lambda _args: self.step(1)
                ).tooltip(f"next {facet_element_name}")
                ui.button(
                    "", icon="fast_forward", on_click=lambda _args: self.step_area(1)
                ).tooltip(f"next {area_element_name}")
                ui.button(
                    "",
                    icon="last_page",
                    on_click=lambda _args: self.goto(self.total - 1),
                ).tooltip("to last")
            with ui.row() as self.button_row_row:
                self.button_row = ButtonRow(
                    self, self.competence_tree, self.current_achievement
                )
            with ui.row() as self.card_row:
                with ui.card() as self.achievement_view:
                    self.index_view = ui.label(self.get_index_str())
                    self.link_view = ui.html()
                    self.markdown_view = ui.markdown()

    def show_progress(self):
        """
        Update the progress bar based on the
        number of achievements with a non-None level value.
        """
        count = sum(
            1
            for achievement in self.learner.achievements
            if achievement.level is not None
        )
        self.progress_bar.total = self.total
        self.progress_bar.update_value(count)

    async def step_area(self, area_step: int):
        """
        Step towards the area given in area_step.
        For example, 1 means next area, -1 means previous area.
        """
        if area_step == 0:
            return  # No movement required

        direction = 1 if area_step > 0 else -1
        area_count = 0

        # Start with the next/previous achievement based on the direction
        new_index = self.achievement_index + direction

        # Loop through achievements until the desired area count is reached
        while 0 <= new_index < len(self.learner.achievements):
            achievement = self.learner.achievements[new_index]
            element = self.competence_tree.lookup_by_path(achievement.path)

            if isinstance(element, CompetenceArea):
                area_count += 1
                if area_count == abs(area_step):
                    # Found the required area, update the index
                    await self.goto(new_index)
                    return

            # Move to the next/previous achievement
            new_index += direction

        # Notify if no more areas in the direction
        with self.container:
            ui.notify("Reached the end of the areas in this direction.")

    def goto(self, index: int):
        self.achievement_index = index
        self.step(0)

    def step(self, step: int = 0):
        """
        step with the achievement view
        """
        self.update_achievement_view(step)

    def update_achievement_view(self, step: int = 0):
        """
        display the active achievement as the step indicates
        """
        self.show_progress()
        if self.achievement_index + step < 0:
            ui.notify("first achievement reached!")
            step = 0
        if self.achievement_index + step < len(self.learner.achievements):
            self.achievement_index += step
        else:
            ui.notify("Done!")
        self.update_current_achievement_view()

    def update_current_achievement_view(self):
        """
        show the current achievement
        """
        self.index_view.text = self.get_index_str()
        achievement = self.current_achievement
        self.store()
        self.webserver.render_dcm(
            self.dcm,
            self.learner,
            selected_paths=[achievement.path],
            clear_assessment=False,
        )
        self.button_row.achievement = achievement
        self.button_row.set_button_states(achievement)
        competence_element = self.competence_tree.lookup_by_path(achievement.path)
        if not competence_element:
            ui.notify(f"invalid path: {achievement.path}")
            self.markdown_view.content = f"⚠️ {achievement.path}"
        else:
            if hasattr(competence_element, "path"):
                if competence_element.url:
                    link = Link.create(competence_element.url, competence_element.path)
                else:
                    link = competence_element.path
            else:
                link = "⚠️ - competence element path missing"
            self.link_view.content = link
            description = competence_element.description or ""
            if isinstance(competence_element, CompetenceArea):
                aspect = competence_element.aspect
                description = f"### {aspect.name}\n\n**{competence_element.name}**:\n\n{description}"
            if isinstance(competence_element, CompetenceFacet):
                area = competence_element.area
                description = f"### {area.name}\n\n**{competence_element.name}**:\n\n{description}"
            self.markdown_view.content = description
