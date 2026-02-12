import pickle
import json

def clean(obj):
    """Превращает Yamlium-объекты в обычные Python-типы."""
    # ---- Yamlium-узлы ----
    if hasattr(obj, '__class__') and hasattr(obj.__class__, '__module__'):
        module = obj.__class__.__module__
        if module and 'yamlium.nodes' in module:
            # У Scalar есть .value — берём его
            if hasattr(obj, 'value'):
                return clean(obj.value)
            # Остальные (Key, Mapping, Sequence…) — в строку
            return str(obj)

    # ---- Контейнеры ----
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

    # ---- Примитивы ----
    return obj

# 1. Загружаем бинарный файл
with open('task2.bin', 'rb') as f:
    raw = pickle.load(f)

# 2. Очищаем от Yamlium-обёрток
cleaned = clean(raw)

# 3. Записываем JSON с отступами 2 пробела – 100% работает
with open('task2.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2, sort_keys=True)

print('✅ JSON сохранён в schedule.json')

# 4. Покажем первые несколько строк – чтобы вы убедились, что отступы есть
with open('task2.json', 'r', encoding='utf-8') as f:
    preview = f.read(500)
print('📄 Начало файла:\n', preview)