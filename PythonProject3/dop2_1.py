import pickle
import json

def clean(obj):
    if hasattr(obj, '__class__') and hasattr(obj.__class__, '__module__'):
        module = obj.__class__.__module__
        if module and 'yamlium.nodes' in module:
            if hasattr(obj, 'value'):
                return clean(obj.value)
            return str(obj)

    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            key = clean(k)
            if not isinstance(key, str):
                key = str(key)
            new[key] = clean(v)
        return new
    if isinstance(obj, (list, tuple)):
        return [clean(x) for x in obj]

    return obj

with open('task2.bin', 'rb') as f:
    raw = pickle.load(f)

cleaned = clean(raw)

with open('task2.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2, sort_keys=True)

print('JSON сохранён в task2.json')
with open('task2.json', 'r', encoding='utf-8') as f:
    preview = f.read(500)
print('Начало файла:\n', preview)