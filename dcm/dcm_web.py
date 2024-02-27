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
        self.ringspec=ringspec
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
            selection = ["empty", "curved", "horizontal", "angled"]
            self.text_mode_select = self.parent.webserver.add_select(
                self.ring_level,
                selection,
                value=self.ringspec.text_mode,
                on_change=self.on_text_mode_change,
            )
            self.level_visible_checkbox = ui.checkbox("level").on(
                "click", self.on_level_visible_change
            )
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

    def on_level_visible_change(self):
        """ """
        self.ringspec.levels_visible = self.level_visible_checkbox.value
        self.parent.on_change()

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
        self.symmetry_mode=None
        self.symmetry_level=None

    def setup_ui(self):
        """
        setup the user interface
        """
        with ui.expansion("ring specs", icon="settings") as self.expansion:
            with ui.expansion("symmetry",icon="balance"):
                with ui.row():
                    self.symmetry_mode_radio = ui.radio(
                        ["count", "time", "score"], 
                        on_change=self.on_symmetry_change
                    ).props("inline")
                with ui.row():
                    self.symmetry_level_radio = ui.radio(
                        ["aspect", "area", "facet"], 
                        on_change=self.on_symmetry_change
                    ).props("inline")
            with ui.grid(columns=2, rows=8) as self.grid:
                inner_ratio = 0
                outer_ratio = 1 / 7
                levels = ["tree", "aspect", "area", "facet"]
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
        update the ring specifications based on the given competence tree
        """
        self.symmetry_level, self.symmetry_mode = ct.get_symmetry_spec()
        self.symmetry_level_radio.value=self.symmetry_level
        self.symmetry_mode_radio.value=self.symmetry_mode
        # set ct after changing radio buttions
        self.ct=ct
        for rl in ["tree", "aspect", "area", "facet"]:
            self.rsv[rl].update(ct.ring_specs[rl])

    def on_symmetry_change(self,args):
        """
        handle symmetry changes
        """
        if self.ct:       
            # get compentency tree symmetry settings
            # and the current ui radio button settings
            ct_symmetry_level, ct_symmetry_mode = self.ct.get_symmetry_spec()   
            self.symmetry_level=self.symmetry_level_radio.value
            self.symmetry_mode=self.symmetry_mode_radio.value
            # check whether the radio values are different from the ct values
            if (ct_symmetry_level != self.symmetry_level or ct_symmetry_mode != self.symmetry_mode):
                self.ct.set_symmetry_mode(self.symmetry_level,self.symmetry_mode)       
            pass
        self.on_change()
        
    def on_change(self):
        """
        if a ring spec trigger update
        """
        self.webserver.on_update_ringspecs()
