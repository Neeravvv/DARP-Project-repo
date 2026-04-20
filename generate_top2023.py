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
]
OUTPUT_PATH = PROJECT_DIR / "top2023.csv"
REPORT_PATH = PROJECT_DIR / "top2023_match_report.csv"

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
    {"rank": 1, "title": "Last Night", "artist": "Morgan Wallen"},
    {"rank": 2, "title": "Flowers", "artist": "Miley Cyrus"},
    {"rank": 3, "title": "Kill Bill", "artist": "SZA"},
    {"rank": 4, "title": "Anti-Hero", "artist": "Taylor Swift"},
    {"rank": 5, "title": "Creepin'", "artist": "Metro Boomin"},
    {"rank": 6, "title": "Calm Down", "artist": "Rema"},
    {"rank": 7, "title": "Die for You", "artist": "The Weeknd"},
    {"rank": 8, "title": "Fast Car", "artist": "Luke Combs"},
    {"rank": 9, "title": "Snooze", "artist": "SZA"},
    {"rank": 10, "title": "I'm Good (Blue)", "artist": "David Guetta"},
    {"rank": 11, "title": "Unholy", "artist": "Sam Smith"},
    {"rank": 12, "title": "You Proof", "artist": "Morgan Wallen"},
    {"rank": 13, "title": "Something in the Orange", "artist": "Zach Bryan"},
    {"rank": 14, "title": "Rich Flex", "artist": "Drake"},
    {"rank": 15, "title": "As It Was", "artist": "Harry Styles"},
    {"rank": 16, "title": "Rock and a Hard Place", "artist": "Bailey Zimmerman"},
    {"rank": 17, "title": "Under the Influence", "artist": "Chris Brown"},
    {"rank": 18, "title": "Cruel Summer", "artist": "Taylor Swift"},
    {"rank": 19, "title": "Thinkin' Bout Me", "artist": "Morgan Wallen"},
    {"rank": 20, "title": "Boy's a Liar Pt. 2", "artist": "PinkPantheress"},
    {"rank": 21, "title": "Favorite Song", "artist": "Toosii"},
    {"rank": 22, "title": "Thought You Should Know", "artist": "Morgan Wallen"},
    {"rank": 23, "title": "Thank God", "artist": "Kane Brown"},
    {"rank": 24, "title": "Sure Thing", "artist": "Miguel"},
    {"rank": 25, "title": "All My Life", "artist": "Lil Durk"},
    {"rank": 26, "title": "Ella Baila Sola", "artist": "Eslabon Armado"},
    {"rank": 27, "title": "Karma", "artist": "Taylor Swift"},
    {"rank": 28, "title": "Just Wanna Rock", "artist": "Lil Uzi Vert"},
    {"rank": 29, "title": "Cuff It", "artist": "Beyonce"},
    {"rank": 30, "title": "Vampire", "artist": "Olivia Rodrigo"},
    {"rank": 31, "title": "FukUMean", "artist": "Gunna"},
    {"rank": 32, "title": "Lavender Haze", "artist": "Taylor Swift"},
    {"rank": 33, "title": "Players", "artist": "Coi Leray"},
    {"rank": 34, "title": "Need a Favor", "artist": "Jelly Roll"},
    {"rank": 35, "title": "Dance the Night", "artist": "Dua Lipa"},
    {"rank": 36, "title": "Love You Anyway", "artist": "Luke Combs"},
    {"rank": 37, "title": "One Thing at a Time", "artist": "Morgan Wallen"},
    {"rank": 38, "title": "Superhero (Heroes & Villains)", "artist": "Metro Boomin"},
    {"rank": 39, "title": "Bad Habit", "artist": "Steve Lacy"},
    {"rank": 40, "title": "La Bebe", "artist": "Yng Lvcas"},
    {"rank": 41, "title": "Golden Hour", "artist": "Jvke"},
    {"rank": 42, "title": "Religiously", "artist": "Bailey Zimmerman"},
    {"rank": 43, "title": "Spin Bout U", "artist": "Drake"},
    {"rank": 44, "title": "Cupid", "artist": "Fifty Fifty"},
    {"rank": 45, "title": "Search & Rescue", "artist": "Drake"},
    {"rank": 46, "title": "Barbie World", "artist": "Nicki Minaj"},
    {"rank": 47, "title": "Next Thing You Know", "artist": "Jordan Davis"},
    {"rank": 48, "title": "Escapism", "artist": "Raye"},
    {"rank": 49, "title": "Un x100to", "artist": "Grupo Frontera"},
    {"rank": 50, "title": "Until I Found You", "artist": "Stephen Sanchez"},
    {"rank": 51, "title": "Shirt", "artist": "SZA"},
    {"rank": 52, "title": "Paint the Town Red", "artist": "Doja Cat"},
    {"rank": 53, "title": "Made You Look", "artist": "Meghan Trainor"},
    {"rank": 54, "title": "Wait in the Truck", "artist": "Hardy"},
    {"rank": 55, "title": "All I Want for Christmas Is You", "artist": "Mariah Carey"},
    {"rank": 56, "title": "Everything I Love", "artist": "Morgan Wallen"},
    {"rank": 57, "title": "Chemical", "artist": "Post Malone"},
    {"rank": 58, "title": "Heart Like a Truck", "artist": "Lainey Wilson"},
    {"rank": 59, "title": "Going, Going, Gone", "artist": "Luke Combs"},
    {"rank": 60, "title": "Rockin' Around the Christmas Tree", "artist": "Brenda Lee"},
    {"rank": 61, "title": "Dancin' in the Country", "artist": "Tyler Hubbard"},
    {"rank": 62, "title": "Daylight", "artist": "David Kushner"},
    {"rank": 63, "title": "Lift Me Up", "artist": "Rihanna"},
    {"rank": 64, "title": "Eyes Closed", "artist": "Ed Sheeran"},
    {"rank": 65, "title": "TQG", "artist": "Karol G"},
    {"rank": 66, "title": "Try That in a Small Town", "artist": "Jason Aldean"},
    {"rank": 67, "title": "Tennessee Orange", "artist": "Megan Moroney"},
    {"rank": 68, "title": "Jingle Bell Rock", "artist": "Bobby Helms"},
    {"rank": 69, "title": "Princess Diana", "artist": "Ice Spice"},
    {"rank": 70, "title": "Tomorrow 2", "artist": "GloRilla"},
    {"rank": 71, "title": "A Holly Jolly Christmas", "artist": "Burl Ives"},
    {"rank": 72, "title": "Where She Goes", "artist": "Bad Bunny"},
    {"rank": 73, "title": "Bebe Dame", "artist": "Fuerza Regida"},
    {"rank": 74, "title": "I Remember Everything", "artist": "Zach Bryan"},
    {"rank": 75, "title": "I Like You (A Happier Song)", "artist": "Post Malone"},
    {"rank": 76, "title": "What It Is (Block Boy)", "artist": "Doechii"},
    {"rank": 77, "title": "Nobody Gets Me", "artist": "SZA"},
    {"rank": 78, "title": "Rich Men North of Richmond", "artist": "Oliver Anthony Music"},
    {"rank": 79, "title": "Super Freaky Girl", "artist": "Nicki Minaj"},
    {"rank": 80, "title": "Dial Drunk", "artist": "Noah Kahan"},
    {"rank": 81, "title": "What Was I Made For?", "artist": "Billie Eilish"},
    {"rank": 82, "title": "Seven", "artist": "Jung Kook"},
    {"rank": 83, "title": "Wait for U", "artist": "Future"},
    {"rank": 84, "title": "Last Christmas", "artist": "Wham!"},
    {"rank": 85, "title": "Handle on You", "artist": "Parker McCollum"},
    {"rank": 86, "title": "Por Las Noches", "artist": "Peso Pluma"},
    {"rank": 87, "title": "Memory Lane", "artist": "Old Dominion"},
    {"rank": 88, "title": "Area Codes", "artist": "Kaliii"},
    {"rank": 89, "title": "Bury Me in Georgia", "artist": "Kane Brown"},
    {"rank": 90, "title": "PRC", "artist": "Peso Pluma"},
    {"rank": 91, "title": "What My World Spins Around", "artist": "Jordan Davis"},
    {"rank": 92, "title": "Ain't That Some", "artist": "Morgan Wallen"},
    {"rank": 93, "title": "Wild as Her", "artist": "Corey Kent"},
    {"rank": 94, "title": "Peaches & Eggplants", "artist": "Young Nudy"},
    {"rank": 95, "title": "I Wrote the Book", "artist": "Morgan Wallen"},
    {"rank": 96, "title": "Bzrp Music Sessions, Vol. 53", "artist": "Bizarrap"},
    {"rank": 97, "title": "Meltdown", "artist": "Travis Scott"},
    {"rank": 98, "title": "Put It on da Floor Again", "artist": "Latto"},
    {"rank": 99, "title": "Bloody Mary", "artist": "Lady Gaga"},
    {"rank": 100, "title": "Watermelon Moonshine", "artist": "Lainey Wilson"},
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
