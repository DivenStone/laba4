import pickle
import yamlium

with open('task1.yml', 'r', encoding='utf-8') as f:
    yaml_text = f.read()
data = yamlium.parse(yaml_text)

with open('task2.bin', 'wb') as f:
    pickle.dump(data, f)

print('Бинарный файл task2.bin создан.')
print('Тип корневого объекта:', type(data).__name__)