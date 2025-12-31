import pygame


class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 'down'
        self.pixel_x = 0
        self.pixel_y = 0

    def check_position(self, entity):
        return (entity.x == self.x) and (entity.y == self.y)

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_pos(self):
        return self.x, self.y

    def set_direction(self, new_x, new_y):
        if new_x > self.x:
            self.direction = 'right'
        elif new_x < self.x:
            self.direction = 'left'
        elif new_y > self.y:
            self.direction = 'down'
        elif new_y < self.y:
            self.direction = 'up'

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    @staticmethod
    def validate_move(start_x, start_y, end_x, end_y, maze_size, walls, gate=None):
        """
        Static method to check if a move from (start_x, start_y) to (end_x, end_y) is valid.
        """
        # 1. Check Map Boundaries
        if not (0 <= end_x < maze_size and 0 <= end_y < maze_size):
            return False

        # 2. Check Gate Collision
        if gate and gate.is_blocking():
            gx, gy = gate.grid_x, gate.grid_y

            # The gate is visually at the TOP of cell (gx, gy).
            # It acts as a wall between (gx, gy) and (gx, gy-1).

            # Case A: Moving DOWN into the gate cell from above
            # From (gx, gy-1) -> To (gx, gy)
            if start_x == gx and start_y == gy - 1 and end_x == gx and end_y == gy:
                return False

            # Case B: Moving UP out of the gate cell
            # From (gx, gy) -> To (gx, gy-1)
            if start_x == gx and start_y == gy and end_x == gx and end_y == gy - 1:
                return False

        # 3. Check Wall Collision
        # Moving RIGHT
        if end_x > start_x:
            for w in walls:
                if w['x'] == end_x and w['y'] == end_y and w['dir'] in ['vertical', 'both']: return False
        # Moving LEFT
        elif end_x < start_x:
            for w in walls:
                if w['x'] == start_x and w['y'] == start_y and w['dir'] in ['vertical', 'both']: return False
        # Moving DOWN
        elif end_y > start_y:
            for w in walls:
                if w['x'] == end_x and w['y'] == end_y and w['dir'] in ['horizontal', 'both']: return False
        # Moving UP
        elif end_y < start_y:
            for w in walls:
                if w['x'] == start_x and w['y'] == start_y and w['dir'] in ['horizontal', 'both']: return False

        return True

    def check_eligible_move(self, new_x, new_y, maze_size, walls, gate=None):
        """Wrapper for instance-based check"""
        return Entity.validate_move(self.x, self.y, new_x, new_y, maze_size, walls, gate)