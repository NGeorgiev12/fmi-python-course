from typing import Dict, List


class RunewordsCalculator:

    def __init__(self, runewords : Dict[str, List[str]]):
        self._runewords : Dict[str, List[str]] = runewords
        self._acc_runes : List[str] = []
        self._runeword_names = list(runewords.keys())

    def add_runes(self, runes : List[str]):
        self._acc_runes.extend(runes)

    def __iter__(self):
        return self
    
    def __next__(self):
        if not self._runeword_names:
            raise StopIteration
        for name in self._runeword_names:
            recipe = self._runewords[name]
            it = iter(self._acc_runes)
            if all(rune in it for rune in recipe):
                self._runeword_names.remove(name)
                return name
        return None
    
    
calculator = RunewordsCalculator({"Enigma": ("Ber", "Ith", "Eld")})
print(next(iter(calculator)))  # None ✓
calculator.add_runes(["Ber", "Ith", "Eld"])
print(next(iter(calculator)))  # Enigma ✓
print(next(iter(calculator)))  # StopIteration ✓