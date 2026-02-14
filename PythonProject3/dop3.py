# -*- coding: utf-8 -*-

# ======================================================================
# 1. Чтение бинарных данных (Reader) – полностью из ДЗ №1
# ======================================================================
class Reader:
    """Чтение бинарных данных с отслеживанием позиции."""

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
# 2. Десериализация по формальной грамматике (рекурсивный спуск) – ДЗ №1
# ======================================================================
def deserialize(reader):
    return parse_value(reader)


def parse_value(reader):
    marker = reader.read_byte()
    if marker == 0:  # NULL
        return None
    elif marker == 1:  # BOOL
        return parse_bool(reader)
    elif marker == 2:  # INT
        return parse_int(reader)
    elif marker == 3:  # FLOAT (хранится как строка)
        return parse_float(reader)
    elif marker == 4:  # STRING
        return parse_str(reader)
    elif marker == 5:  # LIST
        return parse_list(reader)
    elif marker == 6:  # DICT
        return parse_dict(reader)
    else:
        raise ValueError(f'Неизвестный маркер: {marker}')


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
        key = parse_str(reader)  # ключ всегда строка (гарантия бинарного протокола)
        value = parse_value(reader)
        dct[key] = value
    return dct


# ======================================================================
# 3. Сериализация в XML (вместо JSON) – новая часть для ДЗ №3
# ======================================================================
import xml.etree.ElementTree as ET
import xml.dom.minidom as md


def build_xml_element(name, data):
    """
    Рекурсивно строит ElementTree.Element из данных Python.
    - name: имя текущего узла
    - data: dict, list, str, int, float, bool, None
    """
    elem = ET.Element(name)

    if isinstance(data, dict):
        for key, value in data.items():
            child = build_xml_element(key, value)
            elem.append(child)

    elif isinstance(data, list):
        for item in data:
            child = build_xml_element('item', item)  # каждый элемент списка -> <item>
            elem.append(child)

    else:  # примитив: str, int, float, bool, None
        if data is None:
            elem.text = ''
        else:
            elem.text = str(data)

    return elem


def write_pretty_xml(root, output_file):
    """Записывает XML с отступами 2 пробела, удаляя лишние пустые строки."""
    rough_string = ET.tostring(root, encoding='utf-8')
    dom = md.parseString(rough_string)
    pretty_bytes = dom.toprettyxml(indent='  ', encoding='utf-8')

    # minidom иногда вставляет лишние пустые строки – чистим
    lines = pretty_bytes.decode('utf-8').split('\n')
    clean_lines = [line for line in lines if line.strip() != '']
    pretty_xml = '\n'.join(clean_lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)


# ======================================================================
# 4. Главная функция: бинарный файл -> XML
# ======================================================================
def binary_to_xml(input_bin, output_xml, root_name='task3'):
    # 1. Загружаем бинарный файл
    with open(input_bin, 'rb') as f:
        binary_data = f.read()

    # 2. Десериализуем через наш парсер (формальная грамматика)
    reader = Reader(binary_data)
    data = deserialize(reader)

    # 3. Строим XML-дерево
    root = build_xml_element(root_name, data)

    # 4. Записываем с pretty-print
    write_pretty_xml(root, output_xml)

    print(f'XML сохранён в {output_xml}')


# ======================================================================
# 5. Запуск
# ======================================================================
if __name__ == '__main__':
    # Укажите имена входного и выходного файлов

    binary_to_xml('task1.bin', 'task3.xml', root_name='task3')
