import mysql.connector
from mysql.connector import Error
from enum import Enum
import json


class ArtistRole(Enum):
    COMPOSER = "composer"
    ARTIST = "artist"
    ARRANGER = "arranger"


class IDX_Type(Enum):
    OP = "opening"
    ED = "ending"
    IN = "insert"


class DatabaseConnector:
    def __init__(self, host_name, user_name, user_password, db):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=host_name, user=user_name, passwd=user_password, database=db
            )
            print("Connection to MySQL DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

    def close(self):
        self.connection.commit()
        # self.connection.rollback()
        self.connection.close()

    def search_anisongs(self, name: str) -> list:
        if self.connection is not None:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM anisong_view WHERE anime_name_eng LIKE %s or song_name LIKE %s",
                (f"%{name}%", f"%{name}%"),
            )

            results = cursor.fetchall()
            cursor.close()
            return results
        return []

    def search_songs(self, song_name: str) -> list:
        if self.connection is not None:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT s.*, jSON_ARRAYAGG(JSON_OBJECT('id', a.id, 'name', a.artist_name, 'role', sa.artist_role)) AS artists "
                "FROM songs s "
                "INNER JOIN song_artist_links sa ON s.id = sa.song "
                "INNER JOIN artists a ON sa.artist = a.id "
                "WHERE s.song_name LIKE %s "
                "GROUP BY s.id "
                "ORDER BY s.song_name ",
                (f"%{song_name}%",),
            )

            results = cursor.fetchall()
            for line in results:
                line["artists"] = json.loads(line["artists"])
            cursor.close()

            return results
        return []

    def insert_song(
        self,
        name: str | None,
        id: int | None,
    ):
        if self.connection is not None:
            with self.connection.cursor() as cursor:
                if id is not None:
                    cursor.execute(
                        "INSERT INTO songs (song_name, id) VALUES (%s, %s)",
                        (name, id),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO songs (song_name) VALUES (%s)",
                        (name,),
                    )

    def insert_anime(
        self,
        name_eng: str | None,
        name_jpn_romaji: str | None,
        name_jpn: str | None,
        anilist_id: int | None,
        id: int | None,
    ):
        if self.connection is not None:
            with self.connection.cursor() as cursor:
                if id is not None:
                    cursor.execute(
                        "INSERT INTO animes (name_eng, name_jpn, name_jpn_romaji, anilist_id, id) VALUES (%s, %s, %s, %s, %s)",
                        (name_eng, name_jpn, name_jpn_romaji, anilist_id, id),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO animes (name_eng, name_jpn_romaji, name_jpn, anilist_id) VALUES (%s, %s, %s, %s)",
                        (name_eng, name_jpn, name_jpn_romaji, anilist_id),
                    )

    def bind_anime_song_unchecked(
        self,
        anime: int,
        song: int,
        user: int | None,
        idx_type: IDX_Type,
        idx_value: int,
        confirmed: bool,
        rebroadcast: bool,
    ):
        if self.connection is not None:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO anime_song_links (idx_type, idx_value, confirmed, rebroadcast, anime, song, user_bind) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        idx_type.value,
                        idx_value,
                        confirmed,
                        rebroadcast,
                        anime,
                        song,
                        user,
                    ),
                )

    def bind_anime_song(
        self,
        anime: int,
        song: int,
        user: int,
        idx_type: IDX_Type,
        idx_value: int,
        confirmed: bool,
        rebroadcast: bool,
    ):
        if self.connection is not None:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "CALL bind_anime_song(@%s, @%s, @%s, @%s, @%s, @%s, @%s)",
                    (
                        anime,
                        song,
                        user,
                        idx_type.value,
                        idx_value,
                        confirmed,
                        rebroadcast,
                    ),
                )

    def insert_artist(self, name: str, id: int | None):
        with self.connection.cursor() as cursor:
            if id is not None:
                cursor.execute(
                    "INSERT INTO artists (artist_name, id) VALUES (%s, %s)",
                    (name, id),
                )
            else:
                cursor.execute(
                    "INSERT INTO artists (artist_name) VALUES (%s)",
                    (name,),
                )

    def insert_user(self, username, permissions):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (display_name, permissions) VALUES (%s, %s)",
                (username, permissions),
            )

    def get_user(self, username):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,),
            )



    def bind_artist_song(
        self, song: int, artist: int, confirmed, artist_role: ArtistRole
    ):
        if self.connection is not None:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO song_artist_links (song, artist, confirmed, artist_role) "
                    "VALUES (%s, %s, %s, %s)",
                    (song, artist, confirmed, artist_role.value),
                )

    def search_artists(self, name: str) -> list:
        if self.connection is not None:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM artists WHERE artist_name LIKE %s",
                (f"%{name}%",),
            )
            results = cursor.fetchall()
            cursor.close()
            return results
        return []

    def search_animes(self, name: str) -> list:
        if self.connection is not None:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM animes WHERE name_eng LIKE %s OR name_jpn_romaji LIKE %s OR name_jpn LIKE %s",
                (f"%{name}%", f"%{name}%", f"%{name}%"),
            )
            results = cursor.fetchall()
            cursor.close()
            return results
        return []

    def get_all_artists(self) -> list:
        if self.connection is not None:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT id, artist_name FROM artists ORDER BY artist_name")
            results = cursor.fetchall()
            cursor.close()
            return results
        return []

    def get_all_animes(self) -> list:
        if self.connection is not None:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, name_eng, name_jpn_romaji FROM animes ORDER BY name_eng"
            )
            results = cursor.fetchall()
            cursor.close()
            return results
        return []

    def get_all_songs(self) -> list:
        if self.connection is not None:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT id, song_name FROM songs ORDER BY song_name")
            results = cursor.fetchall()
            cursor.close()
            return results
        return []
