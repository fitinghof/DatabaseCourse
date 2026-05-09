-- Anime table
-- Song table
-- Artists
-- spotify links, apple music links etc. (Both to artists and songs)
-- users
-- Anime - song link (+ index in anime)
-- Anisong view
-- Anime - anime site links (Anilist, MyAnimeList, AniDB etc, tmdb?, tvdb?) (confirmed field?)


-- Internal tables
CREATE TABLE IF NOT EXISTS animes (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    anilist_id INTEGER,
    name_eng VARCHAR(256),
    name_jpn_romaji VARCHAR(256),
    name_jpn VARCHAR(256)
);


CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    song_name VARCHAR(256)
);


CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    artist_name VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    display_name VARCHAR(256) NOT NULL,
    permissions INTEGER NOT NULL,
    CONSTRAINT unique_name UNIQUE (display_name)
);

-- Internal links
CREATE TABLE IF NOT EXISTS anime_song_links (
    -- PRIMARY KEY as either anime + song or seperate id
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    idx_type ENUM('opening', 'insert', 'ending') NOT NULL,
    idx_value INTEGER NOT NULL,
    confirmed BOOLEAN NOT NULL,
    rebroadcast BOOLEAN NOT NULL,
    anime INTEGER NOT NULL,
    song INTEGER NOT NULL,
    user_bind INTEGER,
    FOREIGN KEY (anime) REFERENCES animes(id),
    FOREIGN KEY (song) REFERENCES songs(id),
    FOREIGN KEY (user_bind) REFERENCES users(id),
    CONSTRAINT valid UNIQUE (idx_type, idx_value, rebroadcast, anime, song)
);

CREATE TABLE IF NOT EXISTS song_artist_links (
    -- PRIMARY KEY as either artist + song or seperate id
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    song INTEGER NOT NULL,
    artist INTEGER NOT NULL,
    confirmed BOOLEAN NOT NULL,
    -- allowing multiple song / artist binds of same song / artist
    -- would allow an artist to be connected to a song with different roles
    artist_role ENUM('composer', 'artist', 'arranger') NOT NULL, 
    FOREIGN KEY (song) REFERENCES songs(id),
    FOREIGN KEY (artist) REFERENCES artists(id),
    CONSTRAINT valid UNIQUE (song, artist, artist_role)
);


-- external links
CREATE TABLE IF NOT EXISTS spotify_artist_links (
    spotify VARCHAR(256) NOT NULL,
    artist INTEGER NOT NULL,
    FOREIGN KEY (artist) REFERENCES artists(id)
);

CREATE TABLE IF NOT EXISTS spotify_song_links (
    spotify VARCHAR(256) NOT NULL,
    song INTEGER NOT NULL,
    FOREIGN KEY (song) REFERENCES songs(id)
);

-- Views
CREATE VIEW anisong_view AS 
    SELECT
        a.id as anime_id,
        a.name_eng as anime_name_eng,
        a.name_jpn as anime_name_jpn,
        a.name_jpn_romaji as anime_name_jpn_romaji,

        s.id as song_id,
        s.song_name as song_name,

        asl.id as anisong_id,
        asl.idx_type as idx_type,
        asl.idx_value as idx_value,
        asl.confirmed as confirmed_link,
        asl.rebroadcast as rebroadcast
    FROM
        anime_song_links asl
        INNER JOIN songs s ON asl.song = s.id
        INNER JOIN animes a ON asl.anime = a.id
;

-- bind procedure, checks permissons and adds binds
DELIMITER ##
CREATE PROCEDURE bind_anime_song (
    IN anime INTEGER,
    IN song INTEGER,
    IN p_user_id INTEGER,
    IN idx_type ENUM('opening', 'insert', 'ending'),
    IN idx_value INTEGER,
    IN confirmed BOOLEAN,
    IN rebroadcast BOOLEAN
    )
BEGIN
    DECLARE user_permissions INTEGER DEFAULT 0;
    DECLARE valid BOOLEAN DEFAULT FALSE;
    SELECT permissions INTO user_permissions FROM users WHERE id = p_user_id;
    SELECT has_permission(user_permissions, 'bind_anime_song') INTO valid;
    IF valid THEN 
        INSERT INTO anime_song_links (anime, song, user_bind, idx_type, idx_value, confirmed, rebroadcast) 
        VALUES (anime, song, p_user_id, idx_type, idx_value, confirmed, rebroadcast);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User was not allowed to execute this query';
    END IF;
END ##

DELIMITER ;


DELIMITER ##
CREATE PROCEDURE bind_artist (
    IN artist INTEGER,
    IN song INTEGER,
    IN p_user_id INTEGER,
    IN confirmed BOOLEAN,
    IN artist_role ENUM('composer', 'artist', 'arranger')
    )
BEGIN
    DECLARE user_permissions INTEGER DEFAULT 0;
    DECLARE valid BOOLEAN DEFAULT FALSE;
    SELECT permissions INTO user_permissions FROM users WHERE id = p_user_id;
    SELECT has_permission(user_permissions, 'bind_artist') INTO valid;
    IF valid THEN 
        INSERT INTO song_artist_links (artist, song, confirmed, artist_role) 
        VALUES (artist, song, confirmed, artist_role);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'User was not allowed to execute this query';
    END IF;
END ##

DELIMITER ;
-- permission parser function, could be used in procedure?

DELIMITER ##

CREATE FUNCTION has_permission (
    permission_int INTEGER, 
    permission ENUM('admin', 'bind_anime_song', 'bind_artist')
) 
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    RETURN (permission_int & 
        CASE permission
            WHEN 'admin' THEN 1
            WHEN 'bind_anime_song' THEN 2
            WHEN 'bind_artist' THEN 4
            ELSE 0
        END
    ) != 0;
END ##

DELIMITER ;


