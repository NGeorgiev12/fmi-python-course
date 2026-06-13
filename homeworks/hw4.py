import importlib
import re

class BridgeKeeper:
    """Context manager class (to do)"""
    TYPE_REGEX = r"(dict\[\w+,\s*\w+\]|\w+\[\w+\]|\w+)"
    NAME_REGEX = rf"^\w+ : {TYPE_REGEX}( \| {TYPE_REGEX})?$"

    def __init__(self, module_name : str):
        self._module_name = module_name
        self._module = importlib.import_module(module_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        "Tова не виждам къде мога да го ползвам"
        pass

    def __getattr__(self, obj_name : str):
        obj = getattr(self._module, obj_name)
        if self._check_name(obj) and self._check_quest(obj) and self._check_extra_requirements(obj):
            return obj
        raise AttributeError

    def _check_name(self, obj):
        return hasattr(obj, "__name__") and str(obj.__name__[0]).isupper()

    def _check_quest(self, obj):
        if not callable(obj):
            return False
        
        doc_str = obj.__doc__
        args = []
        
        if doc_str and "Parameters" in doc_str:
            params_match = re.search(r"Parameters\n----------\n(.*?)(\n\n|$)", doc_str, re.DOTALL)
            if params_match:
                for row in params_match.group(1).splitlines():
                    if re.match(self.NAME_REGEX, row):
                        type_str = re.match(self.NAME_REGEX, row).group(2)
                        args.append(self._generate_arg(type_str))

        try:
            obj(*args)
            return True
        except Exception:
            return False

    def _check_extra_requirements(self, obj):
        for attr_name in dir(obj):
            if attr_name.startswith('__') and attr_name.endswith('__'):
                continue
            letters = re.findall(r'[a-zA-Z]', attr_name)
            if not letters:
                continue
            if letters[-1].isupper() and not re.search(r'[aeiouAEIOU]{4,}', attr_name):
                return True
        return False

    def _generate_arg(self, type_str : str):
        if type_str.startswith("dict"):
            return {}
        elif "[" in type_str:
            return []
        elif type_str == "int":
            return 1
        elif type_str == "float":
            return 1.0
        elif type_str == "str":
            return "a"
        elif type_str == "bool":
            return True
        return None
    
