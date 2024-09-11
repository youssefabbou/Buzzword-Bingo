# Importieren der erforderlichen Module und Bibliotheken
import os  # Betriebssystem-Schnittstellenfunktionen
import curses  # Terminal-Steuerung für die Erstellung von Text-Benutzeroberflächen
import multiprocessing  # Unterstützung für parallele Ausführung und Prozesse
import logging  # Protokollierung von Ereignissen, Fehlern und anderen Informationen
from curses import textpad  # Zusätzliche Zeichenfunktionen für Curses
from datetime import datetime  # Datum- und Uhrzeitfunktionen
import uuid  # Erzeugung eindeutiger Bezeichner
import random  # Zufallszahlen- und Auswahlfunktionen
import posix_ipc  # Interprozesskommunikation für POSIX-kompatible Systeme
import time  # Zeitfunktionen

# Einrichten der Protokollierung
logging.basicConfig(filename='bingo_game.log', level=logging.INFO, format='%(asctime)s - %(message)s', filemode='a')

# Definition der BingoCard-Klasse
class BingoCard:
    def __init__(self, rows, cols, words=None, card=None):
        self.rows = rows  # Anzahl der Zeilen der Bingo-Karte
        self.cols = cols  # Anzahl der Spalten der Bingo-Karte
        if card:
            self.card = card  # Verwendet eine bestehende Karte
        else:
            self.card = self.create_card(words)  # Erstellt eine neue Karte mit den angegebenen Wörtern
        self.original_card = [row[:] for row in self.card]  # Speichert eine Kopie der ursprünglichen Karte
        self.mark_middle_as_joker()  # Markiert das mittlere Feld als Joker, falls zutreffend

    def create_card(self, words):
        card = []
        chosen_words = random.sample(words, self.rows * self.cols)  # Zufällige Auswahl der Wörter
        index = 0
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(chosen_words[index])
                index += 1
            card.append(row)
        return card

    def mark_middle_as_joker(self):
        if self.rows == self.cols and self.rows % 2 == 1 and self.rows in [5, 7]:  # Prüft, ob die Karte 5x5 oder 7x7 ist
            middle = self.rows // 2
            self.card[middle][middle] = "Joker"
            self.original_card[middle][middle] = "Joker"

    def check_bingo(self):
        for row in self.card:
            if all(cell == 'X' or cell == 'Joker' for cell in row):  # Überprüft vollständige Zeile
                return True

        for col in range(self.cols):
            if all(self.card[row][col] == 'X' or self.card[row][col] == 'Joker' for row in range(self.rows)):  # Überprüft vollständige Spalte
                return True

        if all(self.card[i][i] == 'X' or self.card[i][i] == 'Joker' for i in range(min(self.rows, self.cols))):  # Überprüft Diagonale von oben links nach unten rechts
            return True

        if all(self.card[i][self.cols - i - 1] == 'X' or self.card[i][self.cols - i - 1] == 'Joker' for i in range(min(self.rows, self.cols))):  # Überprüft Diagonale von oben rechts nach unten links
            return True

        return False

    def mark(self, row, col):
        if self.card[row][col] != 'Joker':
            self.card[row][col] = 'X'  # Markiert ein Feld mit 'X'

    def unmark(self, row, col):
        if self.card[row][col] == 'X':
            self.card[row][col] = self.original_card[row][col]  # Entfernt die Markierung von einem Feld

    def __str__(self):
        card_str = ""
        for row in self.card:
            card_str += " | ".join(f"{cell:5}" for cell in row) + "\n"  # Formatiert die Karte als String
        return card_str

# Zeichnet die Bingo-Karte im Terminal
def draw_card(stdscr, card, marked, field_width, field_height, color_pair, game_won, winner=None):
    stdscr.clear()  # Bildschirm löschen
    max_y, max_x = stdscr.getmaxyx()  # Maximale Abmessungen des Bildschirms
    for i, row in enumerate(card):
        for j, word in enumerate(row):
            x1, y1 = 2 + j * (field_width + 1), 2 + i * (field_height + 1)
            x2, y2 = x1 + field_width, y1 + field_height
            if y2 >= max_y or x2 >= max_x:
                continue
            textpad.rectangle(stdscr, y1, x1, y2, x2)  # Zeichnet ein Rechteck
            if (i, j) in marked:
                stdscr.addstr(y1 + (field_height // 2), x1 + 1, "X".center(field_width - 1), curses.A_REVERSE | color_pair)
            else:
                stdscr.addstr(y1 + (field_height // 2), x1 + 1, word[:field_width - 1].center(field_width - 1), color_pair)
    if game_won:
        win_message = f"Player {winner} won!" if winner else "You won!"
        stdscr.addstr(max_y - 4, 2, win_message.center(max_x - 4), curses.A_BOLD | color_pair)
    stdscr.addstr(max_y - 2, 2, "Press 'x' to exit the game", curses.A_BOLD | color_pair)
    stdscr.refresh()

# Liest Wörter aus einer Datei ein
def read_words_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [word.strip() for line in file for word in line.split(',') if word.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {filename} was not found.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

# Speichert die Bingo-Karte in einer Datei
def save_bingo_card(game_id, card, player):
    filename = f"bingo_{game_id}_{player}.txt"
    with open(filename, "w", encoding='utf-8') as file:
        for row in card:
            file.write(",".join(row) + "\n")

# Lädt die Bingo-Karte aus einer Datei
def load_bingo_card(game_id, player):
    filename = f"bingo_{game_id}_{player}.txt"
    with open(filename, "r", encoding='utf-8') as file:
        return [line.split(',') for line in file.read().split('\n') if line]

# Formatiert die Bingo-Karte als String
def format_bingo_card(card):
    formatted_card = []
    for row in card:
        formatted_card.append(','.join(row))
    return '\n'.join(formatted_card)

# Parsen einer Bingo-Karte aus einem String
def parse_bingo_card(card_str):
    return [line.split(',') for line in card_str.strip().split('\n')]

# Erstellt eine Nachrichtenwarteschlange
def create_message_queue(name, max_message_size=1024):
    try:
        mq = posix_ipc.MessageQueue(name, flags=posix_ipc.O_CREAT, mode=0o666, max_message_size=max_message_size)
        return mq
    except Exception as e:
        logging.error(f"Error creating message queue: {e}")
        return None

# Sendet eine Nachricht an die Warteschlange
def send_message(mq, message):
    try:
        mq.send(message.encode())
        logging.debug(f"Message sent successfully: {message}")
    except posix_ipc.BusyError as e:
        logging.error(f"Message queue is full or busy: {e}")
    except posix_ipc.ExistentialError as e:
        logging.error(f"Message queue does not exist: {e}")
    except posix_ipc.PermissionError as e:
        logging.error(f"Permission error while sending message: {e}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

# Empfängt eine Nachricht aus der Warteschlange
def receive_message(mq, message_size=1024):
    try:
        message, _ = mq.receive(message_size)
        logging.debug(f"Message received: {message.decode()}")
        return message.decode()
    except Exception as e:
        logging.error(f"Error receiving message: {e}")
        return None

# Bereinigt die Nachrichtenwarteschlange
def cleanup_message_queue(mq, name):
    try:
        mq.close()
        mq.unlink()
    except Exception as e:
        logging.error(f"Error cleaning up message queue: {e}")

# Prozess, der Nachrichten in die Warteschlange schreibt
def write_to_queue(message_queue, queue, color_pair, stdscr, max_y, win_event):
    while not win_event.is_set():
        row, col = queue.get()
        if row is None and col is None:
            break
        try:
            stdscr.addstr(1, 2, f"Marked: {row},{col}", curses.A_BOLD | color_pair)
            logging.info(f"Marked: {row},{col}")
        except Exception as e:
            stdscr.addstr(max_y - 3, 2, f"Error writing to queue: {e}", curses.A_BOLD | color_pair)
            stdscr.refresh()

# Prozess, der Nachrichten aus der Warteschlange liest
def read_from_queue(message_queue, game, marked, draw_card, stdscr, field_width, field_height, color_pair, win_event):
    while not win_event.is_set():
        try:
            message = receive_message(message_queue)
            if message and message.startswith("Player"):
                winner = message.split()[1]
                win_event.set()
                stdscr.addstr(1, 2, "Win message received", curses.A_BOLD | color_pair)
                draw_card(stdscr, game.card, marked, field_width, field_height, color_pair, True, winner=winner)
                logging.info(f"Win message received: {message}")
                stdscr.refresh()
                time.sleep(2)  # Warten Sie 2 Sekunden, bevor das Spiel endet
                break
        except Exception as e:
            stdscr.addstr(3, 2, f"Error reading from queue: {e}", curses.A_BOLD | color_pair)
            stdscr.refresh()

# Hauptspielschleife
def main_game_loop(stdscr, rows, cols, game, marked, message_queues, queue, color_pair, yellow_blue, win_event, player):
    max_y, max_x = stdscr.getmaxyx()  # Maximale Abmessungen des Bildschirms
    field_width = 10  # Anpassung der Feldbreite für 7x7 Raster
    field_height = 1  # Anpassung der Feldhöhe für 7x7 Raster

    while not win_event.is_set():
        key = stdscr.getch()
        if key == ord('x'):
            queue.put((None, None))
            logging.info("Game exited")
            win_event.set()
            break
        if key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            col = (mx - 2) // (field_width + 1)
            row = (my - 2) // (field_height + 1)
            if 0 <= row < rows and 0 <= col < cols:
                if (row, col) in marked:
                    marked.remove((row, col))
                    game.unmark(row, col)
                else:
                    marked.add((row, col))
                    game.mark(row, col)
                draw_card(stdscr, game.card, marked, field_width, field_height, color_pair, False)

                queue.put((row, col))

                if game.check_bingo():
                    stdscr.addstr(2 + rows * (field_height + 1), 2, f"Player {player} won!".center((field_width + 1) * cols), yellow_blue)
                    stdscr.addstr(3, 2, "Win message sent", curses.A_BOLD | color_pair)
                    stdscr.refresh()
                    for mq in message_queues:
                        send_message(mq, f"Player {player} won!")
                        stdscr.addstr(4, 2, "Win message sent", curses.A_BOLD | color_pair)
                    logging.info(f"Player {player} won!")
                    win_event.set()
                    break

# Spieler tritt einem bestehenden Spiel bei
def join_game(game_id):
    try:
        rows, cols, words = load_round_file(game_id)
    except FileNotFoundError as e:
        logging.error(e)
        return

    card = [words[i * cols:(i + 1) * cols] for i in range(rows)]

    player_id = str(uuid.uuid4())[:8]
    send_queue_name = f"/bingo_queue_{game_id}player{player_id}_send"
    receive_queue_name = f"/bingo_queue_{game_id}player{player_id}_receive"

    logging.info(f"Player {player_id} joined")

    game_info = load_game_info(game_id)
    game_info['players'].append(player_id)
    game_info['receive_queues'].append(receive_queue_name)
    save_game_info(game_id, game_info)

    curses.wrapper(main, rows, cols, card, send_queue_name, game_info['receive_queues'], game_id, f"{game_id}_round.txt", player_id)

# Hauptfunktion des Spiels
def main(stdscr, rows, cols, card, send_queue_name, receive_queue_names, game_id, round_filename, player):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    color_pair = curses.color_pair(1)
    yellow_blue = curses.color_pair(2)

    game = BingoCard(rows, cols, card=card)
    marked = set()
    win_event = multiprocessing.Event()

    if rows == cols and rows % 2 == 1 and rows in [5, 7]:  # Markiert das mittlere Feld als Joker, falls zutreffend
        middle = rows // 2
        marked.add((middle, middle))

    field_width = 10  # Anpassung der Feldbreite für 7x7 Raster
    field_height = 1  # Anpassung der Feldhöhe für 7x7 Raster

    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    draw_card(stdscr, game.card, marked, field_width, field_height, color_pair, False)

    queue = multiprocessing.Queue()
    max_y, max_x = stdscr.getmaxyx()

    send_queue = create_message_queue(send_queue_name)
    receive_queues = [create_message_queue(name) for name in receive_queue_names]

    write_process = multiprocessing.Process(target=write_to_queue, args=(send_queue, queue, color_pair, stdscr, max_y, win_event))
    read_processes = [
        multiprocessing.Process(target=read_from_queue, args=(receive_queue, game, marked, draw_card, stdscr, field_width, field_height, color_pair, win_event))
        for receive_queue in receive_queues
    ]
    game_process = multiprocessing.Process(target=main_game_loop, args=(stdscr, rows, cols, game, marked, receive_queues, queue, color_pair, yellow_blue, win_event, player))

    write_process.start()
    for read_process in read_processes:
        read_process.start()
    game_process.start()

    logging.info("Game started")
    game_process.join()
    write_process.join()
    for read_process in read_processes:
        read_process.join()

    end_time = datetime.now()
    logging.info(f"Game ended at: {end_time}")

    with open(round_filename, 'a', encoding='utf-8') as round_file:
        round_file.write(f"End time: {end_time}\n")
        round_file.write("Marked coordinates:\n")
        for mark in marked:
            round_file.write(f"{mark}\n")

    cleanup_message_queue(send_queue, send_queue_name)
    for receive_queue in receive_queues:
        cleanup_message_queue(receive_queue, receive_queue.name)

# Lädt Spielinformationen aus einer Datei
def load_game_info(game_id):
    filename = f"game_info_{game_id}.txt"
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        receive_queues = [line.strip() for line in lines[1:]]
        return {'receive_queues': receive_queues, 'players': [receive_queue.split('_')[-2] for receive_queue in receive_queues]}

# Speichert Spielinformationen in einer Datei
def save_game_info(game_id, game_info):
    filename = f"game_info_{game_id}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"{len(game_info['players'])}\n")
        for player_id in game_info['players']:
            receive_queue_name = f"/bingo_queue_{game_id}player{player_id}_receive"
            file.write(f"{receive_queue_name}\n")

# Lädt eine Runde aus einer Datei
def load_round_file(game_id):
    for filename in os.listdir('.'):
        if filename.endswith(f"-bingo-{game_id}.txt"):
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                rows = int(lines[0].split(': ')[1])
                cols = int(lines[1].split(': ')[1])
                wordfile = lines[3].split(': ')[1].strip()
                words = read_words_from_file(wordfile)
                return rows, cols, words
    raise FileNotFoundError(f"No round file found for game ID {game_id}")

# Erstellt eine neue Runden-Datei
def create_round_file(game_id, rows, cols, users, wordfile, start_time):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{timestamp}-bingo-{game_id}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"Height: {rows}\n")
        file.write(f"Width: {cols}\n")
        file.write(f"Users: {users}\n")
        file.write(f"Wordfile: {wordfile}\n")
        file.write(f"Start time: {start_time}\n")
    logging.info(f"Round file created: {filename}")
    return filename

# Startet ein neues Spiel
def start_game():
    game_id = str(uuid.uuid4())[:8]
    print(f"Game ID: {game_id}")

    rows = int(input("Please enter the number of rows for the Bingo card : "))
    cols = int(input("Please enter the number of columns for the Bingo card : "))
    wordfile = input("Please enter the path to the file with the buzzwords: ")

    buzzwords = read_words_from_file(wordfile)

    if len(buzzwords) < rows * cols:
        print(f"Not enough words ({len(buzzwords)}) for a {rows}x{cols} Bingo card.")
        return

    users = 2
    start_time = datetime.now()
    round_filename = create_round_file(game_id, rows, cols, users, wordfile, start_time)

    server_game = BingoCard(rows, cols, words=buzzwords)
    save_bingo_card(game_id, server_game.card, "server")

    client_game = BingoCard(rows, cols, words=buzzwords)
    save_bingo_card(game_id, client_game.card, "client")

    game_info = {'receive_queues': [], 'players': []}
    save_game_info(game_id, game_info)

    print(f"Game ID: {game_id}")
    print("Waiting for players to join...")

    player_joined = multiprocessing.Event()
    join_check_process = multiprocessing.Process(target=check_player_join, args=(game_id, player_joined))
    join_check_process.start()

    # Warten, bis mindestens ein Spieler beitritt
    player_joined.wait()

    join_check_process.terminate()
    join_check_process.join()

    game_info = load_game_info(game_id)  # Aktualisierte Spielinformationen neu laden
    curses.wrapper(main, rows, cols, load_bingo_card(game_id, "server"), f"/bingo_queue_{game_id}_player_server_send", game_info['receive_queues'], game_id, round_filename, "server")

# Überprüft, ob ein Spieler dem Spiel beitritt
def check_player_join(game_id, player_joined):
    while not player_joined.is_set():
        game_info = load_game_info(game_id)
        if len(game_info['players']) > 0:
            player_joined.set()
        time.sleep(1)

# Fügt Protokolleinträge in die Runden-Datei ein
def insert_log_entries_in_file(log_filename, round_filename):
    with open(log_filename, 'r') as log_file:
        log_data = log_file.read()
    with open(round_filename, 'a', encoding='utf-8') as round_file:
        round_file.write('\n' + log_data)

# Ruft die Hauptfunktion auf
if __name__ == "__main__":
    mode = input("Enter 's' to start a game or 'j' to join a game: ")
    if mode == 's':
        start_game()
    elif mode == 'j':
        game_id = input("Please enter the game ID to join: ")
        join_game(game_id)
    else:
        print("Invalid mode selected.")
