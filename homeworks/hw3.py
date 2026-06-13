import re
import keyword

class Egg:
    _tournament = None

    def __init__(self):
        self._colors = []   
        self._total = 0.0
        self._broken_top = False
        self._broken_bottom = False

    def paint(self, *pairs):
        new_total = sum(p for _, p in pairs)
        if self._total + new_total > 100.0:
            raise ValueError("Cannot overfill the egg")
        for hex_color, percentage in pairs:
            self._colors.append((hex_color.upper(), percentage))
            self._total += percentage

    def _pigment(self, side):
        """Return total pigment for 'top' (0-50%) or 'bottom' (50-100%) half."""
        if side not in ("top", "bottom"):
            raise ValueError("side must be 'top' or 'bottom'")
        lower = 0.0 if side == "top" else 50.0
        upper = 50.0 if side == "top" else 100.0

        total_pigment = 0.0
        cumulative = 0.0
        for hex_color, percentage in self._colors:
            seg_start = cumulative
            seg_end   = cumulative + percentage
            overlap = max(0.0, min(seg_end, upper) - max(seg_start, lower))
            if overlap > 0:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                pig_per_pct = (r + g + b) / percentage
                total_pigment += overlap * pig_per_pct
            cumulative += percentage
        return total_pigment

    def _clash(self, other, side):
        if side == "top":
            if self._broken_top:
                raise TypeError("This egg's top is already broken")
            if other._broken_top:
                raise TypeError("The other egg's top is already broken")
        else:
            if self._broken_bottom:
                raise TypeError("This egg's bottom is already broken")
            if other._broken_bottom:
                raise TypeError("The other egg's bottom is already broken")

        my_pig    = self._pigment(side)
        their_pig = other._pigment(side)

        if my_pig >= their_pig:
            winner, loser = self, other
        else:
            winner, loser = other, self

        if side == "top":
            loser._broken_top = True
        else:
            loser._broken_bottom = True

        if self._tournament is not None:
            self._tournament._record(self, other, side, winner)

        return winner

    def __mul__(self, other):
        return self._clash(other, "top")

    def __matmul__(self, other):
        return self._clash(other, "bottom")
    

class EggTournament:
    def __init__(self):
        self._eggs   = {}   # name -> egg
        self._wins   = {}   # egg  -> int
        self._history = {}

    def register(self, egg, name):
        if not name.isidentifier() or keyword.iskeyword(name):
            raise ValueError("Invalid registration name")
        if egg._tournament is not None:
            raise ValueError("An egg cannot be registered in multiple tournaments")
        if name in self._eggs:
            raise ValueError(f"Egg with name {name} has already been registered")
        
        self._eggs[name] = egg
        self._wins[egg]  = 0
        egg._tournament  = self

    def _record(self, egg_a, egg_b, side, winner):
        """Only care about clashes between two registered eggs."""
        reg = set(self._eggs.values())
        if egg_a not in reg or egg_b not in reg:
            return
        key = frozenset({egg_a, egg_b})
        if key not in self._history:
            self._history[key] = {}
        self._history[key][side] = winner
        self._wins[winner] += 1

    def _ranking(self):
        """Return dict: egg -> rank (dense/no-skip)."""
        eggs = list(self._wins.keys())
        sorted_eggs = sorted(eggs, key=lambda e: self._wins[e], reverse=True)
        rank_map = {}
        rank = 1
        i = 0
        while i < len(sorted_eggs):
            j = i
            while j < len(sorted_eggs) and \
                  self._wins[sorted_eggs[j]] == self._wins[sorted_eggs[i]]:
                j += 1
            for e in sorted_eggs[i:j]:
                rank_map[e] = rank
            rank += 1
            i = j
        return rank_map

    def __getitem__(self, key):
        if isinstance(key, slice):
            egg_a = key.start
            egg_b = key.stop
            side_str = key.step
        elif isinstance(key, tuple) and len(key) == 3:
            egg_a, egg_b, side_str = key
        else:
            raise KeyError(key)

        side = "top" if side_str == "top" else "bottom"
        k = frozenset({egg_a, egg_b})
        if k not in self._history or side not in self._history[k]:
            raise KeyError("No such clash recorded")
        return self._history[k][side]

    def __rmatmul__(self, position):
        rank_map = self._ranking()
        at_pos = {e for e, r in rank_map.items() if r == position}
        if not at_pos:
            raise IndexError(f"No egg at position {position}")
        if len(at_pos) == 1:
            return next(iter(at_pos))
        return at_pos

    def __getattr__(self, name):
        """Called only when normal lookup fails"""
        eggs = object.__getattribute__(self, "_eggs")
        if name in eggs:
            egg = eggs[name]
            rank_map = self._ranking()
            wins = object.__getattribute__(self, "_wins")
            return {"position": rank_map[egg], "victories": wins[egg]}
        raise AttributeError("Apologies, there is no such egg registered")

    def __contains__(self, egg):
        return egg in self._eggs.values()