# -*- coding: utf-8 -*-

# ======================================================================
# 1. Чтение бинарных данных (Reader)
# ======================================================================
class Reader:
    """Обёртка над bytes: хранит данные и текущую позицию."""
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_byte(self):
        b = self.data[self.pos]
        self.pos += 1
        return b

    def read_bytes(self, n):
        b = self.data[self.pos:self.pos + n]
        self.pos += n
        return b

    def read_uint32(self):
        b = self.read_bytes(4)
        return int.from_bytes(b, 'big', signed=False)

    def read_int64(self):
        b = self.read_bytes(8)
        return int.from_bytes(b, 'big', signed=True)

    def read_string(self):
        length = self.read_uint32()
        b = self.read_bytes(length)
        return b.decode('utf-8')


# ======================================================================
# 2. Десериализация (парсинг бинарного формата по грамматике)
# ======================================================================
def deserialize(reader):
    return parse_value(reader)

def parse_value(reader):
    marker = reader.read_byte()
    if marker == 0:
        return None
    elif marker == 1:
        return parse_bool(reader)
    elif marker == 2:
        return parse_int(reader)
    elif marker == 3:
        return parse_float(reader)
    elif marker == 4:
        return parse_str(reader)
    elif marker == 5:
        return parse_list(reader)
    elif marker == 6:
        return parse_dict(reader)
    else:
        raise ValueError(f"Неизвестный маркер типа: {marker}")

def parse_bool(reader):
    b = reader.read_byte()
    return b == 1

def parse_int(reader):
    return reader.read_int64()

def parse_float(reader):
    s = parse_str(reader)
    return float(s)

def parse_str(reader):
    return reader.read_string()

def parse_list(reader):
    length = reader.read_uint32()
    lst = []
    for _ in range(length):
        lst.append(parse_value(reader))
    return lst

def parse_dict(reader):
    length = reader.read_uint32()
    dct = {}
    for _ in range(length):
        key = parse_str(reader)
        value = parse_value(reader)
        dct[key] = value
    return dct


# ======================================================================
# 3. Генератор JSON (без библиотек, ручное экранирование)
# ======================================================================
def json_dumps(obj, level=0):
    indent = '  ' * level
    next_indent = '  ' * (level + 1)

    if obj is None:
        return 'null'
    if isinstance(obj, bool):
        return 'true' if obj else 'false'
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, str):
        escaped = ''
        for ch in obj:
            if ch == '"': escaped += '\\"'
            elif ch == '\\': escaped += '\\\\'
            elif ch == '\n': escaped += '\\n'
            elif ch == '\r': escaped += '\\r'
            elif ch == '\t': escaped += '\\t'
            else: escaped += ch
        return '"' + escaped + '"'
    if isinstance(obj, list):
        if not obj:
            return '[]'
        items = [json_dumps(item, level + 1) for item in obj]
        return '[\n' + ',\n'.join(next_indent + item for item in items) + '\n' + indent + ']'
    if isinstance(obj, dict):
        if not obj:
            return '{}'
        pairs = []
        for key, value in obj.items():
            if not isinstance(key, str):
                key = str(key)
            k_str = json_dumps(key, level + 1)
            v_str = json_dumps(value, level + 1)
            pairs.append(next_indent + k_str + ': ' + v_str)
        return '{\n' + ',\n'.join(pairs) + '\n' + indent + '}'
    return json_dumps(str(obj), level)


# ======================================================================
# 4. Основная программа
# ======================================================================
def main():
    # 1. Читаем бинарный файл, полученный в обязательном задании
    with open('task1.bin', 'rb') as f:
        binary_data = f.read()

    # 2. Десериализация (парсинг по грамматике)
    reader = Reader(binary_data)
    schedule = deserialize(reader)

    # 3. Конвертация в JSON
    json_str = json_dumps(schedule)

    # 4. Запись в файл
    with open('task1.json', 'w', encoding='utf-8') as f:
        f.write(json_str)

    print("Конвертация завершена. Результат в schedule.json")

if __name__ == '__main__':
    main()