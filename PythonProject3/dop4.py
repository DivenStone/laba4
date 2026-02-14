import time
import json
import yamlium

def convert_yamlium(obj):
    if hasattr(obj, '__class__') and hasattr(obj.__class__, '__module__'):
        module = obj.__class__.__module__
        if module and 'yamlium.nodes' in module:
            if hasattr(obj, 'value'):
                return convert_yamlium(obj.value)
            else:
                return str(obj)

    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            str_key = convert_yamlium(k)
            if not isinstance(str_key, str):
                str_key = str(str_key)
            new_dict[str_key] = convert_yamlium(v)
        return new_dict

    if isinstance(obj, (list, tuple)):
        return [convert_yamlium(item) for item in obj]

    return obj

def _parse_scalar(s):
    s = s.strip()
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


def parse_yaml(text):
    lines = text.splitlines()
    clean_lines = []
    for line in lines:
        if not line.strip():
            continue
        if '#' in line:
            pos = line.index('#')
            line = line[:pos].rstrip()
            if not line:
                continue
        clean_lines.append(line)

    root = None
    stack = []
    indent_stack = []

    for line in clean_lines:
        indent = len(line) - len(line.lstrip(' '))
        content = line.strip()
        while indent_stack and indent < indent_stack[-1]:
            stack.pop()
            indent_stack.pop()
        if content.startswith('- '):
            item_str = content[2:].strip()
            item = _parse_scalar(item_str)

            if not stack:
                root = []
                stack.append(root)
                indent_stack.append(indent)
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
                        indent_stack.append(indent)

        elif ': ' in content or content.endswith(':'):
            if ': ' in content:
                key, val_str = content.split(': ', 1)
                val = _parse_scalar(val_str.strip())
            else:
                key = content[:-1]
                val = None

            key = key.strip()

            if not stack:
                root = {}
                stack.append(root)
                indent_stack.append(indent)
                root[key] = val
            else:
                parent = stack[-1]
                if isinstance(parent, dict):
                    parent[key] = val
                elif isinstance(parent, list):
                    # Словарь внутри списка
                    new_dict = {key: val}
                    parent.append(new_dict)
                    stack.append(new_dict)
                    indent_stack.append(indent)

    return root if root is not None else {}

def json_dumps(obj):
    if obj is None:
        return 'null'
    if isinstance(obj, bool):
        return 'true' if obj else 'false'
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, str):
        escaped = obj.replace('\\', '\\\\').replace('"', '\\"')
        return '"' + escaped + '"'
    if isinstance(obj, list):
        items = [json_dumps(item) for item in obj]
        return '[' + ','.join(items) + ']'
    if isinstance(obj, dict):
        pairs = []
        for k, v in obj.items():
            key_str = json_dumps(str(k))
            pairs.append(key_str + ':' + json_dumps(v))
        return '{' + ','.join(pairs) + '}'
    return json_dumps(str(obj))

def yaml_to_json_manual(yaml_text):
    data = parse_yaml(yaml_text)
    return json_dumps(data)

def yaml_to_json_lib(yaml_text):
    data = yamlium.parse(yaml_text)
    data_clean = convert_yamlium(data)   
    return json.dumps(data_clean, ensure_ascii=False)

def measure_time(func, yaml_text, iterations=100):
    start = time.perf_counter()
    for _ in range(iterations):
        _ = func(yaml_text)
    end = time.perf_counter()
    return end - start


def main():
    try:
        with open('task1.yml', 'r', encoding='utf-8') as f:
            yaml_content = f.read()
    except FileNotFoundError:
        print("Файл 'task1.yaml' не найден в текущей папке!")
        return

    _ = yaml_to_json_manual(yaml_content)
    _ = yaml_to_json_lib(yaml_content)

    print("Замер производительности (100 итераций)...")
    t_manual = measure_time(yaml_to_json_manual, yaml_content, 100)
    t_lib    = measure_time(yaml_to_json_lib, yaml_content, 100)
    print("\n" + "="*60)
    print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ КОНВЕЙЕРОВ (100 итераций)")
    print("="*60)
    print(f"Самописный конвейер (YAML -> JSON): {t_manual:.4f} сек")
    print(f"Библиотечный конвейер (yamlium+json): {t_lib:.4f} сек")
    if t_lib > 0:
        print(f"Ускорение при использовании библиотек: {t_manual / t_lib:.2f}×")
    print("="*60)

    print("\nПроверка корректности (первые 200 символов JSON):")
    json_manual = yaml_to_json_manual(yaml_content)
    json_lib    = yaml_to_json_lib(yaml_content)
    print(" Manual:", json_manual[:200])
    print(" Lib:   ", json_lib[:200])


if __name__ == '__main__':
    main()