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
    PROJECT_DIR / "top2024.csv",
]
OUTPUT_PATH = PROJECT_DIR / "top2025.csv"
REPORT_PATH = PROJECT_DIR / "top2025_match_report.csv"

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
    {"rank": 1, "title": "Die with a Smile", "artist": "Lady Gaga"},
    {"rank": 2, "title": "Luther", "artist": "Kendrick Lamar"},
    {"rank": 3, "title": "A Bar Song (Tipsy)", "artist": "Shaboozey"},
    {"rank": 4, "title": "Lose Control", "artist": "Teddy Swims"},
    {"rank": 5, "title": "Birds of a Feather", "artist": "Billie Eilish"},
    {"rank": 6, "title": "Beautiful Things", "artist": "Benson Boone"},
    {"rank": 7, "title": "Ordinary", "artist": "Alex Warren"},
    {"rank": 8, "title": "I Had Some Help", "artist": "Post Malone"},
    {"rank": 9, "title": "APT.", "artist": "Rose"},
    {"rank": 10, "title": "Pink Pony Club", "artist": "Chappell Roan"},
    {"rank": 11, "title": "Love Somebody", "artist": "Morgan Wallen"},
    {"rank": 12, "title": "Espresso", "artist": "Sabrina Carpenter"},
    {"rank": 13, "title": "I'm the Problem", "artist": "Morgan Wallen"},
    {"rank": 14, "title": "That's So True", "artist": "Gracie Abrams"},
    {"rank": 15, "title": "TV Off", "artist": "Kendrick Lamar"},
    {"rank": 16, "title": "Timeless", "artist": "The Weeknd"},
    {"rank": 17, "title": "Not Like Us", "artist": "Kendrick Lamar"},
    {"rank": 18, "title": "Just in Case", "artist": "Morgan Wallen"},
    {"rank": 19, "title": "Taste", "artist": "Sabrina Carpenter"},
    {"rank": 20, "title": "Squabble Up", "artist": "Kendrick Lamar"},
    {"rank": 21, "title": "30 for 30", "artist": "SZA"},
    {"rank": 22, "title": "Mutt", "artist": "Leon Thomas"},
    {"rank": 23, "title": "Good News", "artist": "Shaboozey"},
    {"rank": 24, "title": "Nokia", "artist": "Drake"},
    {"rank": 25, "title": "Golden", "artist": "Huntrix"},
    {"rank": 26, "title": "Wildflower", "artist": "Billie Eilish"},
    {"rank": 27, "title": "What I Want", "artist": "Morgan Wallen"},
    {"rank": 28, "title": "Messy", "artist": "Lola Young"},
    {"rank": 29, "title": "Stargazing", "artist": "Myles Smith"},
    {"rank": 30, "title": "Love Me Not", "artist": "Ravyn Lenae"},
    {"rank": 31, "title": "Good Luck, Babe!", "artist": "Chappell Roan"},
    {"rank": 32, "title": "No One Noticed", "artist": "The Marias"},
    {"rank": 33, "title": "All the Way", "artist": "BigXthaPlug"},
    {"rank": 34, "title": "Too Sweet", "artist": "Hozier"},
    {"rank": 35, "title": "Worst Way", "artist": "Riley Green"},
    {"rank": 36, "title": "Sailor Song", "artist": "Gigi Perez"},
    {"rank": 37, "title": "Sorry I'm Here for Someone Else", "artist": "Benson Boone"},
    {"rank": 38, "title": "Manchild", "artist": "Sabrina Carpenter"},
    {"rank": 39, "title": "Anxiety", "artist": "Doechii"},
    {"rank": 40, "title": "I Got Better", "artist": "Morgan Wallen"},
    {"rank": 41, "title": "Sticky", "artist": "Tyler, the Creator"},
    {"rank": 42, "title": "Undressed", "artist": "Sombr"},
    {"rank": 43, "title": "I Never Lie", "artist": "Zach Top"},
    {"rank": 44, "title": "Back to Friends", "artist": "Sombr"},
    {"rank": 45, "title": "Bed Chem", "artist": "Sabrina Carpenter"},
    {"rank": 46, "title": "Sports Car", "artist": "Tate McRae"},
    {"rank": 47, "title": "Mystical Magical", "artist": "Benson Boone"},
    {"rank": 48, "title": "Whatchu Kno About Me", "artist": "GloRilla"},
    {"rank": 49, "title": "Indigo", "artist": "Sam Barber"},
    {"rank": 50, "title": "Please Please Please", "artist": "Sabrina Carpenter"},
    {"rank": 51, "title": "DTMF", "artist": "Bad Bunny"},
    {"rank": 52, "title": "Blue Strips", "artist": "Jessie Murph"},
    {"rank": 53, "title": "Peekaboo", "artist": "Kendrick Lamar"},
    {"rank": 54, "title": "Your Idol", "artist": "Saja Boys"},
    {"rank": 55, "title": "High Road", "artist": "Koe Wetzel"},
    {"rank": 56, "title": "Abracadabra", "artist": "Lady Gaga"},
    {"rank": 57, "title": "Who", "artist": "Jimin"},
    {"rank": 58, "title": "Burning Blue", "artist": "Mariah the Scientist"},
    {"rank": 59, "title": "All I Want for Christmas Is You", "artist": "Mariah Carey"},
    {"rank": 60, "title": "Daisies", "artist": "Justin Bieber"},
    {"rank": 61, "title": "Soda Pop", "artist": "Saja Boys"},
    {"rank": 62, "title": "Like Him", "artist": "Tyler, the Creator"},
    {"rank": 63, "title": "Residuals", "artist": "Chris Brown"},
    {"rank": 64, "title": "Smile", "artist": "Morgan Wallen"},
    {"rank": 65, "title": "Last Christmas", "artist": "Wham!"},
    {"rank": 66, "title": "Am I Okay?", "artist": "Megan Moroney"},
    {"rank": 67, "title": "Rockin' Around the Christmas Tree", "artist": "Brenda Lee"},
    {"rank": 68, "title": "How It's Done", "artist": "Huntrix"},
    {"rank": 69, "title": "Happen to Me", "artist": "Russell Dickerson"},
    {"rank": 70, "title": "Baile Inolvidable", "artist": "Bad Bunny"},
    {"rank": 71, "title": "Weren't for the Wind", "artist": "Ella Langley"},
    {"rank": 72, "title": "I Ain't Comin' Back", "artist": "Morgan Wallen"},
    {"rank": 73, "title": "Cry for Me", "artist": "The Weeknd"},
    {"rank": 74, "title": "Bad Dreams", "artist": "Teddy Swims"},
    {"rank": 75, "title": "Denial Is a River", "artist": "Doechii"},
    {"rank": 76, "title": "BMF", "artist": "SZA"},
    {"rank": 77, "title": "Eoo", "artist": "Bad Bunny"},
    {"rank": 78, "title": "I'm Gonna Love You", "artist": "Cody Johnson"},
    {"rank": 79, "title": "I Am Not Okay", "artist": "Jelly Roll"},
    {"rank": 80, "title": "Backup Plan", "artist": "Bailey Zimmerman"},
    {"rank": 81, "title": "Jingle Bell Rock", "artist": "Bobby Helms"},
    {"rank": 82, "title": "Revolving Door", "artist": "Tate McRae"},
    {"rank": 83, "title": "What It Sounds Like", "artist": "Huntrix"},
    {"rank": 84, "title": "Hard Fought Hallelujah", "artist": "Brandon Lake"},
    {"rank": 85, "title": "Somebody Loves Me", "artist": "PartyNextDoor"},
    {"rank": 86, "title": "Liar", "artist": "Jelly Roll"},
    {"rank": 87, "title": "Tu Boda", "artist": "Oscar Maydon"},
    {"rank": 88, "title": "After All the Bars Are Closed", "artist": "Thomas Rhett"},
    {"rank": 89, "title": "Nuevayol", "artist": "Bad Bunny"},
    {"rank": 90, "title": "20 Cigarettes", "artist": "Morgan Wallen"},
    {"rank": 91, "title": "Rather Lie", "artist": "Playboi Carti"},
    {"rank": 92, "title": "Free", "artist": "Ejae"},
    {"rank": 93, "title": "Takedown", "artist": "Huntrix"},
    {"rank": 94, "title": "Heart of a Woman", "artist": "Summer Walker"},
    {"rank": 95, "title": "House Again", "artist": "Hudson Westbrook"},
    {"rank": 96, "title": "Dark Thoughts", "artist": "Lil Tecca"},
    {"rank": 97, "title": "No Pole", "artist": "Don Toliver"},
    {"rank": 98, "title": "Folded", "artist": "Kehlani"},
    {"rank": 99, "title": "Superman", "artist": "Morgan Wallen"},
    {"rank": 100, "title": "Loco", "artist": "Neton Vega"},
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
