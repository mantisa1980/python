# -*- coding: utf-8 -*-
__author__ = 'duyhsieh'
import sys
if sys.version[0] == '3':
    import tkinter as tk
else:
    import Tkinter as tk
from functools import partial
#from BisonClient import BisonClient


class Controller(object):
    def __init__(self, model, view):
        self.ark_command_buttons = dict()
        self.model = model
        self.view = view
    
    def on_click_event(self, system, command, input_data):
        resp = self.model.send_ark_command(system, command, input_data)
        self.view.on_response(resp)


class Model(object):
    def __init__(self):
        self.total_commands = {
            'login':['LOGIN'],
            'lobbylogin':['LOBBYLOGIN'],
            'echo':['ECHO','ECHO1'],
        }

    def get_total_commands(self):
        return self.total_commands

    def send_ark_command(self, system, command, input_data):
        print("[Model] sending to system:[{}],command:[{}],data:\n{}".format(
            system, command, input_data))
        return {'dummy':'test'}

class View(object):
    def __init__(self):
        self.ark_command_buttons = dict()
        self.reverse_command_table = dict()
        self.command_click_event_listeners = list()

    def on_click_custom_command_button(self):
        print("clicking custom command button",  )
        pass

    def on_click_command_button(self, system, command):
        for listener in self.command_click_event_listeners:
            listener(system, command, {'todo':'input data'})

    def register_click_event(self, listener):
        self.command_click_event_listeners.append(listener)

    def add_request_button(self, system, command):
        if system not in self.ark_command_buttons:
            self.ark_command_buttons[system] = list()
        
        if command in self.reverse_command_table:
            command = command + '_' + system

        self.ark_command_buttons[system].append(command)

        self.reverse_command_table[command] = system

    def on_response(self, message):
        print("[View] setting display message", message)

    def render(self):
        window = tk.Tk()
        window.title('GUIClient')
        window.geometry('800x600')
        
        top_frame = tk.Frame(master=window,bg='yellow')
        label = tk.Label(master=top_frame, text="Status...")
        label.pack()
        top_frame.pack(side=tk.TOP)

        command_frame = tk.Frame(master=window, bg="blue")
        command_frame.pack(side=tk.LEFT, fill=tk.X)

        custom_command_frame = tk.Frame(master=window, bg="green")
        #custom_command_frame.pack(side=tk.LEFT)
        custom_command_frame.pack(side=tk.BOTTOM)

        for cmd in sorted(self.reverse_command_table.keys()):
            system = self.reverse_command_table[cmd]
            btn = tk.Button(master=command_frame, text=cmd, command=partial(self.on_click_command_button, system, cmd))
            btn.pack(side=tk.LEFT, ipadx=1, ipady=1) # internal padding

        #stextbox = tk.Text(master=command_frame)
            #textbox.pack(side=tk.LEFT)
        #textbox.pack(side=tk.BOTTOM)

        label_custom_system_inputbox = tk.Label(master=custom_command_frame, text="Custom System")
        label_custom_system_inputbox.pack(side=tk.LEFT)
        self.custom_system_inputbox = tk.Entry(custom_command_frame)
        self.custom_system_inputbox.pack(side=tk.LEFT)

        label_custom_command_inputbox = tk.Label(master=custom_command_frame, text="Custom Command")
        label_custom_command_inputbox.pack(side=tk.LEFT)
        self.custom_command_inputbox = tk.Entry(custom_command_frame)
        self.custom_command_inputbox.pack(side=tk.LEFT)

        btn = tk.Button(master=custom_command_frame, text="SendCustom", command=self.on_click_custom_command_button)
        btn.pack(side=tk.LEFT)
        
        window.mainloop()

def main():
    model = Model()
    view = View()
    ctrl = Controller(model, view)

    total_commands = model.get_total_commands()
    for system, command_lst in total_commands.items():
        for command in command_lst:
            view.add_request_button(system, command)
    view.register_click_event(ctrl.on_click_event)
    view.render()

if __name__ == "__main__":
    main()