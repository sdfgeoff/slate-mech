import bpy
import time

running = False
t = time.time()

def start_game(*args):
    global running
    if not running and t + 0.1 < time.time():
        running = True
        bpy.ops.view3d.game_start()


bpy.app.handlers.game_post.append(exit)
bpy.app.handlers.scene_update_post.append(start_game)



