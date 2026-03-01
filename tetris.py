import random
import tkinter as tk
from tkinter import messagebox


CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
PREVIEW_SIZE = 4
DROP_INTERVAL_MS = 450


SHAPES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1], [1, 1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "J": [[1, 0, 0], [1, 1, 1]],
    "L": [[0, 0, 1], [1, 1, 1]],
}

COLORS = {
    "I": "#00D9FF",
    "O": "#FFE341",
    "T": "#B266FF",
    "S": "#62FF66",
    "Z": "#FF6666",
    "J": "#4D79FF",
    "L": "#FFB347",
}


class Tetris:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("俄罗斯方块 (Tkinter)")
        self.root.resizable(False, False)

        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_running = False
        self.after_id = None

        self.current_piece = None
        self.current_key = ""
        self.current_x = 0
        self.current_y = 0

        self.next_key = random.choice(list(SHAPES.keys()))

        self._build_ui()
        self._bind_keys()
        self.start_game()

    def _build_ui(self) -> None:
        wrapper = tk.Frame(self.root, padx=10, pady=10, bg="#1E1E1E")
        wrapper.pack()

        self.canvas = tk.Canvas(
            wrapper,
            width=BOARD_WIDTH * CELL_SIZE,
            height=BOARD_HEIGHT * CELL_SIZE,
            bg="#111111",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, rowspan=8, padx=(0, 12))

        side = tk.Frame(wrapper, bg="#1E1E1E")
        side.grid(row=0, column=1, sticky="n")

        title = tk.Label(side, text="俄罗斯方块", fg="white", bg="#1E1E1E", font=("Arial", 16, "bold"))
        title.pack(anchor="w")

        self.score_label = tk.Label(side, text="分数: 0", fg="white", bg="#1E1E1E", font=("Arial", 12))
        self.score_label.pack(anchor="w", pady=(12, 0))

        self.lines_label = tk.Label(side, text="消行: 0", fg="white", bg="#1E1E1E", font=("Arial", 12))
        self.lines_label.pack(anchor="w", pady=(4, 0))

        self.level_label = tk.Label(side, text="等级: 1", fg="white", bg="#1E1E1E", font=("Arial", 12))
        self.level_label.pack(anchor="w", pady=(4, 0))

        tk.Label(side, text="下一个:", fg="white", bg="#1E1E1E", font=("Arial", 12)).pack(anchor="w", pady=(16, 4))

        self.preview = tk.Canvas(
            side,
            width=PREVIEW_SIZE * CELL_SIZE,
            height=PREVIEW_SIZE * CELL_SIZE,
            bg="#111111",
            highlightthickness=0,
        )
        self.preview.pack(anchor="w")

        controls = (
            "操作说明:\n"
            "← → : 左右移动\n"
            "↑ : 旋转\n"
            "↓ : 加速下落\n"
            "空格 : 直接落地\n"
            "R : 重新开始"
        )
        tk.Label(side, text=controls, justify="left", fg="#CCCCCC", bg="#1E1E1E", font=("Arial", 10)).pack(anchor="w", pady=(16, 0))

        self.restart_btn = tk.Button(side, text="重新开始", command=self.start_game)
        self.restart_btn.pack(anchor="w", pady=(14, 0))

    def _bind_keys(self) -> None:
        self.root.bind("<Left>", lambda _: self.move(-1, 0))
        self.root.bind("<Right>", lambda _: self.move(1, 0))
        self.root.bind("<Down>", lambda _: self.move(0, 1))
        self.root.bind("<Up>", lambda _: self.rotate_piece())
        self.root.bind("<space>", lambda _: self.hard_drop())
        self.root.bind("r", lambda _: self.start_game())
        self.root.bind("R", lambda _: self.start_game())

    def start_game(self) -> None:
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_running = True

        self.next_key = random.choice(list(SHAPES.keys()))
        self.spawn_piece()
        self._refresh_labels()
        self.draw()
        self.tick()

    def spawn_piece(self) -> None:
        self.current_key = self.next_key
        self.current_piece = [row[:] for row in SHAPES[self.current_key]]
        self.current_x = (BOARD_WIDTH - len(self.current_piece[0])) // 2
        self.current_y = 0
        self.next_key = random.choice(list(SHAPES.keys()))

        if self._collides(self.current_piece, self.current_x, self.current_y):
            self.game_running = False
            self.draw()
            messagebox.showinfo("游戏结束", f"游戏结束！\n分数: {self.score}\n消行: {self.lines}")

    def _collides(self, piece, px: int, py: int) -> bool:
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if not cell:
                    continue
                bx = px + x
                by = py + y
                if bx < 0 or bx >= BOARD_WIDTH or by >= BOARD_HEIGHT:
                    return True
                if by >= 0 and self.board[by][bx] is not None:
                    return True
        return False

    def move(self, dx: int, dy: int) -> None:
        if not self.game_running:
            return
        nx = self.current_x + dx
        ny = self.current_y + dy
        if not self._collides(self.current_piece, nx, ny):
            self.current_x = nx
            self.current_y = ny
            self.draw()
        elif dy == 1:
            self.lock_piece()

    def rotate_piece(self) -> None:
        if not self.game_running:
            return
        rotated = [list(row) for row in zip(*self.current_piece[::-1])]
        for offset in (0, -1, 1, -2, 2):
            if not self._collides(rotated, self.current_x + offset, self.current_y):
                self.current_piece = rotated
                self.current_x += offset
                self.draw()
                return

    def hard_drop(self) -> None:
        if not self.game_running:
            return
        while not self._collides(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1
        self.lock_piece()

    def lock_piece(self) -> None:
        for y, row in enumerate(self.current_piece):
            for x, cell in enumerate(row):
                if cell:
                    by = self.current_y + y
                    bx = self.current_x + x
                    if 0 <= by < BOARD_HEIGHT and 0 <= bx < BOARD_WIDTH:
                        self.board[by][bx] = self.current_key

        cleared = self.clear_lines()
        if cleared:
            self.lines += cleared
            self.score += {1: 100, 2: 250, 3: 450, 4: 700}.get(cleared, 0) * self.level
            self.level = max(1, self.lines // 10 + 1)
            self._refresh_labels()

        self.spawn_piece()
        self.draw()

    def clear_lines(self) -> int:
        original_len = len(self.board)
        self.board = [row for row in self.board if any(cell is None for cell in row)]
        cleared = original_len - len(self.board)
        for _ in range(cleared):
            self.board.insert(0, [None for _ in range(BOARD_WIDTH)])
        return cleared

    def _refresh_labels(self) -> None:
        self.score_label.config(text=f"分数: {self.score}")
        self.lines_label.config(text=f"消行: {self.lines}")
        self.level_label.config(text=f"等级: {self.level}")

    def tick(self) -> None:
        if self.game_running:
            self.move(0, 1)
            speed = max(90, DROP_INTERVAL_MS - (self.level - 1) * 35)
            self.after_id = self.root.after(speed, self.tick)

    def draw(self) -> None:
        self.canvas.delete("all")

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                key = self.board[y][x]
                if key:
                    self._draw_cell(self.canvas, x, y, COLORS[key])

        if self.current_piece and self.game_running:
            color = COLORS[self.current_key]
            for y, row in enumerate(self.current_piece):
                for x, cell in enumerate(row):
                    if cell:
                        self._draw_cell(self.canvas, self.current_x + x, self.current_y + y, color)

        self._draw_grid()
        self._draw_preview()

    def _draw_grid(self) -> None:
        grid_color = "#222222"
        for x in range(BOARD_WIDTH + 1):
            px = x * CELL_SIZE
            self.canvas.create_line(px, 0, px, BOARD_HEIGHT * CELL_SIZE, fill=grid_color)
        for y in range(BOARD_HEIGHT + 1):
            py = y * CELL_SIZE
            self.canvas.create_line(0, py, BOARD_WIDTH * CELL_SIZE, py, fill=grid_color)

    def _draw_preview(self) -> None:
        self.preview.delete("all")
        piece = SHAPES[self.next_key]
        color = COLORS[self.next_key]

        width = len(piece[0])
        height = len(piece)
        offset_x = (PREVIEW_SIZE - width) * CELL_SIZE // 2
        offset_y = (PREVIEW_SIZE - height) * CELL_SIZE // 2

        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    self._draw_cell(self.preview, x, y, color, offset_x, offset_y)

    @staticmethod
    def _draw_cell(canvas: tk.Canvas, x: int, y: int, color: str, ox: int = 0, oy: int = 0) -> None:
        x1 = ox + x * CELL_SIZE
        y1 = oy + y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#101010")


def main() -> None:
    root = tk.Tk()
    Tetris(root)
    root.mainloop()


if __name__ == "__main__":
    main()
