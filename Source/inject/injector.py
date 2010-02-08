import warnings

from inject import errors, providers
from inject.key import Key
from inject.injection import Injection


def register(injector):
    '''Register an injector so that it is used by all injections
    to get instances.
    '''
    Injection.injector = injector


def unregister(injector=None):
    '''Unregister an injector.
    
    If an injector is given, unregister it only if it is registered.
    If an injector is None, unregister any registered injector.
    '''
    if Injection.injector is injector or injector is None:
        Injection.injector = None


class IInjector(object):
    
    '''Injector interface.'''
    
    bindings = None
    
    def bind(self, type, annotation=None, to=None, scope=None):
        '''Specify a binding for a type and an optional annotation.'''
        pass
    
    def get_instance(self, type, annotation=None):
        '''Return an instance for a type and an optional annotation, using
        the injector bindings, or raise NoProviderError.
        
        If an annotation is given, first, try to get an instance for 
        Key(type, annotation), then for a type alone.
        
        This is a utility method, it must be possible to get providers
        directly from injector's bindings by keys.
        '''
        pass


class Injector(IInjector):
    
    key_class = Key
    provider_class = providers.Factory
    
    def __init__(self):
        self.bindings = {}
    
    def bind(self, type, annotation=None, to=None, scope=None):
        '''Specify a binding for a type and an optional annotation.'''
        if annotation is not None:
            key = self.key_class(type, annotation)
        else:
            key = type
        
        provider = self.provider_class(to, scope=scope)
        
        if key in self.bindings:
            warnings.warn('Overriding an exising binding for %s.' % key)
        self.bindings[key] = provider
    
    def get_key(self, type, annotation=None):
        '''Return a key.
        
        If annotation is None return type, otherwise combine type
        and annotation into a single key.
        '''
        if annotation is not None:
            key = self.key_class(type, annotation)
        else:
            key = type
        return key
    
    def get_provider(self, key):
        '''Return a provider for a key, or raise NoProviderError.'''
        try:
            return self.bindings[key]
        except KeyError:
            raise errors.NoProviderError(key)
    
    def get_instance(self, type, annotation=None):
        '''Return an instance for a type and an optional annotation, using
        the injector bindings, or raise NoProviderError.
        
        If an annotation is given, first, try to get an instance for 
        Key(type, annotation), then for a type alone.
        '''
        bindings = self.bindings
        
        if annotation is not None:
            key = self.get_key(type, annotation)
            if key in bindings:
                return bindings[key]()
            key = type
        else:
            key = type
        
        if key in bindings:
            return bindings[type]()
        
        raise errors.NoProviderError(key)