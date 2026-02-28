import pygame
import random

# --- 1. ตั้งค่าระบบ Pygame เบื้องต้น ---
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Builder: หอคอยนักปราชญ์ 🏰")

# ตั้งค่าฟอนต์
font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 80)
small_font = pygame.font.Font(None, 28)

# --- 2. โหลดรูปภาพทั้งหมด ---
try:
    bg_img = pygame.image.load('background.png')
    bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT)) 
    
    tower_img1 = pygame.image.load('towerLV1.png')
    tower_img2 = pygame.image.load('towerLV2.png')
    tower_img3 = pygame.image.load('towerLV3.png')
    
    monster_img = pygame.image.load('little-man-1.gif')
    monster_img = pygame.transform.scale(monster_img, (50, 50)) 
    print("✨ โหลดรูปภาพทั้งหมดสำเร็จแล้วจ้า!")
except Exception as e:
    print(f"❌ หาไฟล์รูปไม่เจอจ้า: {e}")
    tower_img1 = tower_img2 = tower_img3 = bg_img = monster_img = None

# --- 3. ตัวแปรระบบเกม ---
state = "menu"  # สถานะเกม: 'menu', 'playing', 'game_over', 'paused'
max_tower_hp = 3
tower_hp = max_tower_hp
tower_level = 1
tower_xp = 0
xp_needed = 5  
score = 0  

current_input = "" 
enemies = []
particles = []

damage_flash_alpha = 0   
levelup_flash_alpha = 0  

def spawn_enemy():
    """เสกศัตรูพร้อมโจทย์เลข (ฉบับอัปเกรด แก้ปัญหาตัวทับกัน)"""
    max_num = 5 + (tower_level * 2) 
    a = random.randint(1, max_num)
    b = random.randint(1, max_num)
    speed = random.uniform(0.5, 1.5) + (tower_level * 0.1)
    
    random_y = random.randint(420, 480) 
    start_x = SCREEN_WIDTH + random.randint(50, 150)
    
    if len(enemies) > 0:
        last_x = max([e['x'] for e in enemies])
        if start_x < last_x + 100:
            start_x = last_x + random.randint(100, 200)
            
    enemies.append({
        'x': start_x,
        'y': random_y,
        'a': a, 'b': b, 'ans': a + b, 'speed': speed
    })

def create_explosion(x, y, color, count=30):
    for _ in range(count):
        particles.append({
            'x': x, 'y': y,
            'vx': random.uniform(-5, 5),
            'vy': random.uniform(-5, 5),
            'timer': random.randint(20, 40),
            'color': color
        })

def reset_game():
    """ฟังก์ชันรีเซ็ตค่าต่างๆ เพื่อเริ่มเกมใหม่"""
    global tower_hp, tower_level, tower_xp, xp_needed, score, current_input, damage_flash_alpha
    tower_hp = max_tower_hp
    tower_level = 1
    tower_xp = 0
    xp_needed = 5
    score = 0
    current_input = ""
    enemies.clear()
    particles.clear()
    damage_flash_alpha = 0
    for _ in range(3): spawn_enemy()

clock = pygame.time.Clock()
running = True

# --- 4. ลูปหลักของเกม ---
while running:
    
    if bg_img:
        screen.blit(bg_img, (0, 0)) 
    else:
        screen.fill((20, 30, 50)) 
        
    pygame.draw.rect(screen, (50, 100, 50), (0, 500, SCREEN_WIDTH, 100))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if state == "menu":
                if event.key == pygame.K_SPACE:
                    state = "playing"
                    reset_game()
                    
            elif state == "playing":
                # 🌟 กด ESC เพื่อหยุดเกม (Pause)
                if event.key == pygame.K_ESCAPE:
                    state = "paused"
                elif event.key == pygame.K_BACKSPACE:
                    current_input = current_input[:-1] 
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if current_input != "":
                        try:
                            ans_int = int(current_input)
                            target = None
                            closest_x = 9999
                            for e in enemies:
                                if e['ans'] == ans_int and e['x'] < closest_x:
                                    target = e
                                    closest_x = e['x']
                                    
                            if target:
                                create_explosion(target['x']+25, target['y']+25, (255, 150, 0))
                                pygame.draw.line(screen, (0, 255, 255), (100, 400), (target['x']+25, target['y']+25), 8)
                                enemies.remove(target)
                                spawn_enemy() 
                                score += 100 * tower_level
                                
                                if tower_level < 12:
                                    tower_xp += 1
                                    if tower_xp >= xp_needed:
                                        tower_level += 1
                                        tower_xp = 0
                                        xp_needed += 2 
                                        create_explosion(100, 450, (255, 255, 0), 60)
                                        levelup_flash_alpha = 150 
                        except ValueError:
                            pass
                        current_input = "" 
                else:
                    if event.unicode.isdigit():
                        current_input += event.unicode
                        
            # 🌟 ถ้าเกมหยุดอยู่ กด ESC เพื่อเล่นต่อ
            elif state == "paused":
                if event.key == pygame.K_ESCAPE:
                    state = "playing"
                        
            elif state == "game_over":
                if event.key == pygame.K_r:
                    state = "playing"
                    reset_game()

    # --- อัปเดตตรรกะเกม (จะทำงานเฉพาะตอนที่ state เป็น playing เท่านั้น) ---
    if state == "playing":
        for e in enemies:
            e['x'] -= e['speed']
            if e['x'] < 100:
                tower_hp -= 1
                enemies.remove(e)
                spawn_enemy()
                create_explosion(100, 450, (255, 0, 0)) 
                damage_flash_alpha = 100 
                if tower_hp <= 0:
                    state = "game_over" 
                    
        for p in particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['timer'] -= 1
            if p['timer'] <= 0:
                particles.remove(p)

    # --- 5. วาดกราฟิก ---
    if state == "menu":
        title_text = big_font.render("TOWER BUILDER", True, (255, 215, 0))
        subtitle_text = font.render("Math Defender", True, (200, 200, 200))
        start_text = font.render("Press [ SPACEBAR ] to Start", True, (0, 255, 255))
        
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 150))
        screen.blit(subtitle_text, (SCREEN_WIDTH//2 - subtitle_text.get_width()//2, 220))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 400))

    # 🌟 วาดเกมเพลย์ปกติ ไม่ว่าจะเล่นอยู่, แพ้แล้ว, หรือกด Pause ก็ตาม
    elif state in ["playing", "game_over", "paused"]:
        if tower_level <= 4: current_tower = tower_img1
        elif tower_level <= 8: current_tower = tower_img2
        else: current_tower = tower_img3

        if current_tower:
            tower_rect = current_tower.get_rect()
            tower_rect.bottomleft = (50, 500) 
            screen.blit(current_tower, tower_rect)
        else:
            pygame.draw.rect(screen, (169, 169, 169), (50, 500 - 300, 150, 300))
        
        for e in enemies:
            if monster_img:
                screen.blit(monster_img, (e['x'], e['y'])) 
            else:
                pygame.draw.rect(screen, (200, 50, 50), (e['x'], e['y'], 50, 50)) 
                
            prob_text = small_font.render(f"{e['a']} + {e['b']}", True, (255, 255, 255))
            screen.blit(prob_text, (e['x'] + 5, e['y'] - 25))

        for p in particles:
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), 4)

        hp_text = font.render(f"HP: {tower_hp}/{max_tower_hp}", True, (255, 255, 255))
        screen.blit(hp_text, (20, 20))
        pygame.draw.rect(screen, (100, 0, 0), (140, 25, 200, 25)) 
        if tower_hp > 0:
            hp_ratio = tower_hp / max_tower_hp
            pygame.draw.rect(screen, (0, 255, 0), (140, 25, 200 * hp_ratio, 25)) 

        lvl_text = font.render(f"Level: {tower_level}/12", True, (255, 255, 0))
        xp_text = font.render(f"XP: {tower_xp} / {xp_needed}" if tower_level < 12 else "MAX LEVEL ACHIVED!", True, (0, 255, 0) if tower_level < 12 else (0, 255, 255))
        screen.blit(lvl_text, (20, 70))
        screen.blit(xp_text, (20, 110))
        
        score_text = font.render(f"Score: {score}", True, (255, 215, 0)) 
        screen.blit(score_text, (SCREEN_WIDTH - 200, 20))
        
        input_box = pygame.Rect(SCREEN_WIDTH//2 - 75, 520, 150, 50)
        pygame.draw.rect(screen, (255, 255, 255), input_box) 
        pygame.draw.rect(screen, (0, 0, 0), input_box, 3)    
        input_text = font.render(current_input, True, (0, 0, 0))
        screen.blit(input_text, (input_box.x + 10, input_box.y + 10))
        hint_text = small_font.render("Type Answer & Press ENTER", True, (200, 200, 200))
        screen.blit(hint_text, (SCREEN_WIDTH//2 - 120, 580))

        if damage_flash_alpha > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.set_alpha(damage_flash_alpha)
            flash_surface.fill((255, 0, 0)) 
            screen.blit(flash_surface, (0, 0))
            damage_flash_alpha -= 5 

        if levelup_flash_alpha > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.set_alpha(levelup_flash_alpha)
            flash_surface.fill((255, 255, 0)) 
            screen.blit(flash_surface, (0, 0))
            levelup_flash_alpha -= 5 
            
        # 🌟 วาดหน้าจอหยุดเกม (Pause Overlay)
        if state == "paused":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180) # ทำม่านสีดำโปร่งใส
            overlay.fill((0, 0, 0)) 
            screen.blit(overlay, (0, 0))
            
            pause_text = big_font.render("PAUSED", True, (255, 255, 255))
            resume_text = font.render("Press ESC to Resume", True, (200, 200, 200))
            
            screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2 + 30))

        if state == "game_over":
            over_text = big_font.render("TOWER DESTROYED!", True, (255, 0, 0))
            final_score_text = font.render(f"Final Score: {score}", True, (255, 215, 0))
            restart_text = font.render("Press 'R' to Restart", True, (255, 255, 255))
            
            screen.blit(over_text, (SCREEN_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
            screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

    pygame.display.update()
    clock.tick(60)

pygame.quit()