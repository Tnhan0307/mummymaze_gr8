import pygame
import os

# Thiết lập vị trí thư mục chính
PROJECT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../../..")
)

# Thiết lập vị trí thư mục api, dist, resources
API_PATH = os.path.join(PROJECT_PATH, "api")
DIST_PATH = os.path.join(PROJECT_PATH, "dist")
RESOURCE_PATH = os.path.join(PROJECT_PATH, "resources")

# Thiết lập vị trí dữ liệu
LEVELS_PATH = os.path.join(DIST_PATH, "levels")

# Thiết lập vị trí các tài nguyên
ENTITIES_PATH = os.path.join(RESOURCE_PATH, "entities")
OBJECTS_PATH = os.path.join(RESOURCE_PATH, "objects")
UI_PATH = os.path.join(RESOURCE_PATH, "ui")
SOUNDS_PATH = os.path.join(RESOURCE_PATH, "sounds")
MUSIC_PATH = os.path.join(RESOURCE_PATH, "music")

# Thiết lập cho trò chơi
maze_coord_x = 213
maze_coord_y = 80
fps = 60