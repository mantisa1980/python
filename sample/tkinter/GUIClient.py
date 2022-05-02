# -*- coding: utf-8 -*-
__author__ = 'duyhsieh'
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
        self.ark_request_buttons = dict()
        self.click_event_listeners = list()

    def on_click_button(self, system, command):
        for listener in self.click_event_listeners:
            listener(system, command, {'todo':'input data'})
    
    def register_click_event(self, listener):
        self.click_event_listeners.append(listener)

    def create_request_button(self, system, command):
        if system not in self.ark_request_buttons:
            self.ark_request_buttons[system] = list()
        self.ark_request_buttons[system].append(command)

    def on_response(self, message):
        print("[View] setting display message", message)

    def render(self):
        root = tk.Tk()
        app = tk.Frame(root)

        for system, command_lst in self.ark_request_buttons.items():
            for cmd in command_lst:
                btn = tk.Button(root, text=cmd, command=partial(self.on_click_button, system, cmd))
                btn.pack(side=tk.LEFT)
        root.mainloop()

def main():
    model = Model()
    view = View()
    ctrl = Controller(model, view)

    total_commands = model.get_total_commands()
    for system, command_lst in total_commands.items():
        for command in command_lst:
            view.create_request_button(system, command)
    view.register_click_event(ctrl.on_click_event)
    view.render()

if __name__ == "__main__":
    main()