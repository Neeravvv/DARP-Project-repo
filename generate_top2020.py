from difflib import SequenceMatcher
from pathlib import Path
import re
import unicodedata

import pandas as pd


PROJECT_DIR = Path(r"C:\Users\NEERAV\OneDrive\Desktop\DARP\Project")
SPOTIFY_EXPORT = PROJECT_DIR / "Spotify dataset export 2026-04-03 17-45-38.csv"
DONOR_FILES = [
    PROJECT_DIR / "top2018.csv",
    PROJECT_DIR / "top2019.csv",
]
OUTPUT_PATH = Path(__file__).with_name("top2020.csv")
REPORT_PATH = Path(__file__).with_name("top2020_match_report.csv")

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
    {"rank": 1, "title": "Blinding Lights", "artist": "The Weeknd"},
    {"rank": 2, "title": "Circles", "artist": "Post Malone"},
    {"rank": 3, "title": "The Box", "artist": "Roddy Ricch"},
    {"rank": 4, "title": "Don't Start Now", "artist": "Dua Lipa"},
    {"rank": 5, "title": "Rockstar", "artist": "DaBaby"},
    {"rank": 6, "title": "Adore You", "artist": "Harry Styles"},
    {"rank": 7, "title": "Life Is Good", "artist": "Future"},
    {"rank": 8, "title": "Memories", "artist": "Maroon 5"},
    {"rank": 9, "title": "The Bones", "artist": "Maren Morris"},
    {"rank": 10, "title": "Someone You Loved", "artist": "Lewis Capaldi"},
    {"rank": 11, "title": "Say So", "artist": "Doja Cat"},
    {"rank": 12, "title": "I Hope", "artist": "Gabby Barrett"},
    {"rank": 13, "title": "Whats Poppin", "artist": "Jack Harlow"},
    {"rank": 14, "title": "Dance Monkey", "artist": "Tones and I"},
    {"rank": 15, "title": "Savage", "artist": "Megan Thee Stallion"},
    {"rank": 16, "title": "Roxanne", "artist": "Arizona Zervas"},
    {"rank": 17, "title": "Intentions", "artist": "Justin Bieber"},
    {"rank": 18, "title": "Everything I Wanted", "artist": "Billie Eilish"},
    {"rank": 19, "title": "Roses", "artist": "Saint Jhn"},
    {"rank": 20, "title": "Watermelon Sugar", "artist": "Harry Styles"},
    {"rank": 21, "title": "Before You Go", "artist": "Lewis Capaldi"},
    {"rank": 22, "title": "Falling", "artist": "Trevor Daniel"},
    {"rank": 23, "title": "10,000 Hours", "artist": "Dan + Shay"},
    {"rank": 24, "title": "WAP", "artist": "Cardi B"},
    {"rank": 25, "title": "Ballin'", "artist": "Mustard"},
    {"rank": 26, "title": "Hot Girl Bummer", "artist": "Blackbear"},
    {"rank": 27, "title": "Blueberry Faygo", "artist": "Lil Mosey"},
    {"rank": 28, "title": "Heartless", "artist": "The Weeknd"},
    {"rank": 29, "title": "Bop", "artist": "DaBaby"},
    {"rank": 30, "title": "Lose You to Love Me", "artist": "Selena Gomez"},
    {"rank": 31, "title": "Good as Hell", "artist": "Lizzo"},
    {"rank": 32, "title": "Toosie Slide", "artist": "Drake"},
    {"rank": 33, "title": "Break My Heart", "artist": "Dua Lipa"},
    {"rank": 34, "title": "Chasin' You", "artist": "Morgan Wallen"},
    {"rank": 35, "title": "Savage Love", "artist": "Jawsh 685"},
    {"rank": 36, "title": "No Guidance", "artist": "Chris Brown"},
    {"rank": 37, "title": "My Oh My", "artist": "Camila Cabello"},
    {"rank": 38, "title": "Dynamite", "artist": "BTS"},
    {"rank": 39, "title": "Go Crazy", "artist": "Chris Brown"},
    {"rank": 40, "title": "High Fashion", "artist": "Roddy Ricch"},
    {"rank": 41, "title": "Laugh Now Cry Later", "artist": "Drake"},
    {"rank": 42, "title": "Woah", "artist": "Lil Baby"},
    {"rank": 43, "title": "Death Bed", "artist": "Powfu"},
    {"rank": 44, "title": "Senorita", "artist": "Shawn Mendes"},
    {"rank": 45, "title": "Highest in the Room", "artist": "Travis Scott"},
    {"rank": 46, "title": "Bad Guy", "artist": "Billie Eilish"},
    {"rank": 47, "title": "Mood", "artist": "24kGoldn"},
    {"rank": 48, "title": "Rain on Me", "artist": "Lady Gaga"},
    {"rank": 49, "title": "For the Night", "artist": "Pop Smoke"},
    {"rank": 50, "title": "Ritmo", "artist": "Black Eyed Peas"},
    {"rank": 51, "title": "Heart on Ice", "artist": "Rod Wave"},
    {"rank": 52, "title": "Nobody but You", "artist": "Blake Shelton"},
    {"rank": 53, "title": "Trampoline", "artist": "Shaed"},
    {"rank": 54, "title": "Come & Go", "artist": "Juice Wrld"},
    {"rank": 55, "title": "Truth Hurts", "artist": "Lizzo"},
    {"rank": 56, "title": "If the World Was Ending", "artist": "JP Saxe"},
    {"rank": 57, "title": "We Paid", "artist": "Lil Baby"},
    {"rank": 58, "title": "Yummy", "artist": "Justin Bieber"},
    {"rank": 59, "title": "One Man Band", "artist": "Old Dominion"},
    {"rank": 60, "title": "Got What I Got", "artist": "Jason Aldean"},
    {"rank": 61, "title": "Sunday Best", "artist": "Surfaces"},
    {"rank": 62, "title": "Godzilla", "artist": "Eminem"},
    {"rank": 63, "title": "Bandit", "artist": "Juice Wrld"},
    {"rank": 64, "title": "Party Girl", "artist": "StaySolidRocky"},
    {"rank": 65, "title": "Die from a Broken Heart", "artist": "Maddie & Tae"},
    {"rank": 66, "title": "Popstar", "artist": "DJ Khaled"},
    {"rank": 67, "title": "All I Want for Christmas Is You", "artist": "Mariah Carey"},
    {"rank": 68, "title": "One of Them Girls", "artist": "Lee Brice"},
    {"rank": 69, "title": "Hard to Forget", "artist": "Sam Hunt"},
    {"rank": 70, "title": "One Margarita", "artist": "Luke Bryan"},
    {"rank": 71, "title": "Panini", "artist": "Lil Nas X"},
    {"rank": 72, "title": "Hot", "artist": "Young Thug"},
    {"rank": 73, "title": "I Hope You're Happy Now", "artist": "Carly Pearce"},
    {"rank": 74, "title": "Emotionally Scarred", "artist": "Lil Baby"},
    {"rank": 75, "title": "Suicidal", "artist": "YNW Melly"},
    {"rank": 76, "title": "The Bigger Picture", "artist": "Lil Baby"},
    {"rank": 77, "title": "Only Human", "artist": "Jonas Brothers"},
    {"rank": 78, "title": "The Woo", "artist": "Pop Smoke"},
    {"rank": 79, "title": "Sum 2 Prove", "artist": "Lil Baby"},
    {"rank": 80, "title": "Stuck with U", "artist": "Ariana Grande"},
    {"rank": 81, "title": "Mood Swings", "artist": "Pop Smoke"},
    {"rank": 82, "title": "You Should Be Sad", "artist": "Halsey"},
    {"rank": 83, "title": "Dior", "artist": "Pop Smoke"},
    {"rank": 84, "title": "Supalonely", "artist": "Benee"},
    {"rank": 85, "title": "Even Though I'm Leaving", "artist": "Luke Combs"},
    {"rank": 86, "title": "The Scotts", "artist": "The Scotts"},
    {"rank": 87, "title": "Juicy", "artist": "Doja Cat"},
    {"rank": 88, "title": "Be Like That", "artist": "Kane Brown"},
    {"rank": 89, "title": "Homesick", "artist": "Kane Brown"},
    {"rank": 90, "title": "Rags2Riches", "artist": "Rod Wave"},
    {"rank": 91, "title": "Bluebird", "artist": "Miranda Lambert"},
    {"rank": 92, "title": "Wishing Well", "artist": "Juice Wrld"},
    {"rank": 93, "title": "Does to Me", "artist": "Luke Combs"},
    {"rank": 94, "title": "Pussy Fairy", "artist": "Jhene Aiko"},
    {"rank": 95, "title": "ILY", "artist": "Surf Mesa"},
    {"rank": 96, "title": "More Than My Hometown", "artist": "Morgan Wallen"},
    {"rank": 97, "title": "Lovin' on You", "artist": "Luke Combs"},
    {"rank": 98, "title": "Said Sum", "artist": "Moneybagg Yo"},
    {"rank": 99, "title": "Slide", "artist": "H.E.R."},
    {"rank": 100, "title": "Walk Em Down", "artist": "NLE Choppa"},
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


def title_similarity(left, right):
    return SequenceMatcher(None, normalize_text(left), normalize_text(right)).ratio()


def prepare_spotify_source():
    prepared = pd.read_csv(SPOTIFY_EXPORT)
    prepared["normalized_title"] = prepared["Track"].map(normalize_text)
    prepared["normalized_artist"] = prepared["Artist"].map(normalize_text)
    prepared["normalized_display_title"] = prepared["Title"].map(normalize_text)

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
                "matched_spotify_title": "",
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
    unmatched_rows = []

    for song in SONGS:
        match = select_best_match(song, prepared, artist_token_index)
        if match is None:
            unmatched_rows.append(song)
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
                "matched_spotify_title": match["Title"],
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
    if unmatched_rows:
        donor_pool = pd.concat([result[OUTPUT_COLUMNS], donors], ignore_index=True)
        inferred_rows = pd.DataFrame(build_unmatched_rows(unmatched_rows, donor_pool))
        result = pd.concat([result, inferred_rows], ignore_index=True, sort=False)
        result = result.sort_values("billboard_rank").reset_index(drop=True)

    if int(result[OUTPUT_COLUMNS].isna().sum().sum()) != 0:
        raise ValueError("Output dataset still contains missing values.")

    report_columns = [
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
    report = result[report_columns].copy()

    result[OUTPUT_COLUMNS].to_csv(OUTPUT_PATH, index=False)
    report.to_csv(REPORT_PATH, index=False)

    print(f"Direct Spotify matches: {len(matched_rows)}")
    print(f"Donor-inferred songs: {len(unmatched_rows)}")
    print(f"Total songs: {len(result)}")
    print(f"Dataset saved to: {OUTPUT_PATH}")
    print(f"Report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    build_dataset()
