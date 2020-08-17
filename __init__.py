import gui
reload(gui)

def display(dock=True):
    ui = gui.SetDrivenKeyToolBoxGui()
    ui.show(dock)