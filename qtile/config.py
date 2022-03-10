# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List  # noqa: F401

from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
from libqtile.log_utils import logger

mod = "mod4"
hyper = "mod3"
terminal = guess_terminal()


def switch_to_screen_or_pull_group(qtile, g):
    group = qtile.groups_map[g]

    #if group is visible, switch to that screen
    if group.screen:
        qtile.cmd_to_screen(group.screen.index)
    else:
        qtile.current_screen.set_group(group)


def move_window_and_switch_to_group_or_screen(qtile, g):
    group = qtile.groups_map[g]

    qtile.current_window.cmd_togroup(g)

    #if group is visible, switch to that screen
    if group.screen:
        qtile.cmd_to_screen(group.screen.index)
    else:
        qtile.current_screen.set_group(group)


def next_free_nonempty_group(qtile):
    now = False
    for g in qtile.groups*2:
        if g == qtile.current_group:
            now = True
        if not g.screen and g.windows:
            if now:
                g.cmd_toscreen()
                return


def prev_free_nonempty_group(qtile):
    now = False
    for g in reversed(qtile.groups*2):
        if g == qtile.current_group:
            now = True
        if not g.screen and g.windows:
            if now:
                g.cmd_toscreen()
                return


def next_free_empty_group(qtile):
    now = False
    for g in qtile.groups*2:
        if g == qtile.current_group:
            now = True
        if not g.screen and not g.windows:
            if now:
                g.cmd_toscreen()
                return


# TODO: Generalize function, to not depend on specific layout
def move_right(qtile):
    if qtile.current_window:
        max_columns = qtile.current_layout.num_columns
        num_columns = len(qtile.current_layout.columns)

        # if not rightmost window, then shuffle right
        for w in qtile.current_window.group.windows:
            if w._x > qtile.current_window._x:
                qtile.current_layout.cmd_shuffle_right()
                return

        ## if not on the last column then shuffle right
        #if qtile.current_layout.current < num_columns - 1:
        #    qtile.current_layout.cmd_shuffle_right()

        # create new column if not full
        if num_columns < max_columns:
            if len(qtile.current_layout.columns[num_columns -1]) > 1:
                qtile.current_layout.cmd_shuffle_right()
                return

        # otherwise move to next screen

        w = qtile.current_window
        s = w.group.screen.index + 1
        if s >= len(qtile.screens):
            s = 0
        target_screen = qtile.screens[s]
        w.cmd_toscreen(s)
        qtile.cmd_to_screen(s)
        w.cmd_focus()

        # Try to insert at the right place
        max_columns = qtile.current_layout.num_columns
        num_columns = len(qtile.current_layout.columns)

        if num_columns == 1:
            if len(qtile.current_layout.cc.clients) >= 2:
                qtile.current_layout.cmd_shuffle_left()
            return

        elif num_columns >= max_columns:
            if w in target_screen.group.layout.columns[0].clients:
                return
            target_screen.group.layout.columns[0].add(w)
            target_screen.group.layout.columns[num_columns - 1].remove(w)
            if len(target_screen.group.layout.columns[num_columns -1].clients) == 0:
                target_screen.group.layout.remove_column(target_screen.group.layout.columns[num_columns -1])

        elif num_columns < max_columns:
            target_screen.group.layout.swap_column(-1, 0)


# TODO: Generalize function, to not depend on specific layout
def move_left(qtile):
    if qtile.current_window:
        max_columns = qtile.current_layout.num_columns
        num_columns = len(qtile.current_layout.columns)
        if num_columns < max_columns:
            if qtile.current_layout.current > 0:
                qtile.current_layout.cmd_shuffle_left()
                return
            elif len(qtile.current_layout.columns[0]) > 1:
                qtile.current_layout.cmd_shuffle_left()
                return
        for w in qtile.current_window.group.windows:
            if w._x < qtile.current_window._x:
                qtile.current_layout.cmd_shuffle_left()
                return
        w = qtile.current_window
        s = w.group.screen.index - 1
        w.cmd_toscreen(s)
        qtile.cmd_to_screen(s)
        w.cmd_focus()


def focus_right(qtile):
    if qtile.current_window:
        for w in qtile.current_window.group.windows:
            if w._x > qtile.current_window._x:
                qtile.current_layout.cmd_right()
                return
    qtile.cmd_next_screen()
    if qtile.current_window:
        for w in qtile.current_window.group.windows:
            if w._x < qtile.current_window._x:
                w.cmd_focus()


def focus_left(qtile):
    if qtile.current_window:
        for w in qtile.current_window.group.windows:
            if w._x < qtile.current_window._x:
                qtile.current_layout.cmd_left()
                return
    qtile.cmd_prev_screen()
    if qtile.current_window:
        for w in qtile.current_window.group.windows:
            if w._x > qtile.current_window._x:
                w.cmd_focus()


keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.function(focus_left), desc="Move focus to left"),
    Key([mod], "l", lazy.function(focus_right), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "Left", lazy.function(focus_left), desc="Move focus to left"),
    Key([mod], "Right", lazy.function(focus_right), desc="Move focus to right"),
    Key([mod], "Down", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "Up", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.function(move_left), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.function(move_right), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    Key([mod, "shift"], "Left", lazy.function(move_left), desc="Move window to the left"),
    Key([mod, "shift"], "Right", lazy.function(move_right), desc="Move window to the right"),
    Key([mod, "shift"], "Down", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "Up", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod, "control"], "Left", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([mod, "control"], "Right", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([mod, "control"], "Down", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "Up", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.function(next_free_empty_group), desc="Next free empty group"),
    Key([mod], "m", lazy.window.toggle_minimize()),
    Key([mod], "f", lazy.window.toggle_fullscreen()),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "BackSpace", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([hyper], "d", lazy.spawn("rofi -show run"), desc="Spawn a command using a prompt widget"),
    Key([hyper], "h", lazy.prev_screen(), desc="Previous monitor"),
    Key([hyper], "l", lazy.next_screen(), desc="Next monitor"),
    Key([hyper], "j", lazy.function(next_free_nonempty_group), desc="Next free group"),
    Key([hyper], "k", lazy.function(prev_free_nonempty_group), desc="Previous free group"),
    Key([hyper], "Left", lazy.prev_screen(), desc="Previous monitor"),
    Key([hyper], "Right", lazy.next_screen(), desc="Next monitor"),
    Key([hyper], "Down", lazy.function(next_free_nonempty_group), desc="Next free group"),
    Key([hyper], "Up", lazy.function(prev_free_nonempty_group), desc="Previous free group"),
]

groups = [
    Group("q",
        spawn=[
            "qutebrowser",
            terminal
        ],
        screen_affinity=0,
    ),
    Group("w",
        screen_affinity=1,
    ),
    Group("e",
        screen_affinity=2,
    ),
    Group("r",),
    Group("t"),
    Group("y"),
    Group("u"),
    Group("i"),
    Group("o"),
    Group("p",
        matches=[
            Match(title=["Private"])
        ],
    )
]

for i in groups:
    keys.extend(
        [
            # mod1 + letter of group = switch to group
            Key(
                [mod],
                i.name,
                #lazy.group[i.name].toscreen(),
                lazy.function(switch_to_screen_or_pull_group, i.name),
                desc="Switch to group {}".format(i.name),
            ),
            # mod1 + shift + letter of group = switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.function(move_window_and_switch_to_group_or_screen, i.name),
                desc="Switch to & move focused window to group {}".format(i.name),
            ),
        ]
    )

layouts = [
    layout.Columns(border_focus_stack=["#d75f5f", "#8f3d3d"],
                   border_width=4,
                   border_on_single=True,
                   num_columns=2,
                   wrap_focus_columns=False,
                   insert_position=1,
    ),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    #layout.Stack(num_stacks=3),
    #layout.Bsp(),
    #layout.Matrix(),
    #layout.MonadTall(),
    #layout.MonadWide(),
    #layout.RatioTile(),
    #layout.Tile(),
    #layout.TreeTab(),
    #layout.VerticalTile(),
    #layout.Zoomy(),
]


widget_defaults = dict(
    font="mono bold",
    fontsize=12,
    padding=3,
    foreground="#999999",
)
extension_defaults = widget_defaults.copy()

screens = []

net = widget.Net(
    format="Net:{down} ↓↑{up}",
    #prefix="M"
)

net.allowed_prefixes=["k", "M", "G", "T", "P", "E", "Z", "Y"]
net.units=list(map(lambda p: p + net.base_unit, net.allowed_prefixes))
net.byte_multiplier=0.001

for s in range(5):
    screens.append(Screen(
        bottom=bar.Bar(
            [
                widget.CurrentLayoutIcon(),
                #widget.CurrentLayout(),
                widget.GroupBox(),
                #widget.WindowName(),
                widget.TaskList(markup_focused='<span color="#cccccc">{}</span>'),
                widget.TextBox("Mem:"),
                widget.Memory(
                    measure_mem="G",
                    measure_swap="G"
                ),
                widget.Sep(),
                widget.CPU(
                    format="CPU:{load_percent:>3.0f}%"
                ),
                ##widget.CPUGraph(),
                #widget.ThermalZone(),
                widget.Sep(),
                widget.Wlan(
                    interface="wlp0s20f3"
                ),
                widget.Sep(),
                net,
                #widget.Net(
                #    format="Net:{down} ↓↑{up}",
                #    #prefix="M"

                #),
                ##widget.NetGraph(),
                widget.Sep(),
                widget.DF(),
                widget.Sep(),
                widget.CheckUpdates(),
                widget.Sep(),
                widget.TextBox("Vol:"),
                widget.PulseVolume(),
                widget.Sep(),
                widget.Battery(
                    charge_char="+",
                    discharge_char="-",
                    format="Bat: {char}{percent:2.0%}"
                ),
                widget.Sep(),
                widget.Spacer(length=10),
                #widget.Systray(),
                widget.Clock(
                    format="%a %d-%m-%Y %H:%M",
                    foreground="#ffffff"
                ),
            ],
            24,
            # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
    ))

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: List
follow_mouse_focus = False
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True


# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = False

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
