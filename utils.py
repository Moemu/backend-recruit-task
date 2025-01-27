def check_value(value:str, type:str) -> tuple[bool, int|float|str]:
    if type == 'int':
        if value.isdigit():
            return True, int(value)
        else:
            return False, None
    elif type == 'float':
        if value.replace('.','',1).isdigit():
            return True, float(value)
        else:
            return False, None
    elif type == 'date':
        if value.count('.') == 2 and value.replace('.','',2).isdigit():
            return True, value
        else:
            return False, None
    else:
        return True, value