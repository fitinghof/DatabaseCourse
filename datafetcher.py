import os
from dotenv import load_dotenv
from databasefuncs import DatabaseConnector, IDX_Type, ArtistRole

import psycopg2

host_name = "localhost"
user_name = "root"


def insert_animes(mysql: DatabaseConnector, postgres):
    psql = postgres.cursor()
    psql.execute("SELECT ann_id, eng_name, jpn_name, anilist_id FROM animes")

    animes = psql.fetchall()

    for ann_id, eng_name, jpn_name, anilist_id in animes:
        mysql.insert_anime(eng_name, jpn_name, None, anilist_id, ann_id)

    print(f"inserted {len(animes)} animes!")

    psql.close()


def insert_songs(mysql: DatabaseConnector, postgres):
    psql = postgres.cursor()
    psql.execute("SELECT id, name, artists, composers, arrangers FROM songs")

    songs = psql.fetchall()

    for id, name, artists, composers, arrangers in songs:
        mysql.insert_song(name, id)
        for artist in artists:
            mysql.bind_artist_song(id, artist, False, ArtistRole("artist"))
        for composer in composers:
            mysql.bind_artist_song(id, composer, False, ArtistRole("composer"))
        for arranger in arrangers:
            mysql.bind_artist_song(id, arranger, False, ArtistRole("arranger"))

    print(f"inserted {len(songs)} songs!")

    psql.close()


def insert_binds(mysql: DatabaseConnector, postgres):
    psql = postgres.cursor()
    psql.execute(
        "SELECT anime_ann_id, song_id, song_index_type, song_index_number, is_rebroadcast FROM anime_song_links"
    )

    binds = psql.fetchall()

    for anime, song, idx_type, idx_value, rebroadcast in binds:
        mysql.bind_anime_song_unchecked(
            anime, song, None, IDX_Type(idx_type), idx_value, False, rebroadcast
        )

    print(f"inserted {len(binds)} binds!")

    psql.close()


def insert_artists(mysql: DatabaseConnector, postgres):
    with postgres.cursor() as psql:
        psql.execute("SELECT id, names FROM artists")

        artists = psql.fetchall()

        for id, names in artists:
            mysql.insert_artist(names[0], id)

        print(f"inserted {len(artists)} artists!")


if __name__ == "__main__":
    load_dotenv()
    user_password = os.getenv("MYSQL_ROOT_PASSWORD")

    connector = DatabaseConnector(host_name, user_name, user_password, "test")

    postgrescon = psycopg2.connect(
        dbname="animedb_dev",
        user="animedb_dev",
        password=os.getenv("PG_PASS"),
        host="localhost",
    )

    if postgrescon is not None:
        print("Connected!")
        insert_artists(connector, postgrescon)
        insert_songs(connector, postgrescon)
        insert_animes(connector, postgrescon)
        insert_binds(connector, postgrescon)
        print("All data transfered!")

    connector.close()
