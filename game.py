import pygame
import random
import math
import sys

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaga Style - Multi Shot Upgrade")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)

# 시계
clock = pygame.time.Clock()
FPS = 60

# 폰트
font = pygame.font.SysFont("malgungothic", 36)
small_font = pygame.font.SysFont("malgungothic", 24)

# 배경 클래스 (스크롤링)
class Background(pygame.sprite.Sprite):
    def __init__(self, y_position):
        super().__init__()
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.image.fill((5, 5, 20))
        
        for _ in range(150):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            brightness = random.randint(100, 255)
            pygame.draw.circle(self.image, (brightness, brightness, brightness), (x, y), 1)
        
        self.rect = self.image.get_rect()
        self.rect.y = y_position
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top >= HEIGHT:
            self.rect.bottom = 0

# 플레이어 클래스 (멀티 샷 추가)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLUE, [(25, 0), (0, 40), (50, 40)])
        pygame.draw.polygon(self.image, YELLOW, [(25, 0), (15, 10), (35, 10)])
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 8
        self.lives = 3
        self.score = 0
        self.multi_shot_count = 1  # 총알 개수 (기본 1)
        self.max_multi_shot = 5    # 최대 5개

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        # 멀티 샷: 여러 총알 발사
        center_x = self.rect.centerx
        for i in range(self.multi_shot_count):
            # 각도에 따라 총알 위치 조정 (-spread ~ +spread)
            spread_angle = (self.multi_shot_count - 1) * 10  # 스프레드 각도
            angle = -spread_angle / 2 + i * (spread_angle / (self.multi_shot_count - 1) if self.multi_shot_count > 1 else 0)
            offset_x = math.sin(math.radians(angle)) * 15
            bullet_x = center_x + offset_x
            
            bullet = Bullet(bullet_x, self.rect.top, angle)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def upgrade_multi_shot(self):
        if self.multi_shot_count < self.max_multi_shot:
            self.multi_shot_count += 1

# 적군 클래스
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, RED, [(20, 0), (0, 30), (40, 30)])
        pygame.draw.circle(self.image, YELLOW, (20, 10), 4)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(1, 3)
        self.direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.speed * self.direction
        self.move_counter += 1
        if self.move_counter > 80:
            self.rect.y += 30
            self.direction *= -1
            self.move_counter = 0

# 총알 클래스 (각도 지원)
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        super().__init__()
        self.image = pygame.Surface((6, 16), pygame.SRCALPHA)
        # 총알 모양
        pygame.draw.polygon(self.image, GREEN, [(3, 0), (0, 16), (6, 16)])
        pygame.draw.polygon(self.image, YELLOW, [(3, 0), (2, 4), (4, 4)])
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 12
        self.angle = angle
        # 각도에 따른 속도 벡터
        self.dx = math.sin(math.radians(angle)) * 2
        self.dy = -self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.bottom < 0 or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()

# 스프라이트 그룹
all_sprites = pygame.sprite.Group()
background_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# 배경 생성
bg1 = Background(0)
bg2 = Background(-HEIGHT)
background_sprites.add(bg1, bg2)
all_sprites.add(bg1, bg2)

# 플레이어 생성
player = Player()
all_sprites.add(player)

# 적 생성 함수
def spawn_enemies():
    for row in range(3):
        for col in range(8):
            enemy = Enemy(100 + col * 50, 100 + row * 50)
            all_sprites.add(enemy)
            enemies.add(enemy)

spawn_enemies()

# 게임 루프
running = True
game_over = False

while running:
    clock.tick(FPS)

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.shoot()
            if event.key == pygame.K_r and game_over:
                # 재시작
                player = Player()
                all_sprites.add(player)
                for sprite in all_sprites:
                    if sprite != player and sprite not in background_sprites:
                        sprite.kill()
                spawn_enemies()
                game_over = False

    if not game_over:
        # 업데이트
        all_sprites.update()

        # 충돌: 총알 ↔ 적
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            player.score += 10
            player.upgrade_multi_shot()  # 핵심: 적 맞힐 때마다 업그레이드!

        # 충돌: 적 ↔ 플레이어
        if pygame.sprite.spritecollide(player, enemies, True):
            player.lives -= 1
            if player.lives <= 0:
                game_over = True

        # 적이 화면 아래로 내려오면 게임 오버
        for enemy in enemies:
            if enemy.rect.top > HEIGHT:
                game_over = True

        # 모든 적 제거 시 새로운 웨이브
        if len(enemies) == 0:
            spawn_enemies()

    # 화면 그리기
    screen.fill(BLACK)
    background_sprites.draw(screen)
    all_sprites.draw(screen)

    # UI 오버레이
    score_text = small_font.render(f"점수: {player.score}", True, WHITE)
    lives_text = small_font.render(f"목숨: {player.lives}", True, WHITE)
    multi_text = small_font.render(f"멀티샷: {player.multi_shot_count}/5", True, YELLOW)
    
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(multi_text, (10, 70))

    if game_over:
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = small_font.render("R 키를 눌러 재시작", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()