import pickle
import yamlium

# 1. Читаем YAML
with open('task1.yml', 'r', encoding='utf-8') as f:
    yaml_text = f.read()

# 2. Парсим Yamlium – получаем структуру с узлами Key, Scalar, Mapping...
data = yamlium.parse(yaml_text)

# 3. Сохраняем через pickle
with open('task2.bin', 'wb') as f:
    pickle.dump(data, f)

print('✅ Бинарный файл schedule.bin создан.')
print('📦 Тип корневого объекта:', type(data).__name__)