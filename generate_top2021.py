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
    PROJECT_DIR / "top2020.csv",
]
OUTPUT_PATH = Path(__file__).with_name("top2021.csv")
REPORT_PATH = Path(__file__).with_name("top2021_match_report.csv")

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
    {"rank": 1, "title": "Levitating", "artist": "Dua Lipa"},
    {"rank": 2, "title": "Save Your Tears", "artist": "The Weeknd"},
    {"rank": 3, "title": "Blinding Lights", "artist": "The Weeknd"},
    {"rank": 4, "title": "Mood", "artist": "24kGoldn"},
    {"rank": 5, "title": "Good 4 U", "artist": "Olivia Rodrigo"},
    {"rank": 6, "title": "Kiss Me More", "artist": "Doja Cat"},
    {"rank": 7, "title": "Leave the Door Open", "artist": "Silk Sonic"},
    {"rank": 8, "title": "Drivers License", "artist": "Olivia Rodrigo"},
    {"rank": 9, "title": "Montero (Call Me by Your Name)", "artist": "Lil Nas X"},
    {"rank": 10, "title": "Peaches", "artist": "Justin Bieber"},
    {"rank": 11, "title": "Butter", "artist": "BTS"},
    {"rank": 12, "title": "Stay", "artist": "The Kid Laroi"},
    {"rank": 13, "title": "Deja Vu", "artist": "Olivia Rodrigo"},
    {"rank": 14, "title": "Positions", "artist": "Ariana Grande"},
    {"rank": 15, "title": "Bad Habits", "artist": "Ed Sheeran"},
    {"rank": 16, "title": "Heat Waves", "artist": "Glass Animals"},
    {"rank": 17, "title": "Without You", "artist": "The Kid Laroi"},
    {"rank": 18, "title": "Forever After All", "artist": "Luke Combs"},
    {"rank": 19, "title": "Go Crazy", "artist": "Chris Brown"},
    {"rank": 20, "title": "Astronaut in the Ocean", "artist": "Masked Wolf"},
    {"rank": 21, "title": "34+35", "artist": "Ariana Grande"},
    {"rank": 22, "title": "What You Know Bout Love", "artist": "Pop Smoke"},
    {"rank": 23, "title": "My Ex's Best Friend", "artist": "Machine Gun Kelly"},
    {"rank": 24, "title": "Industry Baby", "artist": "Lil Nas X"},
    {"rank": 25, "title": "Therefore I Am", "artist": "Billie Eilish"},
    {"rank": 26, "title": "Up", "artist": "Cardi B"},
    {"rank": 27, "title": "Fancy Like", "artist": "Walker Hayes"},
    {"rank": 28, "title": "Dakiti", "artist": "Bad Bunny"},
    {"rank": 29, "title": "Best Friend", "artist": "Saweetie"},
    {"rank": 30, "title": "Rapstar", "artist": "Polo G"},
    {"rank": 31, "title": "Heartbreak Anniversary", "artist": "Giveon"},
    {"rank": 32, "title": "For the Night", "artist": "Pop Smoke"},
    {"rank": 33, "title": "Calling My Phone", "artist": "Lil Tjay"},
    {"rank": 34, "title": "Beautiful Mistakes", "artist": "Maroon 5"},
    {"rank": 35, "title": "Holy", "artist": "Justin Bieber"},
    {"rank": 36, "title": "On Me", "artist": "Lil Baby"},
    {"rank": 37, "title": "You Broke Me First", "artist": "Tate McRae"},
    {"rank": 38, "title": "Traitor", "artist": "Olivia Rodrigo"},
    {"rank": 39, "title": "Back in Blood", "artist": "Pooh Shiesty"},
    {"rank": 40, "title": "I Hope", "artist": "Gabby Barrett"},
    {"rank": 41, "title": "Dynamite", "artist": "BTS"},
    {"rank": 42, "title": "Wockesha", "artist": "Moneybagg Yo"},
    {"rank": 43, "title": "You Right", "artist": "Doja Cat"},
    {"rank": 44, "title": "Beat Box 2", "artist": "SpotemGottem"},
    {"rank": 45, "title": "Laugh Now Cry Later", "artist": "Drake"},
    {"rank": 46, "title": "Need to Know", "artist": "Doja Cat"},
    {"rank": 47, "title": "Wants and Needs", "artist": "Drake"},
    {"rank": 48, "title": "Way 2 Sexy", "artist": "Drake"},
    {"rank": 49, "title": "Telepatia", "artist": "Kali Uchis"},
    {"rank": 50, "title": "Whoopty", "artist": "CJ"},
    {"rank": 51, "title": "Lemonade", "artist": "Internet Money"},
    {"rank": 52, "title": "Good Days", "artist": "SZA"},
    {"rank": 53, "title": "Starting Over", "artist": "Chris Stapleton"},
    {"rank": 54, "title": "Body", "artist": "Megan Thee Stallion"},
    {"rank": 55, "title": "Willow", "artist": "Taylor Swift"},
    {"rank": 56, "title": "Bang!", "artist": "AJR"},
    {"rank": 57, "title": "Better Together", "artist": "Luke Combs"},
    {"rank": 58, "title": "You're Mines Still", "artist": "Yung Bleu"},
    {"rank": 59, "title": "Every Chance I Get", "artist": "DJ Khaled"},
    {"rank": 60, "title": "Essence", "artist": "Wizkid"},
    {"rank": 61, "title": "Chasing After You", "artist": "Ryan Hurd"},
    {"rank": 62, "title": "The Good Ones", "artist": "Gabby Barrett"},
    {"rank": 63, "title": "Leave Before You Love Me", "artist": "Marshmello"},
    {"rank": 64, "title": "Glad You Exist", "artist": "Dan + Shay"},
    {"rank": 65, "title": "Lonely", "artist": "Justin Bieber"},
    {"rank": 66, "title": "Beggin'", "artist": "Maneskin"},
    {"rank": 67, "title": "Streets", "artist": "Doja Cat"},
    {"rank": 68, "title": "What's Next", "artist": "Drake"},
    {"rank": 69, "title": "Famous Friends", "artist": "Chris Young"},
    {"rank": 70, "title": "Lil Bit", "artist": "Nelly"},
    {"rank": 71, "title": "Thot Shit", "artist": "Megan Thee Stallion"},
    {"rank": 72, "title": "Late at Night", "artist": "Roddy Ricch"},
    {"rank": 73, "title": "Kings & Queens", "artist": "Ava Max"},
    {"rank": 74, "title": "Anyone", "artist": "Justin Bieber"},
    {"rank": 75, "title": "Track Star", "artist": "Mooski"},
    {"rank": 76, "title": "Time Today", "artist": "Moneybagg Yo"},
    {"rank": 77, "title": "Cry Baby", "artist": "Megan Thee Stallion"},
    {"rank": 78, "title": "All I Want for Christmas Is You", "artist": "Mariah Carey"},
    {"rank": 79, "title": "No More Parties", "artist": "Coi Leray"},
    {"rank": 80, "title": "What's Your Country Song", "artist": "Thomas Rhett"},
    {"rank": 81, "title": "One Too Many", "artist": "Keith Urban"},
    {"rank": 82, "title": "Arcade", "artist": "Duncan Laurence"},
    {"rank": 83, "title": "Yonaguni", "artist": "Bad Bunny"},
    {"rank": 84, "title": "Good Time", "artist": "Niko Moon"},
    {"rank": 85, "title": "If I Didn't Love You", "artist": "Jason Aldean"},
    {"rank": 86, "title": "Knife Talk", "artist": "Drake"},
    {"rank": 87, "title": "POV", "artist": "Ariana Grande"},
    {"rank": 88, "title": "Just the Way", "artist": "Parmalee"},
    {"rank": 89, "title": "Take My Breath", "artist": "The Weeknd"},
    {"rank": 90, "title": "We're Good", "artist": "Dua Lipa"},
    {"rank": 91, "title": "Hell of a View", "artist": "Eric Church"},
    {"rank": 92, "title": "Rockin' Around the Christmas Tree", "artist": "Brenda Lee"},
    {"rank": 93, "title": "Put Your Records On", "artist": "Ritt Momney"},
    {"rank": 94, "title": "Happier Than Ever", "artist": "Billie Eilish"},
    {"rank": 95, "title": "Single Saturday Night", "artist": "Cole Swindell"},
    {"rank": 96, "title": "Things a Man Oughta Know", "artist": "Lainey Wilson"},
    {"rank": 97, "title": "Throat Baby (Go Baby)", "artist": "BRS Kash"},
    {"rank": 98, "title": "Tombstone", "artist": "Rod Wave"},
    {"rank": 99, "title": "Drinkin' Beer. Talkin' God. Amen.", "artist": "Chase Rice"},
    {"rank": 100, "title": "Todo de Ti", "artist": "Rauw Alejandro"},
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
