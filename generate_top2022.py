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
]
OUTPUT_PATH = PROJECT_DIR / "top2022.csv"
REPORT_PATH = PROJECT_DIR / "top2022_match_report.csv"

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
    {"rank": 1, "title": "Heat Waves", "artist": "Glass Animals"},
    {"rank": 2, "title": "As It Was", "artist": "Harry Styles"},
    {"rank": 3, "title": "Stay", "artist": "The Kid Laroi"},
    {"rank": 4, "title": "Easy on Me", "artist": "Adele"},
    {"rank": 5, "title": "Shivers", "artist": "Ed Sheeran"},
    {"rank": 6, "title": "First Class", "artist": "Jack Harlow"},
    {"rank": 7, "title": "Big Energy", "artist": "Latto"},
    {"rank": 8, "title": "Ghost", "artist": "Justin Bieber"},
    {"rank": 9, "title": "Super Gremlin", "artist": "Kodak Black"},
    {"rank": 10, "title": "Cold Heart", "artist": "Elton John"},
    {"rank": 11, "title": "Wait for U", "artist": "Future"},
    {"rank": 12, "title": "About Damn Time", "artist": "Lizzo"},
    {"rank": 13, "title": "Bad Habits", "artist": "Ed Sheeran"},
    {"rank": 14, "title": "Thats What I Want", "artist": "Lil Nas X"},
    {"rank": 15, "title": "Enemy", "artist": "Imagine Dragons"},
    {"rank": 16, "title": "Industry Baby", "artist": "Lil Nas X"},
    {"rank": 17, "title": "ABCDEFU", "artist": "Gayle"},
    {"rank": 18, "title": "Need to Know", "artist": "Doja Cat"},
    {"rank": 19, "title": "Wasted on You", "artist": "Morgan Wallen"},
    {"rank": 20, "title": "Me Porto Bonito", "artist": "Bad Bunny"},
    {"rank": 21, "title": "Woman", "artist": "Doja Cat"},
    {"rank": 22, "title": "Titi Me Pregunto", "artist": "Bad Bunny"},
    {"rank": 23, "title": "Running Up That Hill", "artist": "Kate Bush"},
    {"rank": 24, "title": "We Don't Talk About Bruno", "artist": "Carolina Gaitan"},
    {"rank": 25, "title": "Late Night Talking", "artist": "Harry Styles"},
    {"rank": 26, "title": "I Like You", "artist": "Post Malone"},
    {"rank": 27, "title": "You Proof", "artist": "Morgan Wallen"},
    {"rank": 28, "title": "Bad Habit", "artist": "Steve Lacy"},
    {"rank": 29, "title": "Sunroof", "artist": "Nicky Youre"},
    {"rank": 30, "title": "One Right Now", "artist": "Post Malone"},
    {"rank": 31, "title": "Good 4 U", "artist": "Olivia Rodrigo"},
    {"rank": 32, "title": "Numb Little Bug", "artist": "Em Beihold"},
    {"rank": 33, "title": "Jimmy Cooks", "artist": "Drake"},
    {"rank": 34, "title": "'Til You Can't", "artist": "Cody Johnson"},
    {"rank": 35, "title": "Fancy Like", "artist": "Walker Hayes"},
    {"rank": 36, "title": "The Kind of Love We Make", "artist": "Luke Combs"},
    {"rank": 37, "title": "I Ain't Worried", "artist": "OneRepublic"},
    {"rank": 38, "title": "Break My Soul", "artist": "Beyonce"},
    {"rank": 39, "title": "Something in the Orange", "artist": "Zach Bryan"},
    {"rank": 40, "title": "Save Your Tears", "artist": "The Weeknd"},
    {"rank": 41, "title": "Smokin out the Window", "artist": "Silk Sonic"},
    {"rank": 42, "title": "Levitating", "artist": "Dua Lipa"},
    {"rank": 43, "title": "In a Minute", "artist": "Lil Baby"},
    {"rank": 44, "title": "Moscow Mule", "artist": "Bad Bunny"},
    {"rank": 45, "title": "You Right", "artist": "Doja Cat"},
    {"rank": 46, "title": "She Had Me at Heads Carolina", "artist": "Cole Swindell"},
    {"rank": 47, "title": "Vegas", "artist": "Doja Cat"},
    {"rank": 48, "title": "Pushin P", "artist": "Gunna"},
    {"rank": 49, "title": "Buy Dirt", "artist": "Jordan Davis"},
    {"rank": 50, "title": "I Hate U", "artist": "SZA"},
    {"rank": 51, "title": "Boyfriend", "artist": "Dove Cameron"},
    {"rank": 52, "title": "Glimpse of Us", "artist": "Joji"},
    {"rank": 53, "title": "Surface Pressure", "artist": "Jessica Darrow"},
    {"rank": 54, "title": "Fall in Love", "artist": "Bailey Zimmerman"},
    {"rank": 55, "title": "Love Nwantiti", "artist": "CKay"},
    {"rank": 56, "title": "Super Freaky Girl", "artist": "Nicki Minaj"},
    {"rank": 57, "title": "Hrs and Hrs", "artist": "Muni Long"},
    {"rank": 58, "title": "Sand in My Boots", "artist": "Morgan Wallen"},
    {"rank": 59, "title": "Mamiii", "artist": "Becky G"},
    {"rank": 60, "title": "Knife Talk", "artist": "Drake"},
    {"rank": 61, "title": "AA", "artist": "Walker Hayes"},
    {"rank": 62, "title": "Sweetest Pie", "artist": "Megan Thee Stallion"},
    {"rank": 63, "title": "Provenza", "artist": "Karol G"},
    {"rank": 64, "title": "Essence", "artist": "Wizkid"},
    {"rank": 65, "title": "All I Want for Christmas Is You", "artist": "Mariah Carey"},
    {"rank": 66, "title": "Bam Bam", "artist": "Camila Cabello"},
    {"rank": 67, "title": "5 Foot 9", "artist": "Tyler Hubbard"},
    {"rank": 68, "title": "Get Into It (Yuh)", "artist": "Doja Cat"},
    {"rank": 69, "title": "Efecto", "artist": "Bad Bunny"},
    {"rank": 70, "title": "Rock and a Hard Place", "artist": "Bailey Zimmerman"},
    {"rank": 71, "title": "Doin' This", "artist": "Luke Combs"},
    {"rank": 72, "title": "Oh My God", "artist": "Adele"},
    {"rank": 73, "title": "Better Days", "artist": "Neiked"},
    {"rank": 74, "title": "Meet Me at Our Spot", "artist": "The Anxiety"},
    {"rank": 75, "title": "Fingers Crossed", "artist": "Lauren Spencer-Smith"},
    {"rank": 76, "title": "All Too Well", "artist": "Taylor Swift"},
    {"rank": 77, "title": "Party", "artist": "Bad Bunny"},
    {"rank": 78, "title": "Despues de la Playa", "artist": "Bad Bunny"},
    {"rank": 79, "title": "You Should Probably Leave", "artist": "Chris Stapleton"},
    {"rank": 80, "title": "Rockin' Around the Christmas Tree", "artist": "Brenda Lee"},
    {"rank": 81, "title": "Broadway Girls", "artist": "Lil Durk"},
    {"rank": 82, "title": "Take My Name", "artist": "Parmalee"},
    {"rank": 83, "title": "What Happened to Virgil", "artist": "Lil Durk"},
    {"rank": 84, "title": "Puffin on Zootiez", "artist": "Future"},
    {"rank": 85, "title": "Like I Love Country Music", "artist": "Kane Brown"},
    {"rank": 86, "title": "Jingle Bell Rock", "artist": "Bobby Helms"},
    {"rank": 87, "title": "Ojitos Lindos", "artist": "Bad Bunny"},
    {"rank": 88, "title": "Trouble with a Heartbreak", "artist": "Jason Aldean"},
    {"rank": 89, "title": "A Holly Jolly Christmas", "artist": "Burl Ives"},
    {"rank": 90, "title": "Kiss Me More", "artist": "Doja Cat"},
    {"rank": 91, "title": "She Likes It", "artist": "Russell Dickerson"},
    {"rank": 92, "title": "Never Say Never", "artist": "Cole Swindell"},
    {"rank": 93, "title": "Damn Strait", "artist": "Scotty McCreery"},
    {"rank": 94, "title": "She's All I Wanna Be", "artist": "Tate McRae"},
    {"rank": 95, "title": "Last Night Lonely", "artist": "Jon Pardi"},
    {"rank": 96, "title": "Flower Shops", "artist": "Ernest"},
    {"rank": 97, "title": "To the Moon", "artist": "Jnr Choi"},
    {"rank": 98, "title": "Unholy", "artist": "Sam Smith"},
    {"rank": 99, "title": "One Mississippi", "artist": "Kane Brown"},
    {"rank": 100, "title": "Circles Around This Town", "artist": "Maren Morris"},
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
