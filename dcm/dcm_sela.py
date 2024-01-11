"""
Created on 2024-01-10

@author: wf
"""
from ngwidgets.progress import NiceguiProgressbar
from ngwidgets.webserver import NiceGuiWebserver
from nicegui import ui

from dcm.dcm_core import Achievement, CompetenceTree, Learner


class ButtonRow:
    """
    A button row for selecting competence levels
    to document achievements from  a CompetenceTree.
    """

    def __init__(
        self,
        sela: "SelfAssessment",
        competence_tree: CompetenceTree,
        achievement: Achievement = None,
    ):
        """
        Construct a button row for the competence levels of the given CompetenceTree.

        Args:
            sela (SelfAssessment): The SelfAssessment instance.
            competence_tree (CompetenceTree): The Competence Tree to display buttons for.
            achievement (Achievement): The current achievement of the learner.
        """
        self.sela = sela
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
            for level in self.competence_tree.competence_levels:
                button = ui.button(
                    level.name,
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
        self.set_button_states(self.achievement)
        # refresh the ui
        self.row.update()
        # show achievement_view
        step = 1 if self.achievement.level else 0
        self.sela.update_achievement_view(step)


class SelfAssessment:
    """
    Self assessment for CompetenceTree
    """

    def __init__(
        self,
        webserver: NiceGuiWebserver,
        competence_tree: CompetenceTree,
        learner: Learner,
        debug: bool = False,
    ):
        """
        initialize the self assessment
        """
        self.webserver = webserver
        self.competence_tree = competence_tree
        self.learner = learner
        self.debug = debug
        self.achievement_index = 0
        # do we need setup the achievements?
        if self.learner.achievements is None:
            self.learner.achievements = []
            self.setup_achievements()
        self.setup_ui()
        self.update_achievement_view()

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
        competence_aspects = self.competence_tree.competence_aspects
        for aspect_code, aspect in competence_aspects.items():
            for facet in aspect.facets:
                # Construct the path for the facet
                path: str = f"{self.competence_tree.id}/{aspect_code}/{facet.id}"

                # Create a new Achievement instance with the constructed path
                new_achievement = Achievement(
                    path=path,
                )
                self.learner.achievements.append(new_achievement)

    def get_index_str(self) -> str:
        index_str = f"{self.achievement_index+1:2}/{self.total:2}"
        return index_str

    def setup_ui(self):
        """
        display my competence Tree elements
        """
        self.total = len(self.learner.achievements)
        self.progress_bar = NiceguiProgressbar(
            total=self.total, desc="self assessment", unit="facets"
        )
        self.progress_bar.reset()
        with ui.row():
            ui.button("", icon="arrow_back", on_click=lambda _args: self.step(-1))
            with ui.card() as self.achievement_view:
                self.index_view = ui.label(self.get_index_str())
                self.markdown_view = ui.markdown()
                self.button_row = ButtonRow(
                    self, self.competence_tree, self.current_achievement
                )
            ui.button("", icon="arrow_forward", on_click=lambda _args: self.step(1))

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
        self.progress_bar.update_value(count)

    async def step(self, step: int = 0):
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
            self.index_view.text = self.get_index_str()
            achievement = self.current_achievement
            self.button_row.achievement = achievement
            self.button_row.set_button_states(achievement)
            competence_element = self.competence_tree.lookup_by_path(achievement.path)
            if not competence_element:
                ui.notify("invalid path: {achievement.path}")
                self.markdown_view.content = f"⚠️ {achievement.path}"
            else:
                self.markdown_view.content = competence_element.description
        else:
            ui.notify("Done!")
