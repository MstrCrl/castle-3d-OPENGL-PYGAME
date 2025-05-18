import pygame
from pygame.locals import *
from OpenGL.GL import *
import glm
import config
from model_loader import create_textured_object
from texture_loader import load_texture
from textured_shader import create_shader_program

def screen_to_world(x, y, width, height):
    # Normalize device coordinates [-1, 1]
    norm_x = (2.0 * x) / width - 1.0
    norm_y = 1.0 - (2.0 * y) / height  # Flip y-axis
    return norm_x, norm_y


def main():
    pygame.init()
    display = (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glClearColor(*config.BACKGROUND_COLOR)

    shader = create_shader_program()
    glUseProgram(shader)

    # Load both objects
    vao_castle, ebo_castle, count_castle = create_textured_object("source\castle_vertices.txt", "source\castle_indices.txt")
    # Load both textures
    tex_castle = load_texture("source\castle.jpg")

    glUniform1i(glGetUniformLocation(shader, "texture1"), 0)

    model_loc = glGetUniformLocation(shader, "model")
    view_loc = glGetUniformLocation(shader, "view")
    proj_loc = glGetUniformLocation(shader, "projection")
       
    proj = glm.perspective(glm.radians(100.0), display[0] / display[1], 0.1, 100.0)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(proj))

    clock = pygame.time.Clock()
    angle = 0
    running = True
    position = glm.vec3(0, 1, 0)
    
    camera_distance = 10.0
    mouse_down = False
    rot_x = 0
    rot_y = 0
    last_mouse_pos = (0, 0)
    
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:  # left click
                        mx, my = pygame.mouse.get_pos()
                        norm_x, norm_y = screen_to_world(mx, my, *display)
                        position.x = norm_x * 10  # Scale for visibility
                        position.y = norm_y * 8
                        print(f"Moved object to: {position.x}, {position.y}")
                    
                if event.button == 4:
                    camera_distance -= 0.5  # Zoom in
                    camera_distance = max(1.0, camera_distance)  # Limit zoom in
                elif event.button == 5:
                    camera_distance += 0.5  # Zoom out


            #rotate the object using mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
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
                    rot_y += dx * 0.5
                    rot_x += dy * 0.5
                    last_mouse_pos = (x, y)
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            position.x -= 0.05
        if keys[pygame.K_RIGHT]:
            position.x += 0.05
        if keys[pygame.K_UP]:
            position.y += 0.05
        if keys[pygame.K_DOWN]:
            position.y -= 0.05

        if keys[pygame.K_a]:
            rotation_axis = glm.vec3(1.0, 0.0, 0.0)  # Rotate around X-axis
        if keys[pygame.K_d]:
            rotation_axis = glm.vec3(0.0, 1.0, 0.0)  # Rotate around Y-axis

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        view = glm.lookAt(glm.vec3(0, camera_distance, 0), glm.vec3(0, 0, 0), glm.vec3(0, 0, -1))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))

        # Draw castle
        model1 = glm.mat4(1.0)
        model1 = glm.translate(model1, position)
        model1 = glm.rotate(model1, glm.radians(rot_x), glm.vec3(1, 0, 0))
        model1 = glm.rotate(model1, glm.radians(rot_y), glm.vec3(0, 1, 0))
        model1 = glm.translate(model1, position)  # Move cube back
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model1))
        glBindTexture(GL_TEXTURE_2D, tex_castle)
        glBindVertexArray(vao_castle)
        glDrawElements(GL_TRIANGLES, count_castle, GL_UNSIGNED_INT, None)   

        pygame.display.flip()
        clock.tick(config.FPS)
        angle += 1

    #idagdag dito sa delete
    glDeleteVertexArrays(1, [vao_castle])
    glDeleteBuffers(1, [ebo_castle])
    glDeleteProgram(shader)
    pygame.quit()

if __name__ == "__main__":
    main()
