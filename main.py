import pygame as pg
import random,math,asyncio

settings ={
    "tekiA_tate_speed":1,
    "tekiB_tate_speed":1.5,
    "tekiC_tate_speed":2,
    "tekiA_yoko_speed":random.randint(1,2),
    "tekiB_yoko_speed":random.randint(-2,-1),
    "tekiC_yoko_speed":random.randint(1,3),
    "enemy_beam_speed":random.randint(2,3),
    "tekiA_shoot_interval":240,
    "tekiB_shoot_interval":180,
    "tekiC_shoot_interval":120,
    "boss_beam_interval":1.5,
    "boss_beam_speed":3,
    "boss_beam_radius":20,
    "explosion_volume":0.2,
    "shoot_volume":0.3,
    "boss_hp":60,
    "boss_arawaru":60, #21
    "star_blaster_speed":5
}

class ScrollingBackground:
    def __init__(self, screen, image_path, speed=1):
        self.screen = screen
        self.image = pg.image.load(image_path).convert()
        self.image = pg.transform.scale(self.image, screen.get_size())
        self.speed = speed
        self.y1 = 0
        self.y2 = -self.screen.get_height()

    def update(self):
        # 背景を下にスクロール
        self.y1 += self.speed
        self.y2 += self.speed

        # 1枚が画面下に出たら上に戻す
        if self.y1 >= self.screen.get_height():
            self.y1 = self.y2 - self.screen.get_height()
        if self.y2 >= self.screen.get_height():
            self.y2 = self.y1 - self.screen.get_height()

        # 描画
        self.screen.blit(self.image, (0, self.y1))
        self.screen.blit(self.image, (0, self.y2))

class EventScreen:
    def __init__(self, screen):
        self.screen = screen

        self.font_title = pg.font.Font("assets/fonts/NotoSansJP-VariableFont_wght.ttf", 80)
        self.font_story = pg.font.Font("assets/fonts/NotoSansJP-VariableFont_wght.ttf", 20)
        self.font_start = pg.font.Font("assets/fonts/NotoSansJP-VariableFont_wght.ttf", 30)

        # 各画面用テキスト
        self.screens = {
            "opening": {
                "title": "STAR BLASTER",
                "story": ["","宇宙には目玉星という惑星がある", "目玉星人は地球に攻めてきた", "地球人は大量の目玉に敗北した", "最後に残された戦闘機「Blaster」に乗る主人公「Star」は目玉星人に勝利できるか"],
                "start": "Sキーを押してゲームスタート"
            },
            "game_over": {
                "title": "GAME OVER",
                "story": ["やられてしまった。地球は滅亡した"],
                "start": "Sキーでリトライ"
            },
            "game_clear": {
                "title": "GAME CLEAR",
                "story": ["眼玉星人を倒した。地球に平和が戻った"],
                "start": "Sキーで再挑戦"
            }
        }

    def display(self, screen_type="opening"):
        """screen_type: 'opening', 'game_over', 'game_clear'"""
        texts = self.screens[screen_type]
        running = True
        while running:
            self.screen.fill((0, 0, 0))
            # タイトル描画
            title_surface = self.font_title.render(texts["title"], True, (255, 255, 255))
            self.screen.blit(title_surface, (self.width//2 - title_surface.get_width()//2, 200))
            # ストーリー描画
            for i, line in enumerate(texts["story"]):
                story_surface = self.font_story.render(line, True, (255, 255, 255))
                self.screen.blit(story_surface, (self.width//2 - story_surface.get_width()//2, 300 + i*50))
            # スタート文描画
            start_surface = self.font_start.render(texts["start"], True, (255, 255, 255))
            self.screen.blit(start_surface, (self.width//2 - start_surface.get_width()//2, 700))

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
                if event.type == pg.KEYDOWN and event.key == pg.K_s:
                    running = False
            pg.display.update()
        return True

class StarBlaster():
    def __init__(self, screen):
        self.sprite = pg.image.load("assets/images/star_blaster.png")
        self.sprite = pg.transform.scale(self.sprite, (50, 50))
        self.rect = pg.Rect(400, 650, 50, 70)
        self.screen = screen

        self.shoot_sound = pg.mixer.Sound("assets/sounds/beam_shoot.ogg")
        self.shoot_sound.set_volume(0.3)

        # 爆発用
        self.explosion_sprite = pg.image.load("assets/images/explosion.png")
        self.explosion_sprite = pg.transform.scale(self.explosion_sprite, (50, 50))
        self.is_exploding = False
        self.explosion_timer = 0
        self.explosion_sound = pg.mixer.Sound("assets/sounds/explosion.ogg")
        self.explosion_sound.set_volume(0.2)

    def update(self):
        if self.is_exploding:
            self.screen.blit(self.explosion_sprite, self.rect)
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.is_exploding = False
        else:
            key = pg.key.get_pressed()
            if key[pg.K_RIGHT]:
                self.rect.x += settings["star_blaster_speed"]
            if key[pg.K_LEFT]:
                self.rect.x -= settings["star_blaster_speed"]
            if key[pg.K_UP]:
                self.rect.y -= settings["star_blaster_speed"]
            if key[pg.K_DOWN]:
                self.rect.y += settings["star_blaster_speed"]

            # --- 画面の端からはみ出さないように補正 ---
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > 800:
                self.rect.right = 800
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > 800:
                self.rect.bottom = 800
            self.screen.blit(self.sprite, self.rect)

    def getRect(self):
        return self.rect

    def shoot(self):
        self.shoot_sound.play()
        return StarBlasterBeam(self.rect.centerx, self.rect.top)

    def take_damage(self):
        self.is_exploding = True
        self.explosion_timer = int(0.5 * 60)  # 0.5秒 × 60FPS
        self.explosion_sound.play()

    def get_hitbox(self):
        """当たり判定用の小さめのRectを返す"""
        hit_rect = self.rect.copy()
        hit_rect.width = int(self.rect.width * 2/3)
        hit_rect.height = int(self.rect.height * 2/3)
        # 中央に合わせる
        hit_rect.center = self.rect.center
        return hit_rect

class StarBlasterBeam():
    def __init__(self, x, y):
        self.sprite = pg.image.load("assets/images/beam_xwing.png")
        self.sprite = pg.transform.scale(self.sprite, (10, 50))
        self.rect = self.sprite.get_rect(center=(x, y))

    def update(self, screen):
        self.rect.y -= 10
        screen.blit(self.sprite, self.rect)

class EnemyBeam():
    def __init__(self, x, y, target_x, target_y, speed=settings["enemy_beam_speed"], radius=5, color=(190,0,0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

        # 移動ベクトル計算
        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1
        self.vx = dx / distance * speed
        self.vy = dy / distance * speed

        # rect は当たり判定用
        self.rect = pg.Rect(x - radius, y - radius, radius*2, radius*2)

    def update(self, screen):
        # 位置更新
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)

        # 赤い丸を描画
        pg.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class tekiA():
    def __init__(self):
        self.sprite = pg.image.load("assets/images/tekiA.png")
        self.explosion_sprite = pg.image.load("assets/images/explosion.png")
        self.explosion_sound = pg.mixer.Sound("assets/sounds/explosion.ogg")
        self.explosion_sound.set_volume(settings["explosion_volume"])
        self.sprite = pg.transform.scale(self.sprite, (90, 90))
        self.explosion_sprite = pg.transform.scale(self.explosion_sprite, (90,90))
        self.rect = pg.Rect(100, 0, 50, 70)
        self.speed = 2
        self.is_exploding = False
        self.explosion_timer = 0
        self.shoot_interval = settings["tekiA_shoot_interval"] 
        self.shoot_timer = 0

    def update(self, screen):
        self.shoot_timer += 1
        # 爆発表示タイマー
        if self.is_exploding:
            self.explosion_sound.play()
            screen.blit(self.explosion_sprite, self.rect)
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.is_exploding = False
                self.rect.x = random.randint(50, 700)
                self.rect.y = 0
        else:
           # 移動処理
            self.rect.x += settings["tekiA_yoko_speed"]
            if self.rect.x > 790:
                settings["tekiA_yoko_speed"] *= -1
            elif self.rect.x < 10:
                settings["tekiA_yoko_speed"] *= -1
            self.rect.y += settings["tekiA_tate_speed"]
            if self.rect.y > 790:
                self.rect.y = 0
            screen.blit(self.sprite, self.rect)

    def shoot_at(self, target_rect):
        """自機に向かってビームを撃つ（タイマー判定付き）"""
        if self.shoot_timer >= self.shoot_interval and not self.is_exploding:
            self.shoot_timer = 0
            return EnemyBeam(self.rect.centerx, self.rect.centery,
                             target_rect.centerx, target_rect.centery)
        return None


class tekiB():
    def __init__(self):
        self.sprite = pg.image.load("assets/images/tekiB.png")
        self.explosion_sprite = pg.image.load("assets/images/explosion.png")
        self.explosion_sound = pg.mixer.Sound("assets/sounds/explosion.ogg")
        self.explosion_sound.set_volume(settings["explosion_volume"])
        self.sprite = pg.transform.scale(self.sprite, (60, 60))
        self.explosion_sprite = pg.transform.scale(self.explosion_sprite, (60,60))
        self.rect = pg.Rect(400, 0, 50, 70)
        self.speed = 2
        self.is_exploding = False
        self.explosion_timer = 0
        self.shoot_interval = settings["tekiB_shoot_interval"]  # 3秒ごと
        self.shoot_timer = 0

    def update(self,screen):
        self.shoot_timer += 1
        # 爆発表示タイマー
        if self.is_exploding:
            self.explosion_sound.play()
            screen.blit(self.explosion_sprite, self.rect)
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.is_exploding = False
                self.rect.y = 0
                self.rect.x = random.randint(50, 700)
        else:
           # 移動処理
            self.rect.x += settings["tekiB_yoko_speed"]
            if self.rect.x > 790:
                settings["tekiB_yoko_speed"] *= -1
            elif self.rect.x < 10:
                settings["tekiB_yoko_speed"] *= -1
            self.rect.y += settings["tekiB_tate_speed"]
            if self.rect.y > 790:
                self.rect.y = 0
            
            screen.blit(self.sprite, self.rect)
    
    def shoot_at(self, target_rect):
        """自機に向かってビームを撃つ（タイマー判定付き）"""
        if self.shoot_timer >= self.shoot_interval and not self.is_exploding:
            self.shoot_timer = 0
            return EnemyBeam(self.rect.centerx, self.rect.centery,
                             target_rect.centerx, target_rect.centery)
        return None

class tekiC():
    def __init__(self):
        self.sprite = pg.image.load("assets/images/tekiC.png")
        self.explosion_sprite = pg.image.load("assets/images/explosion.png")
        self.explosion_sound = pg.mixer.Sound("assets/sounds/explosion.ogg")
        self.explosion_sound.set_volume(settings["explosion_volume"])
        self.sprite = pg.transform.scale(self.sprite, (60, 60))
        self.explosion_sprite = pg.transform.scale(self.explosion_sprite, (60,60))
        self.rect = pg.Rect(100,800, 50, 70)
        self.speed = -5
        self.is_exploding = False
        self.explosion_timer = 0
        self.shoot_interval = settings["tekiC_shoot_interval"]
        self.shoot_timer = 0

    def update(self,screen):
        self.shoot_timer += 1
        # 爆発表示タイマー
        if self.is_exploding:
            self.explosion_sound.play()
            screen.blit(self.explosion_sprite, self.rect)
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.is_exploding = False
                self.rect.y = 0
                self.rect.x = random.randint(50, 700)
        else:
           # 移動処理
            self.rect.x += settings["tekiC_yoko_speed"]
            if self.rect.x > 790:
                settings["tekiC_yoko_speed"] *= -1
            elif self.rect.x < 10:
                settings["tekiC_yoko_speed"] *= -1
            self.rect.y += settings["tekiC_tate_speed"]
            if self.rect.y > 790:
                self.rect.y = 0
            
            screen.blit(self.sprite, self.rect)

    def shoot_at(self, target_rect):
        """自機に向かってビームを撃つ（タイマー判定付き）"""
        if self.shoot_timer >= self.shoot_interval and not self.is_exploding:
            self.shoot_timer = 0
            return EnemyBeam(self.rect.centerx, self.rect.centery,
                             target_rect.centerx, target_rect.centery)
        return None

class Boss():
    def __init__(self, screen):
        self.screen = screen
        self.sprite = pg.image.load("assets/images/boss.png")
        self.sprite = pg.transform.scale(self.sprite, (200, 200))
        self.rect = self.sprite.get_rect(center=(400, 100))
        self.hp = settings["boss_hp"]
        self.is_alive = True
        self.is_exploding = False
        self.explosion_sprite = pg.image.load("assets/images/explosion.png")
        self.explosion_sprite = pg.transform.scale(self.explosion_sprite, (200, 200))
        self.explosion_timer = 0

        # BOSSの移動用
        self.speed_x = 5
        self.shoot_timer = 0  # ビーム発射タイマー

    def update(self, star_blaster_rect):
        if self.is_exploding:
            self.screen.blit(self.explosion_sprite, self.rect)
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                self.is_exploding = False
                self.is_alive = False  # 爆発後に消滅
        else:
            # 通常の左右移動やビーム射撃処理
            self.rect.x += self.speed_x
            if self.rect.right > 800 or self.rect.left < 0:
                self.speed_x *= -1
            self.screen.blit(self.sprite, self.rect)

            # ビーム射撃タイマー
            self.shoot_timer += 1
            if self.shoot_timer >= 60:
                self.shoot_timer = 0
                return self.shoot_at(star_blaster_rect)
        return None

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.is_exploding = True
            self.explosion_timer = int(0.5 * 60)

    def shoot_at(self, target_rect):
        """StarBlasterに向かってビームを撃つ（Boss専用サイズ）"""
        return EnemyBeam(
            self.rect.centerx,
            self.rect.centery,
            target_rect.centerx,
            target_rect.centery,
            speed=settings["boss_beam_speed"],
            radius=settings["boss_beam_radius"],       # ← ここで大きさを指定
            color=(180, 0, 0)
        )

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0 and not self.is_exploding:
            self.is_exploding = True
            self.explosion_timer = int(2 * 60)  # 2秒 × 60FPS


def check_starblaster_hit(star_blaster, tekis, enemy_beams, boss):
    player_rect = star_blaster.get_hitbox()
    
    # 1. 敵ビームに当たった場合
    for beam in enemy_beams[:]:
        if beam.rect.colliderect(player_rect):
            print("StarBlaster が敵ビームにヒット！")
            enemy_beams.remove(beam)
            star_blaster_explode(star_blaster)
            return True  # 爆発した

    # 2. 敵本体に当たった場合
    for teki in tekis:
        if not teki.is_exploding and player_rect.colliderect(teki.rect):
            print("StarBlaster が敵に接触！")
            teki.is_exploding = True
            teki.explosion_timer = int(0.3 * 60)
            star_blaster_explode(star_blaster)
            return True

    # 3. BOSS に当たった場合
    if boss and boss.is_alive and not boss.is_exploding and player_rect.colliderect(boss.rect):
        print("StarBlaster が BOSS に接触！")
        star_blaster_explode(star_blaster)
        return True

    return False  # 爆発なし

# StarBlaster 爆発処理
def star_blaster_explode(star_blaster):
    # 爆発アニメーション用のフラグ・タイマーを設定
    star_blaster.is_exploding = True
    star_blaster.explosion_timer = int(0.5 * 60)  # 0.5秒 × 60FPS
    # 爆発音
    star_blaster.explosion_sound.play()

async def main():
    # --- Pygame初期化 ---
    pg.init()
    screen = pg.display.set_mode((800,800))
    pg.display.set_caption("StarBlaster!")
    clock = pg.time.Clock()
    width, height = screen.get_size()

    # --- フォント ---
    font_title = pg.font.Font("assets/fonts/NotoSansJP-VariableFont_wght.ttf", 80)
    font_story = pg.font.Font("assets/fonts/NotoSansJP-VariableFont_wght.ttf", 20)
    font_start = pg.font.Font("assets/fonts/NotoSansJP-VariableFont_wght.ttf", 30)

    # --- 画面テキスト ---
    screens = {
        "opening": {
            "title": "STAR BLASTER",
            "story": ["","宇宙には目玉星という惑星がある",
                      "目玉星人は地球に攻めてきた",
                      "地球人は大量の目玉に敗北した",
                      "最後に残された戦闘機「Blaster」に乗る主人公「Star」は目玉星人に勝利できるか"],
            "start": "Sキーを押してゲームスタート"
        },
        "game_over": {
            "title": "GAME OVER",
            "story": ["やられてしまった。地球は滅亡した"],
            "start": "Sキーでリトライ"
        },
        "game_clear": {
            "title": "GAME CLEAR",
            "story": ["眼玉星人を倒した。地球に平和が戻った"],
            "start": "Sキーで再挑戦"
        }
    }

    # --- ゲームオブジェクト ---
    star_blaster = StarBlaster(screen)
    beams = []
    enemy_beams = []
    tekis = [tekiA(), tekiB(), tekiC()]
    boss = None
    defeated_count = 0

    # --- 背景 ---
    bg_game = ScrollingBackground(screen, "assets/images/background.png", speed=1)
    bg_opening = pg.image.load("assets/images/background.png")
    bg_opening = pg.transform.scale(bg_opening, (800,800))

    # --- BGM ---
    pg.mixer.music.load("assets/sounds/Begining.ogg")
    pg.mixer.music.play(-1)

    # --- 画面状態 ---
    show_opening = True
    show_game_over = False
    show_game_clear = False

    running = True
    while running:
        # --- 背景描画 ---
        if show_opening:
            screen.blit(bg_opening, (0,0))
        else:
            bg_game.update()

        # --- オープニング・ゲームオーバー・クリア ---
        texts = None
        if show_opening:
            texts = screens["opening"]
        elif show_game_over:
            texts = screens["game_over"]
        elif show_game_clear:
            texts = screens["game_clear"]

        if texts:
            # タイトル描画
            title_surface = font_title.render(texts["title"], True, (255,255,255))
            screen.blit(title_surface, (width//2 - title_surface.get_width()//2, 200))
            # ストーリー描画
            for i, line in enumerate(texts["story"]):
                story_surface = font_story.render(line, True, (255,255,255))
                screen.blit(story_surface, (width//2 - story_surface.get_width()//2, 300 + i*50))
            # スタート文描画
            start_surface = font_start.render(texts["start"], True, (255,255,255))
            screen.blit(start_surface, (width//2 - start_surface.get_width()//2, 700))
        else:
            # --- ゲーム本編 ---
            star_blaster.update()

            # プレイヤービーム更新
            for beam in beams[:]:
                beam.update(screen)
                if beam.rect.bottom < 0:
                    beams.remove(beam)

            # 敵更新と射撃
            for teki in tekis:
                teki.update(screen)
                beam = teki.shoot_at(star_blaster.getRect())
                if beam:
                    enemy_beams.append(beam)

            # 敵ビーム更新
            for beam in enemy_beams[:]:
                beam.update(screen)
                if beam.rect.top > 800 or beam.rect.bottom < 0:
                    enemy_beams.remove(beam)

            # プレイヤービームと敵衝突判定
            for teki in tekis:
                for beam in beams[:]:
                    if teki.rect.colliderect(beam.rect):
                        teki.is_exploding = True
                        teki.explosion_timer = int(0.3*60)
                        beams.remove(beam)
                        defeated_count += 1

            # BOSS出現
            if defeated_count >= settings["boss_arawaru"] and boss is None:
                boss = Boss(screen)
                pg.mixer.music.stop()
                pg.mixer.music.load("assets/sounds/FightingBoss.ogg")
                pg.mixer.music.play(-1)

            if boss:
                boss_beam = boss.update(star_blaster.getRect())
                if boss_beam:
                    enemy_beams.append(boss_beam)
                for beam in beams[:]:
                    if boss.rect.colliderect(beam.rect) and boss.is_alive:
                        boss.take_damage(1)
                        beams.remove(beam)

            # プレイヤー当たり判定
            if check_starblaster_hit(star_blaster, tekis, enemy_beams, boss):
                star_blaster.is_exploding = True
                star_blaster.explosion_timer = int(1*60)
                show_game_over = True

            # BOSS倒したらゲームクリア
            if boss and not boss.is_alive and not boss.is_exploding:
                show_game_clear = True

        # --- イベント処理 ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_s:
                if show_opening:
                    # オープニング終了
                    show_opening = False
                    pg.mixer.music.stop()
                    pg.mixer.music.load("assets/sounds/Fighting.ogg")
                    pg.mixer.music.play(-1)
                elif show_game_over or show_game_clear:
                    # ゲーム再挑戦
                    show_game_over = show_game_clear = False
                    star_blaster = StarBlaster(screen)
                    beams.clear()
                    enemy_beams.clear()
                    defeated_count = 0
                    tekis = [tekiA(), tekiB(), tekiC()]
                    boss = None
                    pg.mixer.music.stop()
                    pg.mixer.music.load("assets/sounds/Fighting.ogg")
                    pg.mixer.music.play(-1)
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE and not (show_opening or show_game_over or show_game_clear):
                beams.append(star_blaster.shoot())

        # 画面更新
        pg.display.update()
        clock.tick(60)
        await asyncio.sleep(1/60)

asyncio.run(main())

