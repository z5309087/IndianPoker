from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
import importlib.util
from poker_game import PokerGame  # Assuming poker_game.py contains your PokerGame class

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'algorithms/'

# Initialize the database
def init_db():
    with sqlite3.connect('leaderboard.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS leaderboard
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         algorithm_name TEXT NOT NULL,
                         wins INTEGER DEFAULT 0,
                         losses INTEGER DEFAULT 0,
                         chips INTEGER DEFAULT 0)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS algorithms
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         file_path TEXT NOT NULL)''')
    conn.close()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Upload algorithm
@app.route('/upload', methods=['GET', 'POST'])
def upload_algorithm():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.py'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Save the algorithm info to the database
            with sqlite3.connect('leaderboard.db') as conn:
                cur = conn.cursor()
                cur.execute('INSERT INTO algorithms (file_path) VALUES (?)', (file_path,))
                algo_id = cur.lastrowid
                cur.execute('INSERT INTO leaderboard (algorithm_name) VALUES (?)', (f"Algorithm {algo_id}",))
                conn.commit()

            # Run matches between the new algorithm and all others
            match_all_algorithms()

            # Redirect to the leaderboard page after upload
            return redirect(url_for('leaderboard'))

    return render_template('upload.html')

# Leaderboard page
@app.route('/leaderboard')
def leaderboard():
    with sqlite3.connect('leaderboard.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM leaderboard ORDER BY wins DESC, chips DESC')
        leaderboard_data = cur.fetchall()
    return render_template('leaderboard.html', leaderboard=leaderboard_data)

# Load and run the algorithms
def load_algorithm(file_path):
    spec = importlib.util.spec_from_file_location("module.name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PlayerAlgorithm

def run_match(algorithm1_path, algorithm2_path):
    Algorithm1 = load_algorithm(algorithm1_path)
    Algorithm2 = load_algorithm(algorithm2_path)

    player1 = Algorithm1(name="Player 1")
    player2 = Algorithm2(name="Player 2")

    game = PokerGame(player1_algorithm=player1, player2_algorithm=player2, starting_chips=100)
    game.play_game()

    winner_name = player1.name if player1.chips > player2.chips else player2.name
    return winner_name, player1.chips, player2.chips

def update_leaderboard(winner_name, player1_name, player2_name, player1_chips, player2_chips):
    with sqlite3.connect('leaderboard.db') as conn:
        if winner_name == player1_name:
            conn.execute('UPDATE leaderboard SET wins = wins + 1, chips = chips + ? WHERE algorithm_name = ?', (player1_chips, player1_name))
            conn.execute('UPDATE leaderboard SET losses = losses + 1, chips = chips - ? WHERE algorithm_name = ?', (player2_chips, player2_name))
        else:
            conn.execute('UPDATE leaderboard SET wins = wins + 1, chips = chips + ? WHERE algorithm_name = ?', (player2_chips, player2_name))
            conn.execute('UPDATE leaderboard SET losses = losses + 1, chips = chips - ? WHERE algorithm_name = ?', (player1_chips, player1_name))
        conn.commit()

def match_all_algorithms():
    with sqlite3.connect('leaderboard.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, file_path FROM algorithms')
        algorithms = cur.fetchall()

    for i in range(len(algorithms)):
        for j in range(i + 1, len(algorithms)):
            algo1_id, algo1_path = algorithms[i]
            algo2_id, algo2_path = algorithms[j]

            winner_name, player1_chips, player2_chips = run_match(algo1_path, algo2_path)

            update_leaderboard(winner_name, f"Algorithm {algo1_id}", f"Algorithm {algo2_id}", player1_chips, player2_chips)

# Run the application
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
