from typing import Any

def check_value(value:str, type:str) -> Any:
    if type == 'int':
        if value.isdigit():
            return int(value)
        else:
            return False
    elif type == 'float':
        if value.replace('.','',1).isdigit():
            return float(value)
        else:
            return False
    elif type == 'date':
        if value.count('.') == 2 and value.replace('.','',2).isdigit():
            return value
        else:
            return False
    else:
        return value