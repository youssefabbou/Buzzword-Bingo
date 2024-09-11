Buzzword-Bingo-Spiel

## Übersicht

Dies ist ein **multiplayer-fähiges Bingo-Spiel** für das Terminal, implementiert in Python. Es verwendet `curses` zur Erstellung einer textbasierten Benutzeroberfläche und `multiprocessing` zur parallelen Ausführung von Prozessen. Das Spiel unterstützt **mehrere Spieler** und ermöglicht eine **Echtzeit-Interaktion** durch **POSIX-Nachrichtenwarteschlangen** zur Kommunikation zwischen Prozessen.

## Funktionen

- **Mehrspieler-Modus**: Mehrere Spieler können gleichzeitig am Bingo-Spiel teilnehmen.
- **Textbasierte Benutzeroberfläche**: Das Spiel verwendet das `curses`-Modul, um eine interaktive Oberfläche im Terminal bereitzustellen.
- **Echtzeit-Interaktion**: Mit Hilfe von POSIX-Nachrichtenwarteschlangen können die Spieler in Echtzeit miteinander interagieren.
- **Zufällige Bingo-Karten**: Die Bingo-Karten werden aus einer Liste von Wörtern zufällig generiert.
- **Joker-Funktion**: Die Mitte der Karte wird automatisch als Joker markiert (bei 5x5 oder 7x7 Karten).
- **Protokollierung**: Das Spiel protokolliert alle wichtigen Ereignisse und Fehler in einer Logdatei.

## Voraussetzungen

- Python 3.x
- Installierte Bibliotheken: 
  - `curses`
  - `multiprocessing`
  - `posix_ipc`

Du kannst die Bibliotheken über `pip` installieren:
```
pip install posix_ipc
```

## Installation

1. **Klonen oder Herunterladen des Repositories**:
   ```
   git clone <repository-url>
   cd <repository-ordner>
   ```

2. **Spiel starten**:
   Du kannst entweder ein neues Spiel starten oder einem bestehenden Spiel beitreten.

   Um ein neues Spiel zu starten:
   ```
   python bingo.py
   ```

   Wähle beim Start die Option `s`, um ein neues Spiel zu erstellen, oder `j`, um einem bestehenden Spiel beizutreten.

## Spielanleitung

### Neues Spiel starten:

1. Gib die Anzahl der Zeilen und Spalten für die Bingo-Karte ein (z.B. 5 für ein 5x5 Gitter).
2. Wähle eine Datei aus, die die zu verwendenden Wörter enthält (z.B. `words.txt`).
3. Das Spiel generiert eine Bingo-Karte und startet die Runde.

### Spiel beitreten:

1. Gib die Game-ID ein, die vom Spielleiter bereitgestellt wird.
2. Sobald du dem Spiel beigetreten bist, wird dir eine Bingo-Karte zugewiesen.

### Spielablauf:

- Die Spieler markieren Felder auf ihrer Bingo-Karte durch Auswahl der entsprechenden Positionen. Wenn eine vollständige Zeile, Spalte oder Diagonale markiert ist, gewinnt der Spieler.
- Verwende die Maus oder die Pfeiltasten, um ein Feld zu markieren.
- Um das Spiel zu beenden, drücke `x`.

## Dateien

- **bingo.py**: Hauptskript zum Starten des Spiels.
- **bingo_game.log**: Protokolldatei, in der alle wichtigen Ereignisse und Fehler aufgezeichnet werden.
- **words.txt**: Datei, die eine Liste von Wörtern enthält, die für die Bingo-Karten verwendet werden.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
