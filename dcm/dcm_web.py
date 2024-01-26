"""
Created on 2024-01-26

@author: wf
"""
from nicegui import ui
from nicegui.events import GenericEventArguments

from dcm.dcm_core import CompetenceTree, RingSpec


class RingSpecView:
    """
    show a single ring specification
    """

    def __init__(
        self, parent, ring_level: str, ringspec: RingSpec, throttle: float = 0.1
    ):
        """
        construct me
        """
        self.parent = parent
        self.ring_level = ring_level
        self.ringspec = ringspec
        self.change_enabled = False
        self.throttle = throttle
        self.setup_ui()

    def setup_ui(self):
        """
        setup the user interface
        """
        with self.parent.grid:
            self.inner_ratio_slider = (
                ui.slider(min=0, max=1.0, step=0.01, value=self.ringspec.inner_ratio)
                .props("label-always")
                .on(
                    "update:model-value",
                    self.on_inner_ratio_change,
                    throttle=self.throttle,
                )
            )
            self.outer_ratio_slider = (
                ui.slider(min=0, max=1.0, step=0.01, value=self.ringspec.outer_ratio)
                .props("label-always")
                .on(
                    "update:model-value",
                    self.on_outer_ratio_change,
                    throttle=self.throttle,
                )
            )
            selection = ["empty", "curved", "horizontal", "angled"]
            self.text_mode_select = self.parent.webserver.add_select(
                self.ring_level,
                selection,
                value=self.ringspec.text_mode,
                on_change=self.on_text_mode_change,
            )

    def update(self, rs: RingSpec):
        """
        update the ring specification to be modified by this ui
        """
        self.ringspec = rs
        self.change_enabled = False
        self.text_mode_select.value = rs.text_mode
        self.inner_ratio_slider.value = round(rs.inner_ratio, 2)
        self.outer_ratio_slider.value = round(rs.outer_ratio, 2)
        self.change_enabled = True

    def on_inner_ratio_change(self, gev: GenericEventArguments):
        """
        Handle changes in the inner_ratio slider.
        """
        if self.change_enabled:
            self.ringspec.inner_ratio = gev.args
            self.parent.on_change()

    def on_outer_ratio_change(self, gev: GenericEventArguments):
        """
        Handle changes in the outer_ratio slider.
        """
        if self.change_enabled:
            self.ringspec.outer_ratio = gev.args
            self.parent.on_change()

    async def on_text_mode_change(self, args):
        """
        handle changes in the text_mode
        """
        # ignore changes if change_enabled is not active
        if not self.change_enabled:
            return
        new_text_mode = args.value
        if new_text_mode != self.ringspec.text_mode:
            self.ringspec.text_mode = new_text_mode
        self.parent.on_change()


class RingSpecsView:
    """
    show a list of ringspecs
    """

    def __init__(self, webserver):
        self.webserver = webserver
        # ringspec views
        self.rsv = {}
        self.setup_ui()

    def setup_ui(self):
        """
        setup the user interface
        """
        with ui.expansion("",icon="settings") as self.expansion:
            levels=["tree", "aspect", "area", "facet"]
            with ui.row():
                ui.label("symmetry:")
                self.symmetry_radio = ui.radio(["count","time","score"], value=None).props('inline')
            with ui.row():
                ui.html("<hr>")
            with ui.grid(columns=3, rows=4) as self.grid:
                inner_ratio = 0
                outer_ratio = 1 / 7
                for rl in levels:
                    rs = RingSpec(
                        text_mode="empty",
                        inner_ratio=round(inner_ratio, 2),
                        outer_ratio=round(outer_ratio, 2),
                    )
                    self.rsv[rl] = RingSpecView(self, rl, rs)
                    inner_ratio = outer_ratio
                    outer_ratio = outer_ratio + 2 / 7

    def update_rings(self, ct: CompetenceTree):
        """
        update the ring specifications
        """
        for rl in ["tree", "aspect", "area", "facet"]:
            self.rsv[rl].update(ct.ring_specs[rl])

    def on_change(self):
        """
        if a ring spec trigger update
        """
        self.webserver.on_update_ringspecs()
