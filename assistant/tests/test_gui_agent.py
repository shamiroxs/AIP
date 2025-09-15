from assistant.agents.gui_agent import GUIAgent

gui = GUIAgent()

print(gui.open_app("gedit"))          # Open text editor
print(gui.focus_window("gedit"))      # Focus gedit window
print(gui.type_text("Hello from Leo")) # Type text
print(gui.key_press("Return"))        # Press Enter

##print(gui.open_url("https://debian.org")) # Open Debian site
#print(gui.screenshot("test.png"))     # Take screenshot
print(gui.list_windows())             # List open windows
