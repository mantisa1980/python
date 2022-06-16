import copy
class EventRule(object):
    def __init__(self, rule_type, config):
        self.rule_type = rule_type
        self.config = config

    def apply_addition(self, source):
        for k in source.keys():
            if k in self.config:
                source[k]+=self.config[k]

    def apply_multiplication(self, source):
        for k in source.keys():
            if k in self.config:
                source[k] *= self.config[k]

    def apply_merge(self, source):
        source.update(self.config)

class Composer(object):
    def __init__(self):
        self.events = list()
    
    def add_event(self, event):
        self.events.append(event)

    def compose(self, source, action='addition'):
        source = copy.deepcopy(source)
        if action == 'addition':
            for event in self.events:
                event.apply_addition(source)
        elif action == 'multiplication':
            for event in self.events:
                event.apply_multiplication(source)
        elif action == 'merge':
            for event in self.events:
                event.apply_merge(source)
        else:
            raise Exception('unknown action!{}'.format(action))
        return source

if __name__ == "__main__":
    x = EventRule('aaa', {'x': 1 , 'y': 2})
    y = EventRule('bbb', {'x': 1 , 'z': 2})
    composer = Composer()
    composer.add_event(x)
    composer.add_event(y)
    src_cfg = {'x':100, 'y':100, 'z':100 }
    print(composer.compose(src_cfg, action='addition'))
    print(composer.compose(src_cfg, action='multiplication'))
    print(composer.compose(src_cfg, action='merge'))


