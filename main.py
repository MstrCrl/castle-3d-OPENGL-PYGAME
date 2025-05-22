import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm
import config
from model_loader import create_textured_object
from texture_loader import load_texture
from textured_shader import create_shader_program

# Predefined camera views
views = [
    {"name": "CASTLE TOP VIEW", "zoom": 10.5, "rot_x": -13.0, "rot_y": -449.0},
    {"name": "CASTLE MAIN VIEW", "zoom": 9.0, "rot_x": -45.0, "rot_y": -90.0},
    {"name": "OUTER GATE", "zoom": 8.0, "rot_x": -51.0, "rot_y": -90.0},
    {"name": "VENDORS UNDER BRIDGE", "zoom": 6.5, "rot_x": -36.0, "rot_y": -66.5},
    {"name": "MARKET PLACE", "zoom": 6.0, "rot_x": -50.5, "rot_y": -56.0},
    {"name": "TAVERN", "zoom": 7.0, "rot_x": -49.5, "rot_y": -48.5},
    {"name": "BLACKSMITH", "zoom": 5.5, "rot_x": -54.5, "rot_y": -24.0},
    {"name": "PEASANT HUT", "zoom": 6.5, "rot_x": -52.5, "rot_y": 7.5},
    {"name": "FARM", "zoom": 7.0, "rot_x": -52.5, "rot_y": 26.5},
    {"name": "WINDMILL", "zoom": 8.0, "rot_x": -50.5, "rot_y": 18.5},
    {"name": "UPPER CLASS RESIDENTIAL", "zoom": 7.0, "rot_x": -49.5, "rot_y": -138.5},
    {"name": "POND", "zoom": 7.0, "rot_x": -62.5, "rot_y": -142.5},
    {"name": "CHAPPEL", "zoom": 7.5, "rot_x": -49.5, "rot_y": -218.5},
    {"name": "OUTER OUTPOST", "zoom": 8.5, "rot_x": -58.0, "rot_y": -217.5},
    {"name": "INNER GATE", "zoom": 5.5, "rot_x": -30.5, "rot_y": -89.0},
    {"name": "INNER OUTPOST", "zoom": 7.0, "rot_x": -24.5, "rot_y": -153.0},
    {"name": "CASTLE TOP VIEW", "zoom": 10.5, "rot_x": -13.0, "rot_y": -449.0},
    {"name": "CASTLE MAIN VIEW", "zoom": 9.0, "rot_x": -45.0, "rot_y": -90.0},
]

def main():
    pygame.init()
    pygame.mixer.init()

    display = (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glClearColor(*config.BACKGROUND_COLOR)

    shader = create_shader_program()
    glUseProgram(shader)

    vao_castle, ebo_castle, count_castle = create_textured_object("source\\castle_vertices.txt", "source\\castle_indices.txt")
    tex_castle = load_texture("source\\castle.jpg")

    glUniform1i(glGetUniformLocation(shader, "texture1"), 0)

    model_loc = glGetUniformLocation(shader, "model")
    view_loc = glGetUniformLocation(shader, "view")
    proj_loc = glGetUniformLocation(shader, "projection")

    proj = glm.perspective(glm.radians(100.0), display[0] / display[1], 0.1, 100.0)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(proj))

    clock = pygame.time.Clock()
    running = True
    position = glm.vec3(0, 1, 0)

    view_index = 0
    view_name = views[view_index]["name"]
    rot_x = views[view_index]["rot_x"]
    rot_y = views[view_index]["rot_y"]
    camera_distance = views[view_index]["zoom"]

    target_rot_x = rot_x
    target_rot_y = rot_y
    target_camera_distance = camera_distance

    mouse_down = False
    last_mouse_pos = (0, 0)

    auto_mode = True
    last_auto_switch_time = pygame.time.get_ticks()

    # Define per-view intervals (ms)
    auto_switch_intervals = (
        [2500] * 3 +          # views 0-2: 2.5 sec each
        [1500] * 5 +          # views 3-7: 1.5 sec each
        [1125] * 9            # views 8-15: 1.125 sec each (~9 sec total)
    )
    total_auto_scenes = len(auto_switch_intervals)
    total_views = len(views)
    
    pygame.mixer.music.load("source/music.mp4")
    pygame.mixer.music.play(-1)
    pygame.time.wait(1000)

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not auto_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        view_index = (view_index + 1) % total_views
                        view = views[view_index]
                        view_name = view["name"]
                        target_camera_distance = view["zoom"]
                        target_rot_x = view["rot_x"]
                        target_rot_y = view["rot_y"]
                        print(f"Switched to: {view_name}")

                    elif event.key == pygame.K_LEFT:
                        view_index = (view_index - 1) % total_views
                        view = views[view_index]
                        view_name = view["name"]
                        target_camera_distance = view["zoom"]
                        target_rot_x = view["rot_x"]
                        target_rot_y = view["rot_y"]
                        print(f"Switched to: {view_name}")

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        target_camera_distance = max(1.0, target_camera_distance - 0.5)
                    elif event.button == 5:
                        target_camera_distance += 0.5

                    if event.button == 1:
                        mouse_down = True
                        last_mouse_pos = pygame.mouse.get_pos()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_down = False

                if event.type == pygame.MOUSEMOTION and mouse_down:
                    x, y = pygame.mouse.get_pos()
                    dx = x - last_mouse_pos[0]
                    dy = y - last_mouse_pos[1]
                    target_rot_y += dx * 0.5
                    target_rot_x += dy * 0.5
                    last_mouse_pos = (x, y)

        # Auto-switch with per-scene intervals
        if auto_mode and (current_time - last_auto_switch_time) > auto_switch_intervals[view_index]:
            view_index = (view_index + 1) % total_views
            view = views[view_index]
            view_name = view["name"]
            target_camera_distance = view["zoom"]
            target_rot_x = view["rot_x"]
            target_rot_y = view["rot_y"]
            print(f"Auto-switched to: {view_name}")

            last_auto_switch_time = current_time

            if view_index == total_auto_scenes:
                auto_mode = False
                print("Auto mode ended, manual control enabled.")

        lerp_speed = 0.1
        camera_distance += (target_camera_distance - camera_distance) * lerp_speed
        rot_x += (target_rot_x - rot_x) * lerp_speed
        rot_y += (target_rot_y - rot_y) * lerp_speed

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view = glm.lookAt(glm.vec3(0, camera_distance, 0),
                          glm.vec3(0, 0, 0),
                          glm.vec3(0, 0, -1))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))

        model1 = glm.mat4(1.0)
        model1 = glm.translate(model1, position)
        model1 = glm.rotate(model1, glm.radians(rot_x), glm.vec3(1, 0, 0))
        model1 = glm.rotate(model1, glm.radians(rot_y), glm.vec3(0, 1, 0))
        model1 = glm.translate(model1, position)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model1))

        glBindTexture(GL_TEXTURE_2D, tex_castle)
        glBindVertexArray(vao_castle)
        glDrawElements(GL_TRIANGLES, count_castle, GL_UNSIGNED_INT, None)

        pygame.display.flip()
        clock.tick(config.FPS)

    glDeleteVertexArrays(1, [vao_castle])
    glDeleteBuffers(1, [ebo_castle])
    glDeleteProgram(shader)
    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    main()
