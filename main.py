from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_NAME = "pokedex.db"

# --- INIT DB ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Table principale Pokemon
    c.execute('''CREATE TABLE IF NOT EXISTS pokemon (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    state INTEGER DEFAULT 0
                )''')
    # Table des badges (1-n avec Pokemon)
    c.execute('''CREATE TABLE IF NOT EXISTS pokemon_badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pokemon_id INTEGER,
                    badge INTEGER,
                    FOREIGN KEY (pokemon_id) REFERENCES pokemon(id)
                )''')
    conn.commit()
    conn.close()


# --- UTILS ---
def get_pokemon_with_badges():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM pokemon")
    pokemons = c.fetchall()

    results = []
    for p in pokemons:
        p_id, name, state = p
        c.execute("SELECT badge FROM pokemon_badges WHERE pokemon_id=?", (p_id,))
        badges = [row[0] for row in c.fetchall()]
        results.append({
            "id": p_id,
            "name": name,
            "state": bool(state),
            "badges": badges
        })
    conn.close()
    return results


# --- ROUTES ---
@app.route("/pokedex", methods=["GET"])
def get_pokedex():
    return jsonify(get_pokemon_with_badges())


@app.route("/pokemon/<int:pokemon_id>/state", methods=["POST"])
def set_pokemon_state(pokemon_id):
    data = request.get_json()
    state = data.get("state", False)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE pokemon SET state=? WHERE id=?", (int(state), pokemon_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "pokemon_id": pokemon_id, "state": state})


@app.route("/pokemon/<int:pokemon_id>/badges", methods=["POST"])
def set_pokemon_badges(pokemon_id):
    data = request.get_json()
    badges = data.get("badges", [])

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Supprimer les anciens badges
    c.execute("DELETE FROM pokemon_badges WHERE pokemon_id=?", (pokemon_id,))
    # Ajouter les nouveaux
    for badge in badges:
        c.execute("INSERT INTO pokemon_badges (pokemon_id, badge) VALUES (?, ?)", (pokemon_id, badge))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "pokemon_id": pokemon_id, "badges": badges})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
