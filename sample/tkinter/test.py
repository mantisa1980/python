import Tkinter as tk
#from Tkinter import *
#from BisonClient import BisonClient


g_systems = {
    'login':['LOGIN'],
	'lobbylogin':['LOBBYLOGIN'],
	'echo':['ECHO','ECHO1'],
}
g_buttons=list()

def change_system(system):
    global g_current_system
    global g_buttons
    global root, app
    g_current_system = system
    print("change system to", g_current_system)
    for widget in g_buttons:
        print("destorying widgets", widget)
        widget.pack_forget()
        widget.destroy()
    #app.update()
    #root.update()
    
    g_buttons = list()
    for cmd in g_systems[system]:
        btn = tk.Button(root, text=cmd, command=lambda: trigger_command(cmd))
        btn.pack(side=tk.LEFT)
        g_buttons.append(btn)
    #app.update()
    root.update()

def trigger_command(command):
    global g_current_command
    g_current_command = command
    print("trigger command", g_current_command)

g_width=40
g_height=30
g_buttons = list()
g_current_system=None
g_current_command=None

# main frame
root = tk.Tk()
app = tk.Frame(root)
app.pack()

### label
hello = tk.Label(root, text="Hello Tk!", width=g_width, height=g_height)
hello.pack()

############### option list

variable = tk.StringVar(root)
variable.set('Ark System List')
opt = tk.OptionMenu(root, variable, *g_systems.keys(), command=change_system)
opt.config(width=30, font=('Helvetica', 12))
opt.pack()

change_system("echo")
root.mainloop()
