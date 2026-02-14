def parse_yaml(text):
    lines = text.splitlines()
    cllines = []
    for line in lines:
        if not line.strip():
            continue
        if '#' in line:
            pos = line.index('#')
            line = line[:pos].rstrip()
            if not line:
                continue
        cllines.append(line)
    lines = cllines

    root = None
    stack = []
    otstup = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stroka = len(line) - len(line.lstrip(' '))
        conch = line.strip()

        while otstup and stroka < otstup[-1]:
            stack.pop()
            otstup.pop()

        if conch.startswith('- '):
            pervoe = conch[2:].strip()
            item = parse_scalar(pervoe)

            if not stack:
                # корневой список
                root = []
                stack.append(root)
                otstup.append(stroka)
                root.append(item)
            else:
                parent = stack[-1]
                if isinstance(parent, list):
                    parent.append(item)
                elif isinstance(parent, dict):
                    if parent:
                        last_key = list(parent.keys())[-1]

                        new_list = [item]
                        parent[last_key] = new_list
                        stack.append(new_list)
                        otstup.append(stroka)
                    else:
                        pass
                else:
                    pass
        elif ': ' in conch or conch.endswith(':'):
            if ': ' in conch:
                key, val_str = conch.split(': ', 1)
                val_str = val_str.strip()
                val = parse_scalar(val_str)
            else:
                key = conch[:-1]
                val = None

            key = key.strip()

            if not stack:
                root = {}
                stack.append(root)
                otstup.append(stroka)
                root[key] = val
            else:
                parent = stack[-1]
                if isinstance(parent, dict):
                    parent[key] = val
                elif isinstance(parent, list):
                    new_dict = {key: val}
                    parent.append(new_dict)
                    stack.append(new_dict)
                    otstup.append(stroka)
                else:
                    pass
        else:
            pass

        i += 1

    return root if root is not None else {}

def parse_scalar(s):
    if s == '':
        return ''
    lower = s.lower()
    if lower == 'true':
        return True
    if lower == 'false':
        return False
    if lower == 'null' or lower == '~':
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s

def serialize(obj, file):
    TYPE_NULL = 0
    TYPE_BOOL = 1
    TYPE_INT  = 2
    TYPE_FLOAT= 3
    TYPE_STR  = 4
    TYPE_LIST = 5
    TYPE_DICT = 6

    def _write_bytes(b):
        file.write(b)

    def _write_uint32(x):
        _write_bytes(x.to_bytes(4, 'big', signed=False))

    def _write_int64(x):
        _write_bytes(x.to_bytes(8, 'big', signed=True))

    def _write_str(s):
        b = s.encode('utf-8')
        _write_uint32(len(b))
        _write_bytes(b)

    def _write_bool(b):
        _write_bytes(b'\x01' if b else b'\x00')

    def _serialize(obj):
        if obj is None:
            _write_bytes(bytes([TYPE_NULL]))
        elif isinstance(obj, bool):
            _write_bytes(bytes([TYPE_BOOL]))
            _write_bool(obj)
        elif isinstance(obj, int):
            _write_bytes(bytes([TYPE_INT]))
            _write_int64(obj)
        elif isinstance(obj, float):
            _write_bytes(bytes([TYPE_FLOAT]))
            _write_str(str(obj))
        elif isinstance(obj, str):
            _write_bytes(bytes([TYPE_STR]))
            _write_str(obj)
        elif isinstance(obj, list):
            _write_bytes(bytes([TYPE_LIST]))
            _write_uint32(len(obj))
            for item in obj:
                _serialize(item)
        elif isinstance(obj, dict):
            _write_bytes(bytes([TYPE_DICT]))
            _write_uint32(len(obj))
            for k, v in obj.items():
                if not isinstance(k, str):
                    k = str(k)
                _write_str(k)
                _serialize(v)
        else:
            _write_bytes(bytes([TYPE_STR]))
            _write_str(str(obj))

    _serialize(obj)


with open('task1.yml', 'r', encoding='utf-8') as f:
    yaml_text = f.read()

data = parse_yaml(yaml_text)

with open('task1.bin', 'wb') as f:
    serialize(data, f)

print("Конвертация завершена. Бинарный файл: task1.bin")