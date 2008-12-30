# Based on IPY Tutorial/pyevent.py

class Event(object):    
    def __init__(self):
        self.handlers = []
        
    def __contains__(self, handler):
        return handler in self.handlers
        
    def __iadd__(self, handler):
        if isinstance(handler, Event):
            self.handlers.extend(handler.handlers)
        else:
            if not callable(handler):
                raise TypeError, 'Cannot assign to event unless value is callable'
            
            self.handlers.append(handler)
            
        return self
            
    def __isub__(self, handler):
        if isinstance(handler, Event):
            self.handlers = [h for h in self.handlers if h not in handler.handlers]
        else:
            self.handlers.remove(handler)
            
        return self
    
    def __call__(self, sender, event_args):
        if hasattr(event_args, 'Handled'):
            for handler in self.handlers:
                handler(sender, event_args)
                if event_args.Handled:
                    break
        else:
            for handler in self.handlers:
                handler(sender, event_args)
            
            
        