# -*- coding: utf-8 -*-
__author__ = 'duyhsieh'
import sys
if sys.version[0] == '3':
    import tkinter as tk
else:
    import Tkinter as tk
from functools import partial
#from BisonClient import BisonClient
import json

class Controller(object):
    def __init__(self, model, view):
        self.ark_command_buttons = dict()
        self.model = model
        self.view = view
    
    def on_command_click_event(self, system, command):
        resp = self.model.send_ark_command(system, command)
        self.view.on_response(resp)

    def on_custom_command_click_event(self, system, command, input_data):
        resp = self.model.send_ark_command(system, command, input_data=input_data)
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

    def send_ark_command(self, system, command, input_data=None):
        print("[Model] sending to system:[{}],command:[{}],data:\n{}".format(
            system, command, input_data))
        
        if input_data == None:
            print("Get default input data")
        else:
            print("use custom input data", input_data)
        return {'dummy':'test'}

class View(object):
    def __init__(self):
        self.ark_command_buttons = dict()
        self.reverse_command_table = dict()
        self.command_click_event_listeners = list()
        self.custom_command_click_event_listeners = list()

    def on_click_command_button(self, system, command):
        for listener in self.command_click_event_listeners:
            listener(system, command)

    def on_click_custom_command_button(self, inputbox_sys, inputbox_cmd, textbox_custom_cmd):
        # 1.0: get from line 1 and char position 0, and to tk.END ("end")
        system = inputbox_sys.get()
        command =inputbox_cmd.get()
        textbox_text = textbox_custom_cmd.get('1.0', tk.END).rstrip()
        if len(textbox_text) == 0:
            textbox_text = "{}"
        #print("clicking custom command button",  inputbox_sys.get(), inputbox_cmd.get(), textbox_text)
        try:
            json_data = json.loads(textbox_text)
        except:
            print("error parsing json", textbox_text)
            return

        for listener in self.custom_command_click_event_listeners:
            listener(system, command, json_data)

    def register_command_click_event(self, listener):
        self.command_click_event_listeners.append(listener)

    def register_custom_command_click_event(self, listener):
        self.custom_command_click_event_listeners.append(listener)

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
        outer_row=0
        window = tk.Tk()
        window.title('GUIClient')
        window.geometry('800x600')
        
        ########################  top status row
        label = tk.Label(window, text="Status...")
        label.grid(column=0,row=outer_row,columnspan=20)
        
        

        ######################## command button row
        outer_row+=1
        inner_column = 0
        for cmd in sorted(self.reverse_command_table.keys()):
            system = self.reverse_command_table[cmd]
            btn = tk.Button(window, text=cmd, command=partial(self.on_click_command_button, system, cmd))
            #btn.pack(side=tk.LEFT, ipadx=1, ipady=1) # internal padding
            btn.grid(column=inner_column, row=outer_row)
            inner_column+=1

        

        ######################## custom command row
        outer_row+=1
        label_custom_system_inputbox = tk.Label(window, text="Custom System")
        label_custom_system_inputbox.grid(column=0, row=outer_row)
        custom_system_inputbox = tk.Entry(window)
        custom_system_inputbox.grid(column=1,row=outer_row)

        label_custom_command_inputbox = tk.Label(window, text="Custom Command")
        label_custom_command_inputbox.grid(column=2, row=outer_row)
        custom_command_inputbox = tk.Entry(window)
        custom_command_inputbox.grid(column=3, row=outer_row)

        ######################## custom command input data row
        outer_row+=1
        label = tk.Label(window, text="Custom Command Data")
        label.grid(column=0,row=outer_row)
        
        custom_command_data_textbox = tk.Text(window)
        custom_command_data_textbox.grid(column=1,row=outer_row, columnspan=10)


        ######################## custom command submit button row
        outer_row+=1
        btn = tk.Button(window, text="SendCustom")
        btn['command'] = partial(
            self.on_click_custom_command_button, 
            custom_system_inputbox, 
            custom_command_inputbox,
            custom_command_data_textbox)
        btn.grid(column=2, row=outer_row)
        
        window.mainloop()

def main():
    model = Model()
    view = View()
    ctrl = Controller(model, view)

    total_commands = model.get_total_commands()
    for system, command_lst in total_commands.items():
        for command in command_lst:
            view.add_request_button(system, command)
    view.register_command_click_event(ctrl.on_command_click_event)
    view.register_custom_command_click_event(ctrl.on_custom_command_click_event)
    view.render()

if __name__ == "__main__":
    main()