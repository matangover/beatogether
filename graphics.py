import pyglet
import os
import math

def start(looper):
    COLOR = (0,255,0)
    FRAMERATE = 1.0/10
    window = pyglet.window.Window()
    window.set_size(1100, 750)
    batch = pyglet.graphics.Batch()
    height, width = window.get_size()
    
    print "SIZE:", height, width
    images = [pyglet.image.load(os.path.join(os.path.dirname(__file__), 'image%s.png' % (i+1))) for i in range(2)]
    
    @window.event()
    def on_draw():
        window.clear()

        sprites = []
        for i, positions in enumerate(looper.kinect.get_joint_positions()[:2]):
            image = images[i]
            for x, y in positions:
                if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
                    continue
                
                sprite = pyglet.sprite.Sprite(image, batch=batch)
                #sprite.x = float(x) / 640 * width * 3 / 4 + width / 8
                #sprite.y = (480 - float(y)) / 480 * height * 3 / 4 + height / 8
                sprite.x = x + 200
                sprite.y = 680 - y
                sprite.scale = 0.5
                sprites.append(sprite)

        for player in range(2):
            role = player + 1
            tracks = looper.user_tracks[role]
            for track_idx in range(3):
                track = tracks[track_idx]
                
                sprite = pyglet.sprite.Sprite(images[player], batch=batch)
                sprite.x = player * 700 + 100 + track_idx * 70
                sprite.y = 40
                
                if looper.active_tracks[role] == track:
                    sprite.y += 20
                if track.is_recording:
                    sprite.y += 20
                #sprite.scale = 0.5
                sprites.append(sprite)

        #py
        batch.draw()
        pyglet.clock.schedule_interval(lambda dt: None, FRAMERATE)

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.Q:
            print "Exiting Pyglet app"
            pyglet.app.exit()

    pyglet.app.run()