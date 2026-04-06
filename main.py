"""
4 Фото 1 Слово — Python + Pygame
=================================
Установка:  pip install pygame
Запуск:     python game_4pic1word.py

Изображения (опционально):
  images/level1/img1.png … img4.png
  …
  images/level10/img1.png … img4.png
Если файлов нет — используются цветные заглушки.
"""

import pygame
import sys
import os
import math
import random

# ──────────────────────────────────────────────────────────────
#  НАСТРОЙКИ
# ──────────────────────────────────────────────────────────────
WIN_W, WIN_H = 880, 760
FPS = 60

# ──────────────────────────────────────────────────────────────
#  ПАЛИТРА
# ──────────────────────────────────────────────────────────────
C = {
    "bg":        ( 10,  13,  20),
    "surface":   ( 18,  23,  35),
    "surface2":  ( 26,  34,  52),
    "surface3":  ( 34,  44,  66),
    "border":    ( 50,  65,  95),
    "accent":    ( 56, 189, 248),   # голубой
    "accent2":   ( 99, 102, 241),   # индиго
    "success":   ( 52, 211, 153),
    "danger":    (248, 113, 113),
    "warn":      (251, 191,  36),
    "text":      (225, 235, 250),
    "text_dim":  ( 85, 105, 138),
}

# ──────────────────────────────────────────────────────────────
#  УРОВНИ
# ──────────────────────────────────────────────────────────────
LEVELS = [
    {"word": "ТОЧКА",   "hint": "Знак препинания или координата"},
    {"word": "ВЫБОР",   "hint": "Принятие одного из нескольких решений"},
    {"word": "ЛИМИТ",   "hint": "Ограничение или предельное значение"},
    {"word": "ПЛАН",    "hint": "Схема действий или архитектурный чертёж"},
    {"word": "СПИРАЛЬ", "hint": "Линия, закрученная витками"},
    {"word": "ПОГОДА",  "hint": "Состояние атмосферы: дождь, снег, солнце"},
    {"word": "ГЛАСНЫЕ", "hint": "А, Е, Ё, И, О, У, Ы, Э, Ю, Я"},
    {"word": "ПЛАТИТЬ", "hint": "Расплачиваться деньгами"},
    {"word": "СЕЗОНЫ",  "hint": "Весна, Лето, Осень, Зима"},
    {"word": "ДЕРЕВО",  "hint": "Растение с корнями, стволом и ветвями"},
]

RUSSIAN = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯ"


# ──────────────────────────────────────────────────────────────
#  УТИЛИТЫ
# ──────────────────────────────────────────────────────────────
def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def draw_rrect(surf, color, rect, r=10, border=0, bcol=None):
    pygame.draw.rect(surf, color, pygame.Rect(rect), border_radius=r)
    if border and bcol:
        pygame.draw.rect(surf, bcol, pygame.Rect(rect), border, border_radius=r)


def draw_shadow(surf, rect, r=10, alpha=55, offset=5):
    sw = rect[2] + offset * 2
    sh = rect[3] + offset * 2
    s = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.rect(s, (0, 0, 0, alpha), (0, 0, sw, sh), border_radius=r + 2)
    surf.blit(s, (rect[0] - offset, rect[1] + offset // 2))


def make_placeholder(size, level_idx, img_idx):
    """Квадратная цветная заглушка с градиентом и узором."""
    w = h = size
    surf = pygame.Surface((w, h))
    palettes = [
        [(12, 20, 48), (30, 58, 138), (37, 99, 235)],
        [(22, 8,  35), (88, 28, 135), (147, 51, 234)],
        [(5,  25, 18), (6,  78,  59), (16, 185, 129)],
        [(38, 5,   5), (127,29,  29), (220, 38,  38)],
        [(8,  22, 35), (21, 94, 117), (6,  182, 212)],
        [(32, 22,  4), (113,63,  18), (217,119,   6)],
        [(8,  14, 32), (29, 78, 216), (96, 165, 250)],
        [(4,  24, 10), (20, 83,  45), (34, 197,  94)],
        [(26, 8,  26), (86,  7,  78), (168, 85, 247)],
        [(18, 18, 18), (51, 65,  85), (148,163, 184)],
    ]
    cols = palettes[level_idx % len(palettes)]
    for y in range(h):
        t = y / h
        if t < 0.5:
            col = tuple(int(lerp(cols[0][i], cols[1][i], t * 2)) for i in range(3))
        else:
            col = tuple(int(lerp(cols[1][i], cols[2][i], (t - 0.5) * 2)) for i in range(3))
        pygame.draw.line(surf, col, (0, y), (w, y))
    rng = random.Random(level_idx * 100 + img_idx)
    for _ in range(7):
        cx = rng.randint(0, w); cy = rng.randint(0, h)
        cr = rng.randint(15, w // 3)
        a  = rng.randint(20, 70)
        s2 = pygame.Surface((cr*2, cr*2), pygame.SRCALPHA)
        pygame.draw.circle(s2, (*cols[2], a), (cr, cr), cr)
        surf.blit(s2, (cx - cr, cy - cr))
    try:
        fnt = pygame.font.SysFont("Arial", max(14, size // 10), bold=True)
    except Exception:
        fnt = pygame.font.Font(None, max(16, size // 9))
    lbl = fnt.render(f"Фото {img_idx}", True, (255, 255, 255))
    surf.blit(lbl, (w // 2 - lbl.get_width() // 2, h // 2 - lbl.get_height() // 2))
    return surf


def load_images(level_idx, img_size):
    """Загружает 4 КВАДРАТНЫХ изображения (img_size × img_size)."""
    imgs = []
    for i in range(1, 5):
        path = os.path.join("images", f"level{level_idx + 1}", f"img{i}.png")
        loaded = False
        if os.path.exists(path):
            try:
                raw = pygame.image.load(path).convert()
                # crop to square from center, then scale
                rw, rh = raw.get_size()
                sq = min(rw, rh)
                crop = pygame.Surface((sq, sq))
                crop.blit(raw, (-(rw - sq) // 2, -(rh - sq) // 2))
                imgs.append(pygame.transform.smoothscale(crop, (img_size, img_size)))
                loaded = True
            except Exception:
                pass
        if not loaded:
            imgs.append(make_placeholder(img_size, level_idx, i))
    return imgs


def build_pool(word):
    """12 букв: все буквы слова + случайные лишние, перемешанные."""
    letters = list(word)
    rng = random.Random(sum(ord(c) for c in word))
    extras = [rng.choice(RUSSIAN) for _ in range(max(0, 12 - len(letters)))]
    pool = (letters + extras)[:12]
    rng.shuffle(pool)
    return pool


# ──────────────────────────────────────────────────────────────
#  КОМПОНЕНТ: АНИМИРОВАННАЯ КНОПКА
# ──────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, text, bg, fg=None, radius=10, font=None):
        self.rect   = pygame.Rect(rect)
        self.text   = text
        self.bg     = bg
        self.fg     = fg or C["text"]
        self.radius = radius
        self.font   = font
        self.hover  = 0.0
        self.press  = 0.0
        self._held  = False
        self.clicked = False

    def update(self, dt, mpos, mdown):
        over = self.rect.collidepoint(mpos)
        self.hover = lerp(self.hover, 1.0 if over else 0.0, dt * 12)
        if over and mdown and not self._held:
            self._held = True
            self.press = 1.0
            self.clicked = True
        if not mdown:
            self._held = False
        self.press = lerp(self.press, 0.0, dt * 9)

    def draw(self, surf, override_bg=None, override_fg=None):
        scale = 1.0 - self.press * 0.05
        cx, cy = self.rect.center
        dw = int(self.rect.w * scale)
        dh = int(self.rect.h * scale)
        dr = pygame.Rect(cx - dw // 2, cy - dh // 2, dw, dh)

        bg = override_bg or self.bg
        fg = override_fg or self.fg

        if override_bg is None and self.hover > 0.05:
            gs = pygame.Surface((dw + 18, dh + 12), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*self.bg, int(35 * self.hover)),
                             (0, 0, dw + 18, dh + 12), border_radius=self.radius + 3)
            surf.blit(gs, (dr.x - 9, dr.y - 6))

        if override_bg is None:
            bg = tuple(clamp(int(c + self.hover * 22), 0, 255) for c in self.bg)

        draw_rrect(surf, bg, dr, self.radius)

        if self.font and self.text:
            lbl = self.font.render(self.text, True, fg)
            surf.blit(lbl, (dr.centerx - lbl.get_width() // 2,
                            dr.centery - lbl.get_height() // 2))


# ──────────────────────────────────────────────────────────────
#  КОМПОНЕНТ: ВСПЛЫВАЮЩЕЕ СООБЩЕНИЕ
# ──────────────────────────────────────────────────────────────
class Toast:
    def __init__(self):
        self.text  = ""
        self.color = C["text"]
        self.timer = 0.0

    def show(self, text, color=None, dur=2.2):
        self.text  = text
        self.color = color or C["text"]
        self.timer = dur

    def update(self, dt):
        if self.timer > 0:
            self.timer -= dt

    def draw(self, surf, cx, y, font):
        if self.timer <= 0 or not self.text:
            return
        a = int(255 * min(1.0, self.timer / 0.45))
        lbl = font.render(self.text, True, self.color)
        lw, lh = lbl.get_size()
        pad = 14
        bg = pygame.Surface((lw + pad * 2, lh + pad), pygame.SRCALPHA)
        pygame.draw.rect(bg, (0, 0, 0, 160), (0, 0, lw + pad * 2, lh + pad), border_radius=10)
        bg.set_alpha(a)
        lbl.set_alpha(a)
        surf.blit(bg, (cx - (lw + pad * 2) // 2, y))
        surf.blit(lbl, (cx - lw // 2, y + pad // 2))


# ──────────────────────────────────────────────────────────────
#  БАЗОВЫЙ ЭКРАН
# ──────────────────────────────────────────────────────────────
class Screen:
    def __init__(self, game):
        self.game = game

    def on_enter(self): pass
    def handle_event(self, e): pass
    def update(self, dt, mpos, mdown): pass
    def draw(self, surf): pass


# ──────────────────────────────────────────────────────────────
#  ЭКРАН: ГЛАВНОЕ МЕНЮ
# ──────────────────────────────────────────────────────────────
class MenuScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.angle = 0.0
        self.btn_play = None

    def on_enter(self):
        g = self.game
        W, H = g.W, g.H
        bw, bh = int(W * 0.38), int(H * 0.075)
        self.btn_play = Button(
            (W // 2 - bw // 2, int(H * 0.60), bw, bh),
            "ИГРАТЬ", C["accent"], C["bg"], radius=14, font=g.f_btn
        )

    def update(self, dt, mpos, mdown):
        self.angle += dt * 14
        self.btn_play.update(dt, mpos, mdown)
        if self.btn_play.clicked:
            self.btn_play.clicked = False
            self.game.start_game()

    def draw(self, surf):
        g = self.game
        W, H = g.W, g.H
        surf.fill(C["bg"])

        # декоративные кольца
        for i in range(6):
            a = math.radians(self.angle + i * 60)
            r_orbit = int(W * 0.18)
            ox = W // 2 + int(math.cos(a) * r_orbit * 0.25)
            oy = int(H * 0.28) + int(math.sin(a) * r_orbit * 0.12)
            cr = int(W * 0.20) - i * 12
            if cr < 5: continue
            s = pygame.Surface((cr * 2, cr * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*C["accent"], 10 + i * 5), (cr, cr), cr, 2)
            surf.blit(s, (ox - cr, oy - cr))

        # заголовок
        t1 = g.f_title.render("4 ФОТО", True, C["text"])
        t2 = g.f_title.render("1 СЛОВО", True, C["accent"])
        ty = int(H * 0.18)
        surf.blit(t1, (W // 2 - t1.get_width() // 2, ty))
        surf.blit(t2, (W // 2 - t2.get_width() // 2, ty + t1.get_height() + 4))

        sub = g.f_small.render("Угадай слово по четырём картинкам", True, C["text_dim"])
        surf.blit(sub, (W // 2 - sub.get_width() // 2, int(H * 0.46)))

        best = g.f_small.render(f"Лучший результат: {g.best_score} очков", True, C["text_dim"])
        surf.blit(best, (W // 2 - best.get_width() // 2, int(H * 0.52)))

        self.btn_play.draw(surf)

        note = g.f_tiny.render("10 уровней  ·  подсказки  ·  система очков", True, C["text_dim"])
        surf.blit(note, (W // 2 - note.get_width() // 2, int(H * 0.88)))


# ──────────────────────────────────────────────────────────────
#  LAYOUT ИГРОВОГО ЭКРАНА  (все размеры считаются ЗДЕСЬ)
# ──────────────────────────────────────────────────────────────
def compute_layout(W, H, word_len):
    """
    Делит экран на зоны сверху вниз с гарантированными отступами:
      [HEADER]  h=50
      [IMAGES]  квадратная сетка 2×2
      [HINT]    одна строка
      [SLOTS]   слоты ответа
      [LETTERS] 2 ряда кнопок-букв
      [ACTIONS] кнопки управления
      [TOAST]   последняя строка
    """
    PAD   = 14         # внешний отступ по бокам
    GAP   = 8          # зазор между картинками / элементами
    HDR_H = 50
    HINT_H = 22
    SLOT_SECTION = 72  # зона слотов
    LETTER_ROWS  = 2
    LETTER_BTN_H = 46
    ACTION_H     = 50
    TOAST_H      = 36

    # высота картинок: оставшееся место
    available_img_h = (H
                       - HDR_H
                       - GAP
                       - HINT_H - GAP
                       - SLOT_SECTION - GAP
                       - LETTER_ROWS * LETTER_BTN_H + (LETTER_ROWS - 1) * GAP - GAP
                       - ACTION_H - GAP
                       - TOAST_H - GAP * 2)

    # квадратная сетка: img_size ограничен и шириной и доступной высотой
    max_by_w = (W - PAD * 2 - GAP) // 2
    max_by_h = (available_img_h - GAP) // 2
    img_size = max(40, min(max_by_w, max_by_h))

    grid_w = img_size * 2 + GAP
    grid_h = img_size * 2 + GAP
    grid_x = W // 2 - grid_w // 2
    grid_y = HDR_H + GAP

    hint_y = grid_y + grid_h + 6

    # слоты
    MAX_SLOT = 56
    slot_size = min(MAX_SLOT, (W - PAD * 2 - (word_len - 1) * 6) // max(word_len, 1))
    slot_size = max(28, slot_size)
    slots_total_w = word_len * slot_size + (word_len - 1) * 6
    slots_x = W // 2 - slots_total_w // 2
    slots_y = hint_y + HINT_H + 8

    # кнопки-буквы (12 шт, 2 ряда × 6)
    COLS = 6
    btn_gap_x = 6
    btn_gap_y = 6
    btn_w = min(66, (W - PAD * 2 - (COLS - 1) * btn_gap_x) // COLS)
    btn_w = max(40, btn_w)
    btn_h = LETTER_BTN_H
    letters_total_w = COLS * btn_w + (COLS - 1) * btn_gap_x
    letters_x = W // 2 - letters_total_w // 2
    letters_y = slots_y + slot_size + 12

    # кнопки управления
    actions_y = letters_y + LETTER_ROWS * btn_h + (LETTER_ROWS - 1) * btn_gap_y + 12
    act_h = ACTION_H
    act_gap = 8
    act_w = (W - PAD * 2 - act_gap * 2) // 3

    toast_y = actions_y + act_h + 8

    return {
        "PAD": PAD, "GAP": GAP, "HDR_H": HDR_H,
        "img_size": img_size,
        "grid_x": grid_x, "grid_y": grid_y, "grid_w": grid_w, "grid_h": grid_h,
        "hint_y": hint_y,
        "slot_size": slot_size, "slots_x": slots_x, "slots_y": slots_y,
        "btn_w": btn_w, "btn_h": btn_h,
        "btn_gap_x": btn_gap_x, "btn_gap_y": btn_gap_y,
        "letters_x": letters_x, "letters_y": letters_y, "COLS": COLS,
        "actions_y": actions_y, "act_h": act_h, "act_w": act_w, "act_gap": act_gap,
        "toast_y": toast_y,
    }


# ──────────────────────────────────────────────────────────────
#  ЭКРАН: ИГРОВОЙ ПРОЦЕСС
# ──────────────────────────────────────────────────────────────
class GameScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.level_idx   = 0
        self.score       = 0
        self.word        = ""
        self.pool        = []          # list of {"char": str, "used": bool}
        self.slots       = []          # list of pool_idx | None
        self.revealed    = set()       # slot indices opened by hint
        self.images      = []
        self.toast       = Toast()
        self.success_t   = 0.0
        self.lyt         = {}
        # кнопки
        self.letter_btns = []
        self.slot_rects  = []
        self.btn_check   = None
        self.btn_hint    = None
        self.btn_del     = None
        self.btn_menu    = None

    # ── инициализация уровня ─────────────────────────────────
    def on_enter(self):
        self.level_idx = 0
        self.score = 0
        self._load_level()

    def _load_level(self):
        self.word        = LEVELS[self.level_idx]["word"]
        self.revealed    = set()
        self.success_t   = 0.0
        self.level_solved = False          # ← флаг: уровень уже решён
        raw_pool = build_pool(self.word)
        self.pool  = [{"char": c, "used": False} for c in raw_pool]
        self.slots = [None] * len(self.word)
        self._rebuild(reload_images=True)

    def _rebuild(self, reload_images=False):
        g   = self.game
        W, H = g.W, g.H
        L   = compute_layout(W, H, len(self.word))
        self.lyt = L

        if reload_images:
            self.images = load_images(self.level_idx, L["img_size"])

        # слоты ответа
        self.slot_rects = []
        for i in range(len(self.word)):
            rx = L["slots_x"] + i * (L["slot_size"] + 6)
            self.slot_rects.append(
                pygame.Rect(rx, L["slots_y"], L["slot_size"], L["slot_size"])
            )

        # кнопки-буквы
        self.letter_btns = []
        for i, pdata in enumerate(self.pool):
            col = i % L["COLS"]
            row = i // L["COLS"]
            rx = L["letters_x"] + col * (L["btn_w"] + L["btn_gap_x"])
            ry = L["letters_y"] + row * (L["btn_h"] + L["btn_gap_y"])
            btn = Button(
                (rx, ry, L["btn_w"], L["btn_h"]),
                pdata["char"], C["surface2"], C["text"],
                radius=10, font=g.f_letter
            )
            self.letter_btns.append(btn)

        # кнопки управления
        ay   = L["actions_y"]
        ah   = L["act_h"]
        aw   = L["act_w"]
        ag   = L["act_gap"]
        pad  = L["PAD"]
        x0   = pad

        self.btn_del   = Button((x0,           ay, aw, ah), "УДАЛИТЬ",
                                C["surface3"], C["text_dim"], radius=11, font=g.f_btn)
        self.btn_check = Button((x0 + aw + ag, ay, aw, ah), "ПРОВЕРИТЬ",
                                C["accent2"],  C["text"],    radius=11, font=g.f_btn)
        self.btn_hint  = Button((x0 + (aw + ag) * 2, ay, aw, ah), "ПОДСКАЗКА",
                                C["warn"],     C["bg"],      radius=11, font=g.f_btn)

        self.btn_menu  = Button(
            (pad, 8, int(W * 0.13), 34),
            "← МЕНЮ", C["surface2"], C["text_dim"], radius=8, font=g.f_tiny
        )

    # ── логика ──────────────────────────────────────────────
    def _first_empty(self):
        for i, v in enumerate(self.slots):
            if v is None:
                return i
        return None

    def _place(self, pool_idx):
        slot = self._first_empty()
        if slot is None:
            return
        p = self.pool[pool_idx]
        if p["used"]:
            return
        p["used"] = True
        self.slots[slot] = pool_idx

    def _remove_slot(self, idx):
        if idx in self.revealed:
            return
        pi = self.slots[idx]
        if pi is not None:
            self.pool[pi]["used"] = False
            self.slots[idx] = None

    def _remove_last(self):
        for i in range(len(self.slots) - 1, -1, -1):
            if self.slots[i] is not None and i not in self.revealed:
                self.pool[self.slots[i]]["used"] = False
                self.slots[i] = None
                return

    def _check(self):
        if self.level_solved:              # ← уже решён — игнорируем
            return
        guess = "".join(
            self.pool[v]["char"] if v is not None else "?" for v in self.slots
        )
        if "?" in guess:
            self.toast.show("Заполни все буквы!", C["warn"])
            return
        if guess == self.word:
            self.level_solved = True       # ← блокируем повторное нажатие
            bonus = max(10, 100 - len(self.revealed) * 20)
            self.score += bonus
            self.success_t = 1.0
            self.toast.show(f"Верно!  +{bonus} очков", C["success"], 2.4)
            pygame.time.set_timer(pygame.USEREVENT + 1, 1900)
        else:
            self.toast.show("Неверно — попробуй ещё!", C["danger"])

    def _hint(self):
        if self.score < 20:
            self.toast.show("Нужно минимум 20 очков для подсказки", C["warn"])
            return
        for i, ch in enumerate(self.word):
            if i not in self.revealed:
                self._remove_slot(i)
                placed = False
                for pi, p in enumerate(self.pool):
                    if p["char"] == ch and not p["used"]:
                        p["used"] = True
                        self.slots[i] = pi
                        placed = True
                        break
                if not placed:
                    # добавляем букву в пул
                    self.pool.append({"char": ch, "used": True})
                    self.slots[i] = len(self.pool) - 1
                    self.letter_btns.append(None)
                self.revealed.add(i)
                self.score = max(0, self.score - 20)
                self.toast.show(f"Буква «{ch}» открыта  (−20 очков)", C["warn"])
                return
        self.toast.show("Все буквы уже открыты!", C["text_dim"])

    # ── события / обновление ────────────────────────────────
    def handle_event(self, e):
        if e.type == pygame.USEREVENT + 1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            self.level_idx += 1
            if self.level_idx >= len(LEVELS):
                self.game.end_game(self.score)
            else:
                self._load_level()
            return

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if not self.level_solved:
                for i, rect in enumerate(self.slot_rects):
                    if rect.collidepoint(e.pos) and self.slots[i] is not None:
                        self._remove_slot(i)
                        return

    def update(self, dt, mpos, mdown):
        g = self.game
        self.toast.update(dt)
        self.success_t = max(0.0, self.success_t - dt * 0.7)

        self.btn_menu.update(dt, mpos, mdown)

        # после решения — только кнопка меню остаётся активной
        if not self.level_solved:
            self.btn_del.update(dt, mpos, mdown)
            self.btn_check.update(dt, mpos, mdown)
            self.btn_hint.update(dt, mpos, mdown)

            for i, btn in enumerate(self.letter_btns):
                if btn is None: continue
                btn.update(dt, mpos, mdown)
                if btn.clicked:
                    btn.clicked = False
                    self._place(i)

        if self.btn_menu.clicked:
            self.btn_menu.clicked = False
            g.best_score = max(g.best_score, self.score)
            g.show_menu()
        if not self.level_solved:
            if self.btn_del.clicked:
                self.btn_del.clicked = False
                self._remove_last()
            if self.btn_check.clicked:
                self.btn_check.clicked = False
                self._check()
            if self.btn_hint.clicked:
                self.btn_hint.clicked = False
                self._hint()

    # ── отрисовка ───────────────────────────────────────────
    def draw(self, surf):
        g = self.game
        W, H = g.W, g.H
        L = self.lyt
        surf.fill(C["bg"])

        # ── header ──
        hdr = pygame.Surface((W, L["HDR_H"]), pygame.SRCALPHA)
        hdr.fill((*C["surface"], 220))
        surf.blit(hdr, (0, 0))

        lvl_lbl = g.f_small.render(
            f"УРОВЕНЬ  {self.level_idx + 1} / {len(LEVELS)}", True, C["text_dim"])
        surf.blit(lvl_lbl, (W // 2 - lvl_lbl.get_width() // 2,
                            L["HDR_H"] // 2 - lvl_lbl.get_height() // 2))

        sc_lbl = g.f_small.render(f"Очки: {self.score}", True, C["accent"])
        surf.blit(sc_lbl, (W - sc_lbl.get_width() - L["PAD"],
                           L["HDR_H"] // 2 - sc_lbl.get_height() // 2))

        self.btn_menu.draw(surf)

        # ── прогресс-бар ──
        bar_y = L["HDR_H"] - 3
        bar_w = int(W * (self.level_idx / len(LEVELS)))
        pygame.draw.rect(surf, C["surface3"], (0, bar_y, W, 3))
        if bar_w > 0:
            pygame.draw.rect(surf, C["accent"], (0, bar_y, bar_w, 3))

        # ── 4 изображения (квадраты 2×2) ──
        s = L["img_size"]
        gx, gy = L["grid_x"], L["grid_y"]
        g_ = L["GAP"]
        positions = [
            (gx,         gy),
            (gx + s + g_, gy),
            (gx,         gy + s + g_),
            (gx + s + g_, gy + s + g_),
        ]
        for idx, (ix, iy) in enumerate(positions):
            draw_shadow(surf, (ix, iy, s, s), r=10, alpha=50)
            surf.blit(self.images[idx], (ix, iy))
            pygame.draw.rect(surf, C["border"], (ix, iy, s, s), 2, border_radius=10)

        # ── подсказка уровня ──
        hint_str = LEVELS[self.level_idx]["hint"]
        hint_lbl = g.f_tiny.render(hint_str, True, C["text_dim"])
        surf.blit(hint_lbl, (W // 2 - hint_lbl.get_width() // 2, L["hint_y"]))

        # ── слоты ответа ──
        for i, rect in enumerate(self.slot_rects):
            is_rev  = i in self.revealed
            filled  = self.slots[i] is not None
            if self.success_t > 0.01:
                bg = tuple(int(lerp(C["surface2"][j], C["success"][j],
                                    self.success_t * 0.55)) for j in range(3))
                bc = C["success"]
            else:
                bg = C["surface"] if filled else C["surface2"]
                bc = C["accent"] if is_rev else (C["accent"] if filled else C["border"])

            draw_shadow(surf, rect, r=8, alpha=30)
            draw_rrect(surf, bg, rect, r=8, border=2, bcol=bc)

            if filled:
                pi   = self.slots[i]
                char = self.pool[pi]["char"] if pi < len(self.pool) else "?"
                col  = C["accent"] if is_rev else C["text"]
                lbl  = g.f_letter.render(char, True, col)
                surf.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                                rect.centery - lbl.get_height() // 2))
            else:
                # пустой слот — маленький квадратик-индикатор
                sq = 6
                pygame.draw.rect(surf, C["border"],
                                 (rect.centerx - sq // 2,
                                  rect.centery - sq // 2, sq, sq), border_radius=2)

        # ── кнопки-буквы ──
        for i, btn in enumerate(self.letter_btns):
            if btn is None: continue
            p = self.pool[i]
            if p["used"]:
                s2 = pygame.Surface((btn.rect.w, btn.rect.h), pygame.SRCALPHA)
                pygame.draw.rect(s2, (*C["surface"], 60),
                                 (0, 0, btn.rect.w, btn.rect.h), border_radius=10)
                surf.blit(s2, btn.rect.topleft)
                # затемнённый текст
                dim = g.f_letter.render(p["char"], True, C["text_dim"])
                surf.blit(dim, (btn.rect.centerx - dim.get_width() // 2,
                                btn.rect.centery - dim.get_height() // 2))
            else:
                draw_shadow(surf, btn.rect, r=10, alpha=25)
                btn.draw(surf)

        # ── кнопки управления ──
        if self.level_solved:
            # затемняем все кнопки кроме меню
            for btn in (self.btn_del, self.btn_check, self.btn_hint):
                btn.draw(surf, override_bg=C["surface"], override_fg=C["text_dim"])
        else:
            self.btn_del.draw(surf)
            self.btn_check.draw(surf)
            self.btn_hint.draw(surf)

        # ── toast ──
        self.toast.draw(surf, W // 2, L["toast_y"], g.f_small)


# ──────────────────────────────────────────────────────────────
#  ЭКРАН: ФИНАЛ
# ──────────────────────────────────────────────────────────────
class EndScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.angle = 0.0
        self.btn_menu  = None
        self.btn_again = None

    def on_enter(self):
        g = self.game
        W, H = g.W, g.H
        bw, bh = int(W * 0.3), int(H * 0.075)
        self.btn_menu  = Button(
            (W // 2 - bw - 10, int(H * 0.68), bw, bh),
            "МЕНЮ", C["surface3"], C["text"], radius=12, font=g.f_btn)
        self.btn_again = Button(
            (W // 2 + 10, int(H * 0.68), bw, bh),
            "ЕЩЁ РАЗ", C["accent"], C["bg"], radius=12, font=g.f_btn)

    def update(self, dt, mpos, mdown):
        self.angle += dt * 18
        self.btn_menu.update(dt, mpos, mdown)
        self.btn_again.update(dt, mpos, mdown)
        if self.btn_menu.clicked:
            self.btn_menu.clicked = False
            self.game.show_menu()
        if self.btn_again.clicked:
            self.btn_again.clicked = False
            self.game.start_game()

    def draw(self, surf):
        g = self.game
        W, H = g.W, g.H
        surf.fill(C["bg"])

        for i in range(9):
            a = math.radians(self.angle + i * 40)
            r = int(W * 0.28)
            cr = 55 - i * 5
            if cr < 4: continue
            cx = W // 2 + int(math.cos(a) * r * 0.28)
            cy = int(H * 0.35) + int(math.sin(a) * r * 0.14)
            s = pygame.Surface((cr*2, cr*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*C["success"], 22), (cr, cr), cr)
            surf.blit(s, (cx - cr, cy - cr))

        t1 = g.f_title.render("ИГРА ОКОНЧЕНА", True, C["text"])
        surf.blit(t1, (W // 2 - t1.get_width() // 2, int(H * 0.18)))

        sc_str = str(g.final_score)
        t2 = g.f_title.render(sc_str, True, C["accent"])
        ty2 = int(H * 0.34)
        surf.blit(t2, (W // 2 - t2.get_width() // 2, ty2))

        t3 = g.f_small.render("очков набрано", True, C["text_dim"])
        surf.blit(t3, (W // 2 - t3.get_width() // 2, ty2 + t2.get_height() + 6))

        if g.final_score >= g.best_score:
            rec = g.f_small.render("Новый рекорд!", True, C["warn"])
        else:
            rec = g.f_small.render(f"Рекорд: {g.best_score} очков", True, C["text_dim"])
        surf.blit(rec, (W // 2 - rec.get_width() // 2, int(H * 0.56)))

        self.btn_menu.draw(surf)
        self.btn_again.draw(surf)


# ──────────────────────────────────────────────────────────────
#  ГЛАВНЫЙ КЛАСС ИГРЫ
# ──────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.W = min(WIN_W, int(info.current_w * 0.92))
        self.H = min(WIN_H, int(info.current_h * 0.92))
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        pygame.display.set_caption("4 Фото 1 Слово")
        self.clock = pygame.time.Clock()

        self.best_score  = 0
        self.final_score = 0

        self._init_fonts()
        self._init_screens()
        self._switch("menu")

        self._prev_down = False

    # ── шрифты ──────────────────────────────────────────────
    def _init_fonts(self):
        def pick(names, size, bold=False):
            for n in names:
                if n is None:
                    return pygame.font.Font(None, size)
                try:
                    return pygame.font.SysFont(n, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.Font(None, size)

        H = self.H
        TITLE_NAMES  = ["Segoe UI Black", "DejaVu Sans Bold", "Arial Black", "Impact", None]
        BODY_NAMES   = ["Segoe UI", "DejaVu Sans", "Calibri", "Arial", None]

        self.f_title  = pick(TITLE_NAMES, int(H * 0.075), bold=True)
        self.f_btn    = pick(BODY_NAMES,  int(H * 0.033), bold=True)
        self.f_letter = pick(BODY_NAMES,  int(H * 0.038), bold=True)
        self.f_small  = pick(BODY_NAMES,  int(H * 0.027))
        self.f_tiny   = pick(BODY_NAMES,  int(H * 0.022))

    # ── экраны ──────────────────────────────────────────────
    def _init_screens(self):
        self.screens = {
            "menu": MenuScreen(self),
            "game": GameScreen(self),
            "end":  EndScreen(self),
        }

    def _switch(self, name):
        self._current_name = name
        self.current = self.screens[name]
        self.current.on_enter()

    def show_menu(self):
        self._switch("menu")

    def start_game(self):
        self._switch("game")

    def end_game(self, score):
        self.final_score = score
        self.best_score  = max(self.best_score, score)
        self._switch("end")

    # ── ресайз ──────────────────────────────────────────────
    def _on_resize(self, w, h):
        self.W, self.H = w, h
        self._init_fonts()
        self._init_screens()
        self._switch(self._current_name)

    # ── главный цикл ────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            mpos  = pygame.mouse.get_pos()
            mdown = pygame.mouse.get_pressed()[0]
            just  = mdown and not self._prev_down
            self._prev_down = mdown

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.VIDEORESIZE:
                    self._on_resize(e.w, e.h)
                self.current.handle_event(e)

            self.current.update(dt, mpos, just)
            self.current.draw(self.screen)
            pygame.display.flip()


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()
