from macau_gui_client import prepare_gui
from tests.common import WindowMock, DisplayMock


def test_prepare_gui():
    gui = prepare_gui(DisplayMock, WindowMock)
    assert type(gui.menu_window.window) == WindowMock
    assert type(gui.game_window.window) == WindowMock
    assert len(gui.tasks) == 4
