import unittest
from unittest.mock import patch, mock_open
from bangaranga import does_the_banga_rang, TheBangaDoesNotRangError

class TestDoesBangaRanga(unittest.TestCase):

    @patch("builtins.open", mock_open(read_data="banga the ranga"))
    def test_two_words(self):
        result = does_the_banga_rang("тук_няма_значение_какво_е.txt")
        self.assertEqual(result, 2)

    @patch("builtins.open", mock_open(read_data="bang a small ranga"))
    def test_three_words(self):
        result = does_the_banga_rang("ама_наистина_няма_знaчение.txt")
        self.assertEqual(result, 3)

    @patch("builtins.open", mock_open(read_data="chunga-changa bangaranga"))
    def test_single_word_bangaranga(self):
        result = does_the_banga_rang("ще_си_пуша_когато_на_мен_ми_се_пуши.txt")
        self.assertEqual(result, 1)

    @patch("builtins.open", mock_open(read_data="ranga banga"))
    def test_wrong_order_returns_zero(self):
        result = does_the_banga_rang("не_си_познал.txt")
        self.assertEqual(result, 0)

    @patch("builtins.open", mock_open(read_data="BANGARANGA"))
    def test_case_insensitive(self):
        result = does_the_banga_rang("пуша_си_цигарата_и_не_ми_пука_че_лукът_е_лев_и_двайсет.txt")
        self.assertEqual(result, 1)

    @patch("builtins.open", mock_open(read_data="banga ranga bangaranga ban garan ga"))
    def test_minimum_word_count(self):
        result = does_the_banga_rang("пуша_си_цигарата_и_не_ми_пука_че_лукът_е_лев_и_двайсет.txt")
        self.assertEqual(result, 1)

    @patch("builtins.open", side_effect=OSError)
    def test_missing_file_raises_custom_error(self, mock_file):
        with self.assertRaises(TheBangaDoesNotRangError):
            does_the_banga_rang("откакто_се_помъкна_с_тая.txt")

    @patch("builtins.open", mock_open(read_data="banga something"))
    def test_incomplete_bangaranga_returns_zero(self):
        result = does_the_banga_rang("направо_ми_счерни_живота.txt")
        self.assertEqual(result, 0)

    @patch("builtins.open", mock_open(read_data="xbangaranga"))
    def test_word_boundary(self):
        result = does_the_banga_rang("само_ме_ядосва.txt")
        self.assertEqual(result, 0)

    @patch("builtins.open", mock_open(read_data=""))
    def test_empty_file_returns_zero(self):
        result = does_the_banga_rang("вече_нямам_нещо_готино_да_кажа.txt")
        self.assertEqual(result, 0)

    @patch("builtins.open", side_effect=IOError)
    def test_io_error_raises_custom_error(self, mock_file):
        with self.assertRaises(TheBangaDoesNotRangError):
            does_the_banga_rang("адиос_мучачос_компанйерос_бай_бай_чао_по_дяволитее.txt")

