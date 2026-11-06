import tkinter as tk
from tkinter import messagebox

BOARD_SIZE = 8
CELL_SIZE = 80
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE

COLOR_LIGHT = "#F0D9B5"
COLOR_DARK = "#B58863"
COLOR_RED = "#D9383A"
COLOR_BLACK = "#2B2B2B"
COLOR_HIGHLIGHT = "#769656"


class CheckersGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego de Damas - Control por Cursor")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WINDOW_SIZE, height=WINDOW_SIZE)
        self.canvas.pack()

        # Estado del tablero: 'r'/'R' (Rojas), 'b'/'B' (Negras), None (Vacío)
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = 'r'  # Inician las rojas

        # Control del arrastre con cursor
        self.selected_piece = None  # (r, c) de la pieza seleccionada
        self.dragged_item = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.init_board()
        self.draw_board()

        # Bindings de eventos del ratón
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def init_board(self):
        # Piezas negras en filas 0, 1, 2
        for r in range(3):
            for c in range(BOARD_SIZE):
                if (r + c) % 2 == 1:
                    self.board[r][c] = 'b'
        # Piezas rojas en filas 5, 6, 7
        for r in range(5, 8):
            for c in range(BOARD_SIZE):
                if (r + c) % 2 == 1:
                    self.board[r][c] = 'r'

    def draw_board(self):
        self.canvas.delete("all")

        # Dibujar casillas
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = COLOR_DARK if (r + c) % 2 == 1 else COLOR_LIGHT
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # Resaltar origen si hay una pieza seleccionada
        if self.selected_piece:
            sr, sc = self.selected_piece
            x1, y1 = sc * CELL_SIZE, sr * CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                                         fill=COLOR_HIGHLIGHT, outline="")

        # Dibujar piezas (excepto la que se está arrastrando en el momento)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.selected_piece == (r, c) and self.dragged_item:
                    continue
                piece = self.board[r][c]
                if piece:
                    self.draw_piece(r, c, piece)

    def draw_piece(self, r, c, piece):
        x = c * CELL_SIZE + CELL_SIZE // 2
        y = r * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 2 - 8
        color = COLOR_RED if piece.lower() == 'r' else COLOR_BLACK

        # Sombra/Borde de la pieza
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                fill=color, outline="white", width=2)

        # Corona si es Rey
        if piece.isupper():
            self.canvas.create_text(x, y, text="★", fill="gold", font=("Arial", 24, "bold"))

    def get_cell(self, x, y):
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return int(row), int(col)
        return None, None

    def is_valid_move(self, start_r, start_c, end_r, end_c):
        piece = self.board[start_r][start_c]
        if not piece:
            return False

        # Verificar turno
        if self.turn == 'r' and piece.lower() != 'r': return False
        if self.turn == 'b' and piece.lower() != 'b': return False

        # Casilla destino debe ser oscura y vacía
        if (end_r + end_c) % 2 == 0 or self.board[end_r][end_c] is not None:
            return False

        dr = end_r - start_r
        dc = end_c - start_c

        # Movimiento simple
        if abs(dr) == 1 and abs(dc) == 1:
            if piece == 'r' and dr > 0: return False
            if piece == 'b' and dr < 0: return False
            return True

        # Salto para capturar
        elif abs(dr) == 2 and abs(dc) == 2:
            mid_r = (start_r + end_r) // 2
            mid_c = (start_c + end_c) // 2
            target = self.board[mid_r][mid_c]

            if self.turn == 'r' and target and target.lower() == 'b':
                if piece == 'r' and dr > 0: return False
                return True
            if self.turn == 'b' and target and target.lower() == 'r':
                if piece == 'b' and dr < 0: return False
                return True

        return False

    def on_press(self, event):
        r, c = self.get_cell(event.x, event.y)
        if r is not None and self.board[r][c]:
            piece = self.board[r][c]
            # Validar que sea del jugador en turno
            if (self.turn == 'r' and piece.lower() == 'r') or (self.turn == 'b' and piece.lower() == 'b'):
                self.selected_piece = (r, c)
                self.draw_board()

                # Crear pieza temporal flotante para el movimiento con el cursor
                x = c * CELL_SIZE + CELL_SIZE // 2
                y = r * CELL_SIZE + CELL_SIZE // 2
                radius = CELL_SIZE // 2 - 8
                color = COLOR_RED if piece.lower() == 'r' else COLOR_BLACK

                self.dragged_item = self.canvas.create_oval(
                    event.x - radius, event.y - radius,
                    event.x + radius, event.y + radius,
                    fill=color, outline="yellow", width=3
                )
                if piece.isupper():
                    self.canvas.create_text(event.x, event.y, text="★", fill="gold",
                                            font=("Arial", 24, "bold"), tags="drag_star")

    def on_drag(self, event):
        if self.dragged_item:
            radius = CELL_SIZE // 2 - 8
            self.canvas.coords(self.dragged_item,
                               event.x - radius, event.y - radius,
                               event.x + radius, event.y + radius)
            self.canvas.coords("drag_star", event.x, event.y)

    def on_release(self, event):
        if not self.selected_piece:
            return

        start_r, start_c = self.selected_piece
        end_r, end_c = self.get_cell(event.x, event.y)

        # Limpiar pieza arrastrada
        self.canvas.delete(self.dragged_item)
        self.canvas.delete("drag_star")
        self.dragged_item = None

        if end_r is not None and self.is_valid_move(start_r, start_c, end_r, end_c):
            # Ejecutar movimiento
            piece = self.board[start_r][start_c]
            self.board[start_r][start_c] = None
            self.board[end_r][end_c] = piece

            # Si comió una pieza
            if abs(end_r - start_r) == 2:
                mid_r = (start_r + end_r) // 2
                mid_c = (start_c + end_c) // 2
                self.board[mid_r][mid_c] = None

            # Coronación
            if piece == 'r' and end_r == 0:
                self.board[end_r][end_c] = 'R'
            elif piece == 'b' and end_r == 7:
                self.board[end_r][end_c] = 'B'

            # Cambiar turno
            self.turn = 'b' if self.turn == 'r' else 'r'

        self.selected_piece = None
        self.draw_board()
        self.check_game_over()

    def check_game_over(self):
        r_count = sum(cell.lower() == 'r' for row in self.board for cell in row if cell)
        b_count = sum(cell.lower() == 'b' for row in self.board for cell in row if cell)

        if r_count == 0:
            messagebox.showinfo("Fin del juego", "¡Las piezas Negras ganan!")
            self.root.quit()
        elif b_count == 0:
            messagebox.showinfo("Fin del juego", "¡Las piezas Rojas ganan!")
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = CheckersGUI(root)
    root.mainloop()