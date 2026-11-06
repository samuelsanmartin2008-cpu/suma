import streamlit as st

st.set_page_config(page_title="Juego de Damas", page_icon="🔴", layout="centered")

# Estilos CSS personalizados para simular un tablero de damas interactivo y bonito
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        height: 65px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 4px;
    }
    .board-container {
        max-width: 500px;
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar estado del juego
if "board" not in st.session_state:
    # 'r' = Roja, 'R' = Rey Rojo
    # 'b' = Negra, 'B' = Rey Negro
    # None = Casilla vacía
    board = [[None for _ in range(8)] for _ in range(8)]
    for r in range(3):
        for c in range(8):
            if (r + c) % 2 == 1:
                board[r][c] = 'b'
    for r in range(5, 8):
        for c in range(8):
            if (r + c) % 2 == 1:
                board[r][c] = 'r'
    st.session_state.board = board
    st.session_state.turn = 'r'  # 'r' empieza
    st.session_state.selected = None  # (fila, columna) de la pieza seleccionada
    st.session_state.message = "¡Partida iniciada! Mueven las Rojas (🔴)."


def reset_game():
    board = [[None for _ in range(8)] for _ in range(8)]
    for r in range(3):
        for c in range(8):
            if (r + c) % 2 == 1:
                board[r][c] = 'b'
    for r in range(5, 8):
        for c in range(8):
            if (r + c) % 2 == 1:
                board[r][c] = 'r'
    st.session_state.board = board
    st.session_state.turn = 'r'
    st.session_state.selected = None
    st.session_state.message = "¡Partida reiniciada! Mueven las Rojas (🔴)."


def is_valid_move(board, start, end, turn):
    sr, sc = start
    er, ec = end
    piece = board[sr][sc]

    if not piece:
        return False
    if turn == 'r' and piece.lower() != 'r': return False
    if turn == 'b' and piece.lower() != 'b': return False
    if (er + ec) % 2 == 0 or board[er][ec] is not None:
        return False

    dr = er - sr
    dc = ec - sc

    # Movimiento simple
    if abs(dr) == 1 and abs(dc) == 1:
        if piece == 'r' and dr > 0: return False
        if piece == 'b' and dr < 0: return False
        return True

    # Salto para capturar
    elif abs(dr) == 2 and abs(dc) == 2:
        mid_r = (sr + er) // 2
        mid_c = (sc + ec) // 2
        target = board[mid_r][mid_c]
        if turn == 'r' and target and target.lower() == 'b':
            if piece == 'r' and dr > 0: return False
            return True
        if turn == 'b' and target and target.lower() == 'r':
            if piece == 'b' and dr < 0: return False
            return True

    return False


st.title("🔴 Juego de Damas en Streamlit ⚪")
st.write("Haz clic en una de tus fichas para seleccionarla y luego haz clic en la casilla de destino.")

# Mostrar estado actual y botón de reinicio
col_info1, col_info2 = st.columns([3, 1])
with col_info1:
    turno_txt = "Rojas (🔴)" if st.session_state.turn == 'r' else "Negras (⚫)"
    st.info(f"**Turno actual:** {turno_txt}\n\n{st.session_state.message}")
with col_info2:
    if st.button("Reiniciar"):
        reset_game()
        st.rerun()

# Renderizar tablero 8x8 con botones de Streamlit
st.markdown('<div class="board-container">', unsafe_allow_html=True)
for r in range(8):
    cols = st.columns(8)
    for c in range(8):
        piece = st.session_state.board[r][c]
        is_selected = st.session_state.selected == (r, c)

        # Determinar etiqueta y color visual del botón
        if piece == 'r':
            label = "🔴"
        elif piece == 'R':
            label = "👑🔴"
        elif piece == 'b':
            label = "⚫"
        elif piece == 'B':
            label = "👑⚫"
        else:
            label = ""

        # Si está seleccionada, le ponemos un distintivo
        if is_selected:
            label = "📍" + label

        # Asignar colores de fondo según la celda (oscura o clara)
        is_dark = (r + c) % 2 == 1

        with cols[c]:
            if st.button(label if label else " ", key=f"btn_{r}_{c}"):
                if st.session_state.selected is None:
                    # Seleccionar pieza si pertenece al jugador en turno
                    if piece and ((st.session_state.turn == 'r' and piece.lower() == 'r') or
                                  (st.session_state.turn == 'b' and piece.lower() == 'b')):
                        st.session_state.selected = (r, c)
                        st.session_state.message = f"Pieza seleccionada en ({r}, {c}). Elige destino."
                        st.rerun()
                else:
                    sr, sc = st.session_state.selected
                    if (r, c) == (sr, sc):
                        # Deseleccionar si hace clic en la misma pieza
                        st.session_state.selected = None
                        st.session_state.message = "Selección cancelada."
                        st.rerun()
                    else:
                        # Intentar mover
                        if is_valid_move(st.session_state.board, (sr, sc), (r, c), st.session_state.turn):
                            # Ejecutar movimiento
                            p = st.session_state.board[sr][sc]
                            st.session_state.board[sr][sc] = None
                            st.session_state.board[r][c] = p

                            # Si fue salto, eliminar pieza capturada
                            if abs(r - sr) == 2:
                                mid_r = (sr + r) // 2
                                mid_c = (sc + c) // 2
                                st.session_state.board[mid_r][mid_c] = None

                            # Coronación
                            if p == 'r' and r == 0:
                                st.session_state.board[r][c] = 'R'
                            elif p == 'b' and r == 7:
                                st.session_state.board[r][c] = 'B'

                            # Cambiar turno
                            st.session_state.turn = 'b' if st.session_state.turn == 'r' else 'r'
                            st.session_state.selected = None
                            st.session_state.message = "Movimiento exitoso."
                            st.rerun()
                        else:
                            st.session_state.selected = None
                            st.session_state.message = "Movimiento inválido. Intenta de nuevo."
                            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Comprobar ganador
r_count = sum(cell.lower() == 'r' for row in st.session_state.board for cell in row if cell)
b_count = sum(cell.lower() == 'b' for row in st.session_state.board for cell in row if cell)

if r_count == 0:
    st.success("🎉 ¡Las fichas Negras (⚫) han ganado la partida!")
elif b_count == 0:
    st.success("🎉 ¡Las fichas Rojas (🔴) han ganado la partida!")