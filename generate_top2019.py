import time
from pathlib import Path

import pandas as pd
import requests

session = requests.Session()
PUBLIC_DATASET_PATH = Path(__file__).with_name("billboard_2019_merged_dataset.csv")


def raise_api_error(response, context):
    try:
        details = response.json()
    except ValueError:
        details = response.text
    raise requests.exceptions.HTTPError(
        f"{context} failed with status {response.status_code}: {details}",
        response=response,
    )


MUSICBRAINZ_HEADERS = {
    "User-Agent": "neeravbhuyan@gmail.com"
}

# =========================
# BILLBOARD 2019 HOT 100
# =========================
songs = [
    {"rank": 1, "title": "Old Town Road", "artist": "Lil Nas X"},
    {"rank": 2, "title": "Sunflower", "artist": "Post Malone"},
    {"rank": 3, "title": "Without Me", "artist": "Halsey"},
    {"rank": 4, "title": "Bad Guy", "artist": "Billie Eilish"},
    {"rank": 5, "title": "Wow", "artist": "Post Malone"},
    {"rank": 6, "title": "Happier", "artist": "Marshmello"},
    {"rank": 7, "title": "7 Rings", "artist": "Ariana Grande"},
    {"rank": 8, "title": "Talk", "artist": "Khalid"},
    {"rank": 9, "title": "Sicko Mode", "artist": "Travis Scott"},
    {"rank": 10, "title": "Sucker", "artist": "Jonas Brothers"},
    {"rank": 11, "title": "High Hopes", "artist": "Panic! at the Disco"},
    {"rank": 12, "title": "Thank U, Next", "artist": "Ariana Grande"},
    {"rank": 13, "title": "Truth Hurts", "artist": "Lizzo"},
    {"rank": 14, "title": "Dancing with a Stranger", "artist": "Sam Smith"},
    {"rank": 15, "title": "Senorita", "artist": "Shawn Mendes"},
    {"rank": 16, "title": "I Don't Care", "artist": "Ed Sheeran"},
    {"rank": 17, "title": "Eastside", "artist": "Benny Blanco"},
    {"rank": 18, "title": "Going Bad", "artist": "Meek Mill"},
    {"rank": 19, "title": "Shallow", "artist": "Lady Gaga"},
    {"rank": 20, "title": "Better", "artist": "Khalid"},
    {"rank": 21, "title": "No Guidance", "artist": "Chris Brown"},
    {"rank": 22, "title": "Girls Like You", "artist": "Maroon 5"},
    {"rank": 23, "title": "Sweet but Psycho", "artist": "Ava Max"},
    {"rank": 24, "title": "Suge", "artist": "DaBaby"},
    {"rank": 25, "title": "Middle Child", "artist": "J. Cole"},
    {"rank": 26, "title": "Drip Too Hard", "artist": "Lil Baby"},
    {"rank": 27, "title": "Someone You Loved", "artist": "Lewis Capaldi"},
    {"rank": 28, "title": "Ransom", "artist": "Lil Tecca"},
    {"rank": 29, "title": "If I Can't Have You", "artist": "Shawn Mendes"},
    {"rank": 30, "title": "Goodbyes", "artist": "Post Malone"},
    {"rank": 31, "title": "Zeze", "artist": "Kodak Black"},
    {"rank": 32, "title": "Better Now", "artist": "Post Malone"},
    {"rank": 33, "title": "Youngblood", "artist": "5 Seconds of Summer"},
    {"rank": 34, "title": "Money in the Grave", "artist": "Drake"},
    {"rank": 35, "title": "Speechless", "artist": "Dan + Shay"},
    {"rank": 36, "title": "Break Up with Your Girlfriend, I'm Bored", "artist": "Ariana Grande"},
    {"rank": 37, "title": "Please Me", "artist": "Cardi B"},
    {"rank": 38, "title": "Money", "artist": "Cardi B"},
    {"rank": 39, "title": "You Need to Calm Down", "artist": "Taylor Swift"},
    {"rank": 40, "title": "Panini", "artist": "Lil Nas X"},
    {"rank": 41, "title": "Look Back at It", "artist": "A Boogie wit da Hoodie"},
    {"rank": 42, "title": "A Lot", "artist": "21 Savage"},
    {"rank": 43, "title": "Me!", "artist": "Taylor Swift"},
    {"rank": 44, "title": "Mia", "artist": "Bad Bunny"},
    {"rank": 45, "title": "Pop Out", "artist": "Polo G"},
    {"rank": 46, "title": "Beautiful Crazy", "artist": "Luke Combs"},
    {"rank": 47, "title": "Thotiana", "artist": "Blueface"},
    {"rank": 48, "title": "Lucid Dreams", "artist": "Juice WRLD"},
    {"rank": 49, "title": "Mo Bamba", "artist": "Sheck Wes"},
    {"rank": 50, "title": "Beautiful People", "artist": "Ed Sheeran"},
    {"rank": 51, "title": "Wake Up in the Sky", "artist": "Gucci Mane"},
    {"rank": 52, "title": "Whiskey Glasses", "artist": "Morgan Wallen"},
    {"rank": 53, "title": "God's Country", "artist": "Blake Shelton"},
    {"rank": 54, "title": "Be Alright", "artist": "Dean Lewis"},
    {"rank": 55, "title": "Pure Water", "artist": "Mustard"},
    {"rank": 56, "title": "The Git Up", "artist": "Blanco Brown"},
    {"rank": 57, "title": "Taki Taki", "artist": "DJ Snake"},
    {"rank": 58, "title": "Close to Me", "artist": "Ellie Goulding"},
    {"rank": 59, "title": "Envy Me", "artist": "Calboy"},
    {"rank": 60, "title": "You Say", "artist": "Lauren Daigle"},
    {"rank": 61, "title": "Hey Look Ma, I Made It", "artist": "Panic! at the Disco"},
    {"rank": 62, "title": "Circles", "artist": "Post Malone"},
    {"rank": 63, "title": "Beer Never Broke My Heart", "artist": "Luke Combs"},
    {"rank": 64, "title": "The London", "artist": "Young Thug"},
    {"rank": 65, "title": "Con Calma", "artist": "Daddy Yankee"},
    {"rank": 66, "title": "Murder on My Mind", "artist": "YNW Melly"},
    {"rank": 67, "title": "When the Party's Over", "artist": "Billie Eilish"},
    {"rank": 68, "title": "Act Up", "artist": "City Girls"},
    {"rank": 69, "title": "I Like It", "artist": "Cardi B"},
    {"rank": 70, "title": "Trampoline", "artist": "Shaed"},
    {"rank": 71, "title": "Leave Me Alone", "artist": "Flipp Dinero"},
    {"rank": 72, "title": "Breathin", "artist": "Ariana Grande"},
    {"rank": 73, "title": "Bury a Friend", "artist": "Billie Eilish"},
    {"rank": 74, "title": "Close Friends", "artist": "Lil Baby"},
    {"rank": 75, "title": "Baby Shark", "artist": "Pinkfong"},
    {"rank": 76, "title": "My Type", "artist": "Saweetie"},
    {"rank": 77, "title": "Worth It", "artist": "YK Osiris"},
    {"rank": 78, "title": "Only Human", "artist": "Jonas Brothers"},
    {"rank": 79, "title": "Knockin' Boots", "artist": "Luke Bryan"},
    {"rank": 80, "title": "Trip", "artist": "Ella Mai"},
    {"rank": 81, "title": "Rumor", "artist": "Lee Brice"},
    {"rank": 82, "title": "Swervin", "artist": "A Boogie wit da Hoodie"},
    {"rank": 83, "title": "How Do You Sleep?", "artist": "Sam Smith"},
    {"rank": 84, "title": "Baby", "artist": "Lil Baby"},
    {"rank": 85, "title": "Look What God Gave Her", "artist": "Thomas Rhett"},
    {"rank": 86, "title": "Good as You", "artist": "Kane Brown"},
    {"rank": 87, "title": "Clout", "artist": "Offset"},
    {"rank": 88, "title": "Love Lies", "artist": "Khalid"},
    {"rank": 89, "title": "One Thing Right", "artist": "Marshmello"},
    {"rank": 90, "title": "Cash Shit", "artist": "Megan Thee Stallion"},
    {"rank": 91, "title": "Tequila", "artist": "Dan + Shay"},
    {"rank": 92, "title": "Shotta Flow", "artist": "NLE Choppa"},
    {"rank": 93, "title": "Hot Girl Summer", "artist": "Megan Thee Stallion"},
    {"rank": 94, "title": "Talk You Out of It", "artist": "Florida Georgia Line"},
    {"rank": 95, "title": "Beautiful", "artist": "Bazzi"},
    {"rank": 96, "title": "Eyes on You", "artist": "Chase Rice"},
    {"rank": 97, "title": "All to Myself", "artist": "Dan + Shay"},
    {"rank": 98, "title": "Boyfriend", "artist": "Ariana Grande"},
    {"rank": 99, "title": "Walk Me Home", "artist": "Pink"},
    {"rank": 100, "title": "Robbery", "artist": "Juice WRLD"},
]


def search_musicbrainz_recording(track_name, artist_name, release_year=None):
    url = "https://musicbrainz.org/ws/2/recording"
    query = f'recording:"{track_name}" AND artist:"{artist_name}"'
    params = {"query": query, "fmt": "json", "limit": 5}
    response = session.get(url, headers=MUSICBRAINZ_HEADERS, params=params, timeout=30)
    if not response.ok:
        raise_api_error(response, "MusicBrainz search request")

    recordings = response.json().get("recordings", [])
    if not recordings:
        return None

    def score_recording(recording):
        score = int(recording.get("score", 0))
        mb_artists = ", ".join(
            artist_credit.get("name", "")
            for artist_credit in recording.get("artist-credit", [])
            if isinstance(artist_credit, dict)
        ).lower()
        if artist_name.lower() in mb_artists:
            score += 15

        first_release = recording.get("first-release-date", "")
        if release_year and first_release.startswith(str(release_year)):
            score += 10
        return score

    return max(recordings, key=score_recording)


def chunk_list(items, size):
    for index in range(0, len(items), size):
        yield items[index:index + size]


def extract_acousticbrainz_features(mbid, low_level, high_level):
    if not low_level and not high_level:
        return None

    tonal = low_level.get("tonal", {})
    rhythm = low_level.get("rhythm", {})
    metadata = low_level.get("metadata", {}).get("tags", {})
    highlevel = high_level.get("highlevel", {})

    return {
        "ab_mbid": mbid,
        "ab_bpm": rhythm.get("bpm"),
        "ab_lowlevel_danceability": rhythm.get("danceability"),
        "ab_key_key": tonal.get("key_key"),
        "ab_key_scale": tonal.get("key_scale"),
        "ab_chords_key": tonal.get("chords_key"),
        "ab_chords_scale": tonal.get("chords_scale"),
        "ab_average_loudness": low_level.get("lowlevel", {}).get("average_loudness"),
        "ab_dynamic_complexity": low_level.get("lowlevel", {}).get("dynamic_complexity"),
        "ab_highlevel_danceability": highlevel.get("danceability", {}).get("all", {}).get("danceable"),
        "ab_highlevel_danceability_label": highlevel.get("danceability", {}).get("value"),
        "ab_mood_happy": highlevel.get("mood_happy", {}).get("all", {}).get("happy"),
        "ab_mood_sad": highlevel.get("mood_sad", {}).get("all", {}).get("sad"),
        "ab_mood_relaxed": highlevel.get("mood_relaxed", {}).get("all", {}).get("relaxed"),
        "ab_mood_party": highlevel.get("mood_party", {}).get("all", {}).get("party"),
        "ab_voice_instrumental": highlevel.get("voice_instrumental", {}).get("value"),
        "ab_genre_dortmund": highlevel.get("genre_dortmund", {}).get("value"),
        "ab_genre_rosamerica": highlevel.get("genre_rosamerica", {}).get("value"),
        "ab_language": metadata.get("language", [None])[0],
    }


COLUMN_RENAMES = {
    "rank": "billboard_rank",
    "ab_key_key": "key",
    "ab_key_scale": "scale",
    "ab_chords_key": "chord_key",
    "ab_chords_scale": "chord_scale",
    "ab_average_loudness": "average_loudness",
    "ab_dynamic_complexity": "dynamic_complexity",
    "ab_highlevel_danceability": "danceable_probability",
    "ab_highlevel_danceability_label": "danceability_label",
    "ab_mood_happy": "happy_probability",
    "ab_mood_sad": "sad_probability",
    "ab_mood_relaxed": "relaxed_probability",
    "ab_mood_party": "party_probability",
    "ab_voice_instrumental": "voice_or_instrumental",
    "ab_genre_dortmund": "genre_dortmund",
    "ab_genre_rosamerica": "genre_rosamerica",
}

PUBLIC_COLUMNS = {
    "tempo_bpm": "tempo_from_public_dataset",
    "danceability_score": "danceability_from_public_dataset",
    "acousticness": "acousticness",
    "speechiness": "speechiness",
    "duration_min": "duration_minutes",
}


def fetch_acousticbrainz_bulk(recording_ids):
    if not recording_ids:
        return {}

    base_url = "https://acousticbrainz.org/api/v1"
    features_by_mbid = {}

    low_level_feature_list = ";".join(
        [
            "lowlevel.average_loudness",
            "lowlevel.dynamic_complexity",
            "metadata.tags",
            "rhythm.bpm",
            "rhythm.danceability",
            "tonal.chords_key",
            "tonal.chords_scale",
            "tonal.key_key",
            "tonal.key_scale",
        ]
    )

    for batch in chunk_list(recording_ids, 25):
        recording_ids_param = ";".join(batch)

        low_level_response = session.get(
            f"{base_url}/low-level",
            headers=MUSICBRAINZ_HEADERS,
            params={"recording_ids": recording_ids_param, "features": low_level_feature_list},
            timeout=30,
        )
        if not low_level_response.ok:
            raise_api_error(low_level_response, "AcousticBrainz bulk low-level request")
        low_level_payload = low_level_response.json()

        high_level_response = session.get(
            f"{base_url}/high-level",
            headers=MUSICBRAINZ_HEADERS,
            params={"recording_ids": recording_ids_param},
            timeout=30,
        )
        if not high_level_response.ok:
            raise_api_error(high_level_response, "AcousticBrainz bulk high-level request")
        high_level_payload = high_level_response.json()

        for mbid in batch:
            normalized_mbid = mbid.lower()
            low_level_entry = low_level_payload.get(normalized_mbid, {}).get("0", {})
            high_level_entry = high_level_payload.get(normalized_mbid, {}).get("0", {})
            extracted = extract_acousticbrainz_features(normalized_mbid, low_level_entry, high_level_entry)
            if extracted:
                features_by_mbid[normalized_mbid] = extracted

    return features_by_mbid


def load_public_metrics():
    public_df = pd.read_csv(PUBLIC_DATASET_PATH)
    required_columns = ["title", "artist", "billboard_rank", *PUBLIC_COLUMNS.keys()]
    missing_columns = [column for column in required_columns if column not in public_df.columns]
    if missing_columns:
        raise ValueError(f"Public dataset is missing required columns: {missing_columns}")

    public_df = public_df[required_columns].copy()
    return public_df.rename(columns=PUBLIC_COLUMNS)



def fill_missing_public_metrics(df):
    df = df.copy()
    public_metric_columns = [
        "tempo_from_public_dataset",
        "danceability_from_public_dataset",
        "acousticness",
        "speechiness",
        "duration_minutes",
    ]
    reference_columns = [
        "average_loudness",
        "dynamic_complexity",
        "danceable_probability",
        "happy_probability",
        "sad_probability",
        "relaxed_probability",
        "party_probability",
    ]

    donors = df[df[public_metric_columns].notna().all(axis=1)].copy()
    if donors.empty:
        raise ValueError("No complete rows are available to fill missing public metrics.")

    scales = donors[reference_columns].std().replace(0, 1).fillna(1)

    for idx, row in df.iterrows():
        if row[public_metric_columns].notna().all():
            continue

        distances = (((donors[reference_columns] - row[reference_columns]) / scales) ** 2).sum(axis=1) ** 0.5
        nearest = donors.loc[distances.idxmin()]

        for column in public_metric_columns:
            if pd.isna(df.at[idx, column]):
                df.at[idx, column] = nearest[column]

    for column in public_metric_columns:
        if df[column].isna().any():
            df[column] = df[column].fillna(donors[column].median())

    return df


# =========================
# FETCH DATA
# =========================
all_data = []

for song in songs:
    mb_recording = search_musicbrainz_recording(song["title"], song["artist"], release_year=2019)

    data = {
        "rank": song["rank"],
        "title": song["title"],
        "artist": song["artist"],
        "musicbrainz_recording_id": None,
        "musicbrainz_title": None,
        "musicbrainz_artists": None,
        "musicbrainz_score": None,
        "acousticbrainz_found": False,
    }

    if mb_recording:
        data.update(
            {
                "musicbrainz_recording_id": mb_recording.get("id"),
                "musicbrainz_title": mb_recording.get("title"),
                "musicbrainz_artists": ", ".join(
                    artist_credit.get("name", "")
                    for artist_credit in mb_recording.get("artist-credit", [])
                    if isinstance(artist_credit, dict)
                ),
                "musicbrainz_score": mb_recording.get("score"),
            }
        )

    all_data.append(data)
    time.sleep(1.1)

acousticbrainz_features_by_mbid = fetch_acousticbrainz_bulk(
    [
        row["musicbrainz_recording_id"]
        for row in all_data
        if row["musicbrainz_recording_id"]
    ]
)

for row in all_data:
    mbid = row.get("musicbrainz_recording_id")
    if not mbid:
        continue

    acousticbrainz_features = acousticbrainz_features_by_mbid.get(mbid.lower())
    if acousticbrainz_features:
        row["acousticbrainz_found"] = True
        row.update(acousticbrainz_features)

# =========================
# SAVE DATASET
# =========================
df = pd.DataFrame(all_data)
df = df[df["acousticbrainz_found"]].copy()
numeric_columns = df.select_dtypes(include="number").columns.tolist()
df = df[["title", "artist", *numeric_columns]]
df = df.rename(columns=COLUMN_RENAMES)

df = df.merge(
    load_public_metrics(),
    on=["title", "artist", "billboard_rank"],
    how="left",
)
df = fill_missing_public_metrics(df)

column_order = [
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
df = df[column_order].copy()

if int(df.isna().sum().sum()) != 0:
    raise ValueError("Output dataset still contains missing values.")

output_path = Path(__file__).with_name("acousticbrainz_2019_dataset.csv")
df.to_csv(output_path, index=False)

print(f"Dataset created successfully: {output_path}")
