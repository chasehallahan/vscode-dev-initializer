import importlib
import pkgutil

__all__: list[str] = []
_pkg = __name__

for _, mod_name, _ in pkgutil.iter_modules(__path__):
    full_name = f"{_pkg}.{mod_name}"
    module = importlib.import_module(full_name)

    # expose the module itself ⇒ `import modules.comment_cleaner` still works
    globals()[mod_name] = module
    __all__.append(mod_name)

    # auto-promote a same-name callable (function/class) for `from modules import comment_cleaner`
    attr = getattr(module, mod_name, None)
    if callable(attr):
        globals()[mod_name] = attr
        __all__.append(mod_name)
