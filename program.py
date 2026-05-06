import os
from dotenv import load_dotenv
from databasefuncs import DatabaseConnector, IDX_Type, ArtistRole
from flask import Flask, request, render_template, jsonify

load_dotenv()

app = Flask(__name__)
host_name = "localhost"
user_name = "root"
user_password = os.getenv("MYSQL_ROOT_PASSWORD")
connector = DatabaseConnector(host_name, user_name, user_password, "test")


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# Search endpoints
@app.route("/api/search/anisong", methods=["POST"])
def search_anisong():
    try:
        data = request.get_json()
        search_query = data.get("search", "")
        results = connector.search_anisongs(search_query)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/search/songs", methods=["POST"])
def search_songs():
    try:
        data = request.get_json()
        search_query = data.get("search", "")
        results = connector.search_songs(search_query)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/search/artists", methods=["POST"])
def search_artists():
    try:
        data = request.get_json()
        search_query = data.get("search", "")
        results = connector.search_artists(search_query)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/search/animes", methods=["POST"])
def search_animes():
    try:
        data = request.get_json()
        search_query = data.get("search", "")
        results = connector.search_animes(search_query)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# Get all data endpoints (for dropdowns)
@app.route("/api/artists", methods=["GET"])
def get_artists():
    try:
        results = connector.get_all_artists()
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/animes", methods=["GET"])
def get_animes():
    try:
        results = connector.get_all_animes()
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/songs", methods=["GET"])
def get_songs():
    try:
        results = connector.get_all_songs()
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# Add endpoints
@app.route("/api/add/song", methods=["POST"])
def add_song():
    try:
        data = request.get_json()
        name = data.get("name")

        if not name:
            return jsonify({"success": False, "error": "Song name is required"}), 400

        connector.insert_song(name, None)
        return jsonify({"success": True, "message": "Song added successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/add/anime", methods=["POST"])
def add_anime():
    try:
        data = request.get_json()
        name_eng = data.get("name_eng")
        name_jpn_romaji = data.get("name_jpn_romaji")
        name_jpn = data.get("name_jpn")
        anilist_id = data.get("anilist_id")
        anime_id = data.get("id")

        if not name_eng:
            return jsonify({"success": False, "error": "English name is required"}), 400

        connector.insert_anime(
            name_eng, name_jpn_romaji, name_jpn, anilist_id, anime_id
        )
        return jsonify({"success": True, "message": "Anime added successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/add/artist", methods=["POST"])
def add_artist():
    try:
        data = request.get_json()
        name = data.get("name")
        artist_id = data.get("id")

        if not name:
            return jsonify({"success": False, "error": "Artist name is required"}), 400

        connector.insert_artist(name, artist_id)
        return jsonify({"success": True, "message": "Artist added successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# Bind endpoints
@app.route("/api/bind/animeSong", methods=["POST"])
def bind_anime_song():
    try:
        data = request.get_json()
        anime = data.get("anime_id")
        song = data.get("song_id")
        idx_type = data.get("idx_type")
        idx_value = data.get("idx_value")
        rebroadcast = data.get("rebroadcast", False)
        user = data.get("user")

        if not all([anime, song, idx_type, idx_value is not None]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        connector.bind_anime_song(
            anime, song, user, IDX_Type(idx_type), int(idx_value), False, rebroadcast
        )
        return jsonify(
            {"success": True, "message": "Anime-Song binding added successfully"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/bind/artistSong", methods=["POST"])
def bind_artist_song():
    try:
        data = request.get_json()
        song = data.get("song_id")
        artist = data.get("artist_id")
        artist_role = data.get("artist_role")
        user = data.get("user")

        if not all([song, artist, artist_role]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        connector.bind_artist_song(song, artist, False, ArtistRole(artist_role))
        return jsonify(
            {"success": True, "message": "Artist-Song binding added successfully"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
    connector.close()
