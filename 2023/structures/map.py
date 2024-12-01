from functools import lru_cache
from typing import Callable, Iterable, Self


class Map:
    def __init__(self, h: int, w: int, value: int | str = -1) -> None:
        self.w = w
        self.h = h
        self.map = self.create(h, w, value)
        self.show_remap: dict[int | str, int | str] = {-1: '.'}
        self.get_nearest_points = lru_cache(maxsize=None)(self.get_nearest_points)

    @classmethod
    def from_object(cls, lines: list[str]) -> Self:
        h = len(lines)
        w = len(lines[0])
        map = cls(h, w)
        for y, line in enumerate(lines):
            for x, value in enumerate(line):
                map.map[y][x] = value
        return map

    def create(self, y: int, x: int, value: int | str = -1) -> list[list[int | str]]:
        line = [value] * x
        return [line[:] for _ in range(y)]

    def show(self, width: int = 2) -> None:
        for line in self.map:
            for value in line:
                value = self.show_remap.get(value, value)
                print(f'{value:>{width}} ', end='')
            print()

    def find_value(self, value: int | str) -> tuple[int, int]:
        for y, line in enumerate(self.map):
            for x, d in enumerate(line):
                if d == value:
                    return y, x
        raise ValueError('Not found')

    def normalize_point(self, y: int, x: int) -> tuple[int, int] | None:
        if not (0 <= y < self.h) or not (0 <= x < self.w):
            return None
        return y, x

    def get_nearest_points(self, y: int, x: int) -> list[tuple[int, int]]:
        result = []
        for ydiff, xdiff in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_coords = self.normalize_point(y + ydiff, x + xdiff)
            if new_coords is not None:
                result.append(new_coords)
        return result

    def get_nearest_points_by_value(self, y: int, x: int, value: int) -> Iterable[tuple[int, int, int | str]]:
        for new_y, new_x in self.get_nearest_points(y, x):
            new_value = self.map[new_y][new_x]
            if new_value == value:
                yield new_y, new_x, new_value

    def calc_inc_step(self, condition: Callable | None = None) -> bool:
        def target_filter(y, x, value, new_y, new_x, new_value):
            if condition is not None and not condition(y, x, value, new_y, new_x, new_value):
                return False
            return new_value == -1 or new_value > value + 1

        def target_action(y, x, value, new_y, new_x, new_value):
            self.map[new_y][new_x] = value + 1

        return self.calc_step(
            point_filter=lambda y, x, value: value != -1,
            target_filter=target_filter,
            target_action=target_action,
        )

    def calc_step(
        self,
        point_filter: Callable | None = None,
        target_filter: Callable | None = None,
        target_action: Callable | None = None,
        target_value: int | str | None = None,
    ) -> bool:
        any_change = False
        for y, line in enumerate(self.map):
            for x, value in enumerate(line):
                if point_filter is not None and not point_filter(y, x, value):
                    continue
                for new_y, new_x in self.get_nearest_points(y, x):
                    new_value = self.map[new_y][new_x]
                    if target_filter is not None and not target_filter(y, x, value, new_y, new_x, new_value):
                        continue
                    if target_value is not None:
                        self.map[new_y][new_x] = target_value
                    if target_action is not None:
                        target_action(y, x, value, new_y, new_x, new_value)
                    any_change = True
        return any_change
