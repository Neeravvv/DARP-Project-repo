from difflib import SequenceMatcher
from pathlib import Path
import re
import unicodedata

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
SPOTIFY_EXPORT = PROJECT_DIR / "Spotify dataset export 2026-04-03 17-45-38.csv"
DONOR_FILES = [
    PROJECT_DIR / "top2018.csv",
    PROJECT_DIR / "top2019.csv",
    PROJECT_DIR / "top2020.csv",
    PROJECT_DIR / "top2021.csv",
    PROJECT_DIR / "top2022.csv",
    PROJECT_DIR / "top2023.csv",
]
OUTPUT_PATH = PROJECT_DIR / "top2024.csv"
REPORT_PATH = PROJECT_DIR / "top2024_match_report.csv"

OUTPUT_COLUMNS = [
    "title",
    "artist",
    "billboard_rank",
    "tempo_from_public_dataset",
    "danceability_from_public_dataset",
    "acousticness",
    "speechiness",
    "duration_minutes",
    "average_loudness",
    "dynamic_complexity",
    "danceable_probability",
    "happy_probability",
    "sad_probability",
    "relaxed_probability",
    "party_probability",
]

PUBLIC_FEATURE_COLUMNS = [
    "tempo_from_public_dataset",
    "danceability_from_public_dataset",
    "acousticness",
    "speechiness",
    "duration_minutes",
]

INFERRED_FEATURE_COLUMNS = [
    "average_loudness",
    "dynamic_complexity",
    "danceable_probability",
    "happy_probability",
    "sad_probability",
    "relaxed_probability",
    "party_probability",
]

IGNORE_ARTIST_TOKENS = {"the", "and", "with", "da", "dj", "mc"}

SONGS = [
    {"rank": 1, "title": "Lose Control", "artist": "Teddy Swims"},
    {"rank": 2, "title": "A Bar Song (Tipsy)", "artist": "Shaboozey"},
    {"rank": 3, "title": "Beautiful Things", "artist": "Benson Boone"},
    {"rank": 4, "title": "I Had Some Help", "artist": "Post Malone"},
    {"rank": 5, "title": "Lovin on Me", "artist": "Jack Harlow"},
    {"rank": 6, "title": "Not Like Us", "artist": "Kendrick Lamar"},
    {"rank": 7, "title": "Espresso", "artist": "Sabrina Carpenter"},
    {"rank": 8, "title": "Million Dollar Baby", "artist": "Tommy Richman"},
    {"rank": 9, "title": "I Remember Everything", "artist": "Zach Bryan"},
    {"rank": 10, "title": "Too Sweet", "artist": "Hozier"},
    {"rank": 11, "title": "Stick Season", "artist": "Noah Kahan"},
    {"rank": 12, "title": "Cruel Summer", "artist": "Taylor Swift"},
    {"rank": 13, "title": "Greedy", "artist": "Tate McRae"},
    {"rank": 14, "title": "Like That", "artist": "Future"},
    {"rank": 15, "title": "Birds of a Feather", "artist": "Billie Eilish"},
    {"rank": 16, "title": "Please Please Please", "artist": "Sabrina Carpenter"},
    {"rank": 17, "title": "Agora Hills", "artist": "Doja Cat"},
    {"rank": 18, "title": "Good Luck, Babe!", "artist": "Chappell Roan"},
    {"rank": 19, "title": "Saturn", "artist": "SZA"},
    {"rank": 20, "title": "Snooze", "artist": "SZA"},
    {"rank": 21, "title": "Paint the Town Red", "artist": "Doja Cat"},
    {"rank": 22, "title": "Fortnight", "artist": "Taylor Swift"},
    {"rank": 23, "title": "Fast Car", "artist": "Luke Combs"},
    {"rank": 24, "title": "Water", "artist": "Tyla"},
    {"rank": 25, "title": "Feather", "artist": "Sabrina Carpenter"},
    {"rank": 26, "title": "We Can't Be Friends (Wait for Your Love)", "artist": "Ariana Grande"},
    {"rank": 27, "title": "Austin", "artist": "Dasha"},
    {"rank": 28, "title": "Last Night", "artist": "Morgan Wallen"},
    {"rank": 29, "title": "Cowgirls", "artist": "Morgan Wallen"},
    {"rank": 30, "title": "Pink Skies", "artist": "Zach Bryan"},
    {"rank": 31, "title": "Thinkin' Bout Me", "artist": "Morgan Wallen"},
    {"rank": 32, "title": "Texas Hold 'Em", "artist": "Beyonce"},
    {"rank": 33, "title": "Is It Over Now?", "artist": "Taylor Swift"},
    {"rank": 34, "title": "Miles on It", "artist": "Marshmello"},
    {"rank": 35, "title": "I Can Do It with a Broken Heart", "artist": "Taylor Swift"},
    {"rank": 36, "title": "Wild Ones", "artist": "Jessie Murph"},
    {"rank": 37, "title": "Ain't No Love in Oklahoma", "artist": "Luke Combs"},
    {"rank": 38, "title": "Carnival", "artist": "Kanye West"},
    {"rank": 39, "title": "Houdini", "artist": "Eminem"},
    {"rank": 40, "title": "Wanna Be", "artist": "GloRilla"},
    {"rank": 41, "title": "Slow It Down", "artist": "Benson Boone"},
    {"rank": 42, "title": "Redrum", "artist": "21 Savage"},
    {"rank": 43, "title": "Houdini", "artist": "Dua Lipa"},
    {"rank": 44, "title": "Yeah Glo!", "artist": "GloRilla"},
    {"rank": 45, "title": "Rich Baby Daddy", "artist": "Drake"},
    {"rank": 46, "title": "What Was I Made For?", "artist": "Billie Eilish"},
    {"rank": 47, "title": "End of Beginning", "artist": "Djo"},
    {"rank": 48, "title": "Lunch", "artist": "Billie Eilish"},
    {"rank": 49, "title": "Never Lose Me", "artist": "Flo Milli"},
    {"rank": 50, "title": "Lies Lies Lies", "artist": "Morgan Wallen"},
    {"rank": 51, "title": "Type Shit", "artist": "Future"},
    {"rank": 52, "title": "Gata Only", "artist": "FloyyMenor"},
    {"rank": 53, "title": "Hot to Go!", "artist": "Chappell Roan"},
    {"rank": 54, "title": "All I Want for Christmas Is You", "artist": "Mariah Carey"},
    {"rank": 55, "title": "Get It Sexyy", "artist": "Sexyy Red"},
    {"rank": 56, "title": "Made for Me", "artist": "Muni Long"},
    {"rank": 57, "title": "Vampire", "artist": "Olivia Rodrigo"},
    {"rank": 58, "title": "Whatever She Wants", "artist": "Bryson Tiller"},
    {"rank": 59, "title": "Rockin' Around the Christmas Tree", "artist": "Brenda Lee"},
    {"rank": 60, "title": "Pretty Little Poison", "artist": "Warren Zeiders"},
    {"rank": 61, "title": "First Person Shooter", "artist": "Drake"},
    {"rank": 62, "title": "Die with a Smile", "artist": "Lady Gaga"},
    {"rank": 63, "title": "I Like the Way You Kiss Me", "artist": "Artemas"},
    {"rank": 64, "title": "Need a Favor", "artist": "Jelly Roll"},
    {"rank": 65, "title": "Save Me", "artist": "Jelly Roll"},
    {"rank": 66, "title": "Euphoria", "artist": "Kendrick Lamar"},
    {"rank": 67, "title": "Truck Bed", "artist": "Hardy"},
    {"rank": 68, "title": "Jingle Bell Rock", "artist": "Bobby Helms"},
    {"rank": 69, "title": "Flowers", "artist": "Miley Cyrus"},
    {"rank": 70, "title": "Where the Wild Things Are", "artist": "Luke Combs"},
    {"rank": 71, "title": "Everybody", "artist": "Nicki Minaj"},
    {"rank": 72, "title": "La Diabla", "artist": "Xavi"},
    {"rank": 73, "title": "Stargazing", "artist": "Myles Smith"},
    {"rank": 74, "title": "Last Christmas", "artist": "Wham!"},
    {"rank": 75, "title": "I Am Not Okay", "artist": "Jelly Roll"},
    {"rank": 76, "title": "Pour Me a Drink", "artist": "Post Malone"},
    {"rank": 77, "title": "White Horse", "artist": "Chris Stapleton"},
    {"rank": 78, "title": "Lil Boo Thang", "artist": "Paul Russell"},
    {"rank": 79, "title": "Good Good", "artist": "Usher"},
    {"rank": 80, "title": "Act II: Date @ 8", "artist": "4Batz"},
    {"rank": 81, "title": "High Road", "artist": "Koe Wetzel"},
    {"rank": 82, "title": "Monaco", "artist": "Bad Bunny"},
    {"rank": 83, "title": "IDGAF", "artist": "Drake"},
    {"rank": 84, "title": "Burn It Down", "artist": "Parker McCollum"},
    {"rank": 85, "title": "FukUMean", "artist": "Gunna"},
    {"rank": 86, "title": "Taste", "artist": "Sabrina Carpenter"},
    {"rank": 87, "title": "Where It Ends", "artist": "Bailey Zimmerman"},
    {"rank": 88, "title": "FTCU", "artist": "Nicki Minaj"},
    {"rank": 89, "title": "Wildflower", "artist": "Billie Eilish"},
    {"rank": 90, "title": "World on Fire", "artist": "Nate Smith"},
    {"rank": 91, "title": "On My Mama", "artist": "Victoria Monet"},
    {"rank": 92, "title": "Yes, And?", "artist": "Ariana Grande"},
    {"rank": 93, "title": "Exes", "artist": "Tate McRae"},
    {"rank": 94, "title": "A Holly Jolly Christmas", "artist": "Burl Ives"},
    {"rank": 95, "title": "Wind Up Missin' You", "artist": "Tucker Wetmore"},
    {"rank": 96, "title": "Bulletproof", "artist": "Nate Smith"},
    {"rank": 97, "title": "Fe!n", "artist": "Travis Scott"},
    {"rank": 98, "title": "The Painter", "artist": "Cody Johnson"},
    {"rank": 99, "title": "Down Bad", "artist": "Taylor Swift"},
    {"rank": 100, "title": "Dance the Night", "artist": "Dua Lipa"},
]


def normalize_text(value):
    text = "" if pd.isna(value) else str(value)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"\(feat[^)]*\)", "", text)
    text = re.sub(r"\[feat[^\]]*\]", "", text)
    text = re.sub(r"feat\.?.*", "", text)
    text = re.sub(r"ft\.?.*", "", text)
    text = re.sub(r"featuring.*", "", text)
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def artist_similarity(song_artist, dataset_artist):
    song_norm = normalize_text(song_artist)
    data_norm = normalize_text(dataset_artist)
    if not song_norm or not data_norm:
        return 0.0
    song_tokens = set(song_norm.split())
    data_tokens = set(data_norm.split())
    token_overlap = len(song_tokens & data_tokens) / len(song_tokens) if song_tokens else 0.0
    sequence_score = SequenceMatcher(None, song_norm, data_norm).ratio()
    return max(token_overlap, sequence_score)


def title_similarity(left, right):
    return SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def title_match_details(song_title, candidate_title, candidate_display_title):
    song_norm = normalize_text(song_title)
    candidate_norm = normalize_text(candidate_title)
    display_norm = normalize_text(candidate_display_title)
    similarity = max(
        SequenceMatcher(None, song_norm, candidate_norm).ratio(),
        SequenceMatcher(None, song_norm, display_norm).ratio(),
    )
    contains_match = (
        song_norm in candidate_norm
        or candidate_norm in song_norm
        or song_norm in display_norm
        or display_norm in song_norm
    )
    return similarity, contains_match


def prepare_spotify_source():
    prepared = pd.read_csv(SPOTIFY_EXPORT)
    prepared["normalized_artist"] = prepared["Artist"].map(normalize_text)

    artist_token_index = {}
    for index, normalized_artist in prepared["normalized_artist"].items():
        for token in normalized_artist.split():
            if token not in IGNORE_ARTIST_TOKENS:
                artist_token_index.setdefault(token, set()).add(index)
    return prepared, artist_token_index


def candidate_indexes_for_artist(song_artist, artist_token_index, prepared):
    artist_tokens = [
        token
        for token in normalize_text(song_artist).split()
        if token not in IGNORE_ARTIST_TOKENS
    ]
    candidate_indexes = set()
    for token in artist_tokens:
        candidate_indexes |= artist_token_index.get(token, set())
    if candidate_indexes:
        return list(candidate_indexes)
    return prepared.index.tolist()


def select_best_match(song, prepared, artist_token_index):
    candidate_indexes = candidate_indexes_for_artist(song["artist"], artist_token_index, prepared)
    candidates = prepared.loc[candidate_indexes].copy()

    title_scores = candidates.apply(
        lambda row: title_match_details(song["title"], row["Track"], row["Title"]),
        axis=1,
        result_type="expand",
    )
    title_scores.columns = ["title_match_score", "title_contains_match"]
    candidates = candidates.join(title_scores)
    candidates["artist_match_score"] = candidates["Artist"].map(
        lambda value: artist_similarity(song["artist"], value)
    )

    candidates = candidates[
        (candidates["artist_match_score"] >= 0.34)
        | ((candidates["artist_match_score"] >= 0.20) & (candidates["title_contains_match"]))
    ]
    if candidates.empty:
        return None

    candidates["combined_match_score"] = (
        candidates["title_match_score"] * 0.72
        + candidates["artist_match_score"] * 0.28
        + candidates["title_contains_match"].astype(float) * 0.12
    )
    candidates = candidates[
        (candidates["combined_match_score"] >= 0.72)
        | (candidates["title_contains_match"] & (candidates["artist_match_score"] >= 0.34))
    ]
    if candidates.empty:
        return None

    candidates = candidates.sort_values(
        by=["combined_match_score", "artist_match_score", "Tempo"],
        ascending=[False, False, False],
    )
    return candidates.iloc[0]


def load_donors():
    donor_frames = [pd.read_csv(path) for path in DONOR_FILES]
    donors = pd.concat(donor_frames, ignore_index=True)
    donors = donors[OUTPUT_COLUMNS].copy()
    return donors.dropna()


def infer_missing_features(result, donors):
    scales = donors[PUBLIC_FEATURE_COLUMNS].std().replace(0, 1).fillna(1)

    for idx, row in result.iterrows():
        distances = (((donors[PUBLIC_FEATURE_COLUMNS] - row[PUBLIC_FEATURE_COLUMNS]) / scales) ** 2).sum(axis=1) ** 0.5
        nearest = donors.loc[distances.idxmin()]
        for column in INFERRED_FEATURE_COLUMNS:
            result.at[idx, column] = nearest[column]
        result.at[idx, "nearest_neighbor_source"] = f"{nearest['title']} - {nearest['artist']}"

    return result


def build_unmatched_rows(unmatched_songs, donor_pool):
    rows = []
    for song in unmatched_songs:
        candidates = donor_pool.copy()
        candidates["artist_similarity"] = candidates["artist"].map(
            lambda value: artist_similarity(song["artist"], value)
        )
        candidates["title_similarity"] = candidates["title"].map(
            lambda value: title_similarity(song["title"], value)
        )
        candidates["rank_similarity"] = candidates["billboard_rank"].map(
            lambda value: max(0.0, 1.0 - abs(float(value) - float(song["rank"])) / 100.0)
        )
        candidates["donor_score"] = (
            candidates["artist_similarity"] * 0.55
            + candidates["title_similarity"] * 0.15
            + candidates["rank_similarity"] * 0.30
        )
        best = candidates.sort_values(
            by=["donor_score", "artist_similarity", "rank_similarity"],
            ascending=[False, False, False],
        ).iloc[0]

        rows.append(
            {
                "title": song["title"],
                "artist": song["artist"],
                "billboard_rank": song["rank"],
                "tempo_from_public_dataset": best["tempo_from_public_dataset"],
                "danceability_from_public_dataset": best["danceability_from_public_dataset"],
                "acousticness": best["acousticness"],
                "speechiness": best["speechiness"],
                "duration_minutes": best["duration_minutes"],
                "average_loudness": best["average_loudness"],
                "dynamic_complexity": best["dynamic_complexity"],
                "danceable_probability": best["danceable_probability"],
                "happy_probability": best["happy_probability"],
                "sad_probability": best["sad_probability"],
                "relaxed_probability": best["relaxed_probability"],
                "party_probability": best["party_probability"],
                "matched_spotify_artist": "",
                "matched_spotify_track": "",
                "artist_match_score": "",
                "title_match_score": "",
                "combined_match_score": "",
                "nearest_neighbor_source": f"{best['title']} - {best['artist']}",
                "row_source": "inferred_from_donor",
            }
        )
    return rows


def build_dataset():
    prepared, artist_token_index = prepare_spotify_source()

    matched_rows = []
    unmatched_songs = []

    for song in SONGS:
        match = select_best_match(song, prepared, artist_token_index)
        if match is None:
            unmatched_songs.append(song)
            continue

        matched_rows.append(
            {
                "title": song["title"],
                "artist": song["artist"],
                "billboard_rank": song["rank"],
                "tempo_from_public_dataset": pd.to_numeric(match["Tempo"], errors="coerce"),
                "danceability_from_public_dataset": pd.to_numeric(match["Danceability"], errors="coerce"),
                "acousticness": pd.to_numeric(match["Acousticness"], errors="coerce"),
                "speechiness": pd.to_numeric(match["Speechiness"], errors="coerce"),
                "duration_minutes": pd.to_numeric(match["Duration_min"], errors="coerce"),
                "average_loudness": None,
                "dynamic_complexity": None,
                "danceable_probability": None,
                "happy_probability": None,
                "sad_probability": None,
                "relaxed_probability": None,
                "party_probability": None,
                "matched_spotify_artist": match["Artist"],
                "matched_spotify_track": match["Track"],
                "artist_match_score": match["artist_match_score"],
                "title_match_score": match["title_match_score"],
                "combined_match_score": match["combined_match_score"],
                "nearest_neighbor_source": "",
                "row_source": "spotify_match_plus_donor_features",
            }
        )

    result = pd.DataFrame(matched_rows).sort_values("billboard_rank").reset_index(drop=True)
    donors = load_donors()
    result = infer_missing_features(result, donors)

    if unmatched_songs:
        donor_pool = pd.concat([result[OUTPUT_COLUMNS], donors], ignore_index=True)
        inferred_rows = pd.DataFrame(build_unmatched_rows(unmatched_songs, donor_pool))
        result = pd.concat([result, inferred_rows], ignore_index=True, sort=False)
        result = result.sort_values("billboard_rank").reset_index(drop=True)

    if int(result[OUTPUT_COLUMNS].isna().sum().sum()) != 0:
        raise ValueError("Output dataset still contains missing values.")

    report = result[
        [
            "billboard_rank",
            "title",
            "artist",
            "matched_spotify_artist",
            "matched_spotify_track",
            "artist_match_score",
            "title_match_score",
            "combined_match_score",
            "nearest_neighbor_source",
            "row_source",
        ]
    ].copy()

    result[OUTPUT_COLUMNS].to_csv(OUTPUT_PATH, index=False)
    report.to_csv(REPORT_PATH, index=False)

    print(f"Direct Spotify matches: {len(matched_rows)}")
    print(f"Donor-inferred songs: {len(unmatched_songs)}")
    print(f"Total songs: {len(result)}")
    print(f"Dataset saved to: {OUTPUT_PATH}")
    print(f"Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    build_dataset()
