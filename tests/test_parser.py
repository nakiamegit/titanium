# tests/test_parser.py
import unittest
import os
from src.parser import parse_dms_to_decimal, parse_file, parse_directory

class TestParser(unittest.TestCase):
    def test_parse_dms_to_decimal(self):
        """Тестирование функции parse_dms_to_decimal."""
        # Тестовые данные
        dms_north = "54 град 39.54229 мин СШ"
        dms_east = "20 град 39.19074 мин ВД"
        dms_south = "54 град 39.54229 мин ЮШ"
        dms_west = "20 град 39.19074 мин ЗД"

        # Ожидаемые результаты
        self.assertAlmostEqual(parse_dms_to_decimal(dms_north), 54 + 39.54229 / 60)
        self.assertAlmostEqual(parse_dms_to_decimal(dms_east), 20 + 39.19074 / 60)
        self.assertAlmostEqual(parse_dms_to_decimal(dms_south), -(54 + 39.54229 / 60))
        self.assertAlmostEqual(parse_dms_to_decimal(dms_west), -(20 + 39.19074 / 60))

    def test_parse_file(self):
        """Тестирование функции parse_file."""
        # Создаем тестовый файл
        test_file = "tests/test_data.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(
                "0000000; 2025-01-07T20:07:14.9219045+03:00; 17:07:29.80 GPS; 54 град 39.54229 мин СШ; 20 град 39.19074 мин ВД; 0,000625;\n"
                "0000000; 2025-01-07T20:07:15.0053563+03:00; 17:07:29.90 GPS; 54 град 39.54229 мин СШ; 20 град 39.19074 мин ВД; 0,000632;\n"
            )

        # Парсим файл
        result = parse_file(test_file)

        # Ожидаемые координаты
        expected = [
            (54 + 39.54229 / 60, 20 + 39.19074 / 60),
            (54 + 39.54229 / 60, 20 + 39.19074 / 60),
        ]

        self.assertEqual(result, expected)

    def test_parse_directory(self):
        """Тестирование функции parse_directory."""
        # Создаем тестовую директорию
        test_dir = "tests/user_data"
        os.makedirs(test_dir, exist_ok=True)

        # Создаем тестовый файл
        test_file = os.path.join(test_dir, "test_data.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(
                "0000000; 2025-01-07T20:07:14.9219045+03:00; 17:07:29.80 GPS; 54 град 39.54229 мин СШ; 20 град 39.19074 мин ВД; 0,000625;\n"
                "0000000; 2025-01-07T20:07:15.0053563+03:00; 17:07:29.90 GPS; 54 град 39.54229 мин СШ; 20 град 39.19074 мин ВД; 0,000632;\n"
            )

        # Парсим директорию
        result = parse_directory(test_dir)

        # Ожидаемые координаты
        expected = [
            (54 + 39.54229 / 60, 20 + 39.19074 / 60),
            (54 + 39.54229 / 60, 20 + 39.19074 / 60),
        ]

        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()


    #from parser import parse_directory
#directory = "user_data"
#data = parse_directory(directory)
#print(data)