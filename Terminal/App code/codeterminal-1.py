import pygame
import subprocess
import platform
import threading

background_image_path = 'background image/background.PNG'  # 적절한 경로로 변경하세요

try:
    pygame.init()
except Exception as e:
    print(f"Error initializing pygame: {e}")
    exit()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
pygame.display.set_caption("Terminal")

background_image = pygame.image.load(background_image_path)
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

window_width = 800
window_height = 600
bar_height = 30
window_color = (0, 0, 0) 
bar_color = (105, 105, 105)
button_color = (255, 0, 0)
button_text_color = (255, 255, 255)
button_width = 60
button_height = 20
corner_radius = 5

window_x = (screen_width - window_width) // 2
window_y = (screen_height - window_height) // 2

font_size = 24
font = pygame.font.Font(None, font_size)
button_font = pygame.font.Font(None, font_size)

text_color = (0, 255, 0)
loading_color = (255, 255, 0)

input_box = pygame.Rect(window_x + 20, window_y + bar_height + 10, window_width - 40, 40)
input_active = False
text = ''

output_box = pygame.Rect(window_x + 20, window_y + bar_height + 60, window_width - 40, window_height - 100)
output_text = ''
scroll_offset = 0
line_height = font.get_height()
loading = False

def run_command(command):
    global output_text, scroll_offset, loading
    loading = True
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, executable='/bin/bash')
        output_text = result.stdout + result.stderr
    except Exception as e:
        output_text = str(e)
    loading = False
    scroll_offset = 0  

def render_text_wrapped(surface, text, rect, font, color, offset):
    words = text.split(' ')
    lines = []
    current_line = ''
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        test_surface = font.render(test_line, True, color)
        if test_surface.get_width() > rect.width:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                lines.append(word)
        else:
            current_line = test_line
    
    lines.append(current_line)
    
    y = rect.y - offset
    for line in lines:
        text_surface = font.render(line, True, color)
        if y + line_height > rect.y:
            surface.blit(text_surface, (rect.x, y))
        y += line_height

    return len(lines) * line_height  

def draw_rounded_rect(surface, color, rect, radius):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def render_button(surface, text, x, y, width, height, radius):
    button_rect = pygame.Rect(x, y, width, height)
    draw_rounded_rect(surface, button_color, button_rect, radius)
    text_surface = button_font.render(text, True, button_text_color)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(text_surface, text_rect)
    return button_rect


dragging = False
offset_x = 0
offset_y = 0

quit_button_x = screen_width - button_width - 10
quit_button_y = 10

def command_thread(command):
    run_command(command)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    if not loading:
                        threading.Thread(target=command_thread, args=(text,)).start()
                        text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if window_x <= mouse_pos[0] <= window_x + window_width and window_y <= mouse_pos[1] <= window_y + bar_height:
                dragging = True
                offset_x = window_x - mouse_pos[0]
                offset_y = window_y - mouse_pos[1]
            elif input_box.collidepoint(mouse_pos):
                input_active = True
            else:
                input_active = False
            
            quit_button = pygame.Rect(quit_button_x, quit_button_y, button_width, button_height)
            if quit_button.collidepoint(mouse_pos):
                running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_pos = event.pos
                window_x = mouse_pos[0] + offset_x
                window_y = mouse_pos[1] + offset_y
                input_box.topleft = (window_x + 20, window_y + bar_height + 10)
                output_box.topleft = (window_x + 20, window_y + bar_height + 60)
        elif event.type == pygame.MOUSEWHEEL:
            scroll_offset -= event.y * line_height
            scroll_offset = max(0, scroll_offset)
    
    
    screen.blit(background_image, (0, 0))
    
    
    window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
    bar_rect = pygame.Rect(window_x, window_y, window_width, bar_height)
    pygame.draw.rect(screen, window_color, window_rect)
    pygame.draw.rect(screen, bar_color, bar_rect)
    
    
    txt_surface = font.render(text, True, text_color)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, text_color, input_box, 2)
    
    
    pygame.draw.rect(screen, (0, 0, 0), output_box)
    if loading:
        loading_surface = font.render("Loading...", True, loading_color)
        screen.blit(loading_surface, (window_x + 20 + (window_width - 40 - loading_surface.get_width()) // 2, window_y + bar_height + 10 + (40 - loading_surface.get_height()) // 2))
    else:
        total_height = render_text_wrapped(screen, output_text, output_box, font, text_color, scroll_offset)
    
        
        if total_height > output_box.height:
            scroll_offset = min(scroll_offset, total_height - output_box.height)

    
    quit_button = render_button(screen, "Quit", quit_button_x, quit_button_y, button_width, button_height, corner_radius)
    
    pygame.display.flip()

pygame.quit()
exit()
