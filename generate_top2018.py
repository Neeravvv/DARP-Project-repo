import time
from pathlib import Path

import pandas as pd
import requests

session = requests.Session()
SOURCE_PATH = Path(__file__).with_name("top2018.csv")
OUTPUT_PATH = Path(__file__).with_name("acousticbrainz_2018_dataset.csv")

MUSICBRAINZ_HEADERS = {
    "User-Agent": "neeravbhuyan@gmail.com"
}

FINAL_COLUMNS = [
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


def raise_api_error(response, context):
    try:
        details = response.json()
    except ValueError:
        details = response.text
    raise requests.exceptions.HTTPError(
        f"{context} failed with status {response.status_code}: {details}",
        response=response,
    )


def load_2018_songs():
    df = pd.read_csv(SOURCE_PATH).copy()
    df = df.reset_index(drop=True)
    df["billboard_rank"] = df.index + 1
    df = df.rename(
        columns={
            "name": "title",
            "artists": "artist",
            "tempo": "tempo_from_public_dataset",
            "danceability": "danceability_from_public_dataset",
            "duration_ms": "duration_ms",
        }
    )
    df["duration_minutes"] = pd.to_numeric(df["duration_ms"], errors="coerce") / 60000.0
    return df[
        [
            "title",
            "artist",
            "billboard_rank",
            "tempo_from_public_dataset",
            "danceability_from_public_dataset",
            "acousticness",
            "speechiness",
            "duration_minutes",
        ]
    ].copy()


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

    highlevel = high_level.get("highlevel", {})

    return {
        "average_loudness": low_level.get("lowlevel", {}).get("average_loudness"),
        "dynamic_complexity": low_level.get("lowlevel", {}).get("dynamic_complexity"),
        "danceable_probability": highlevel.get("danceability", {}).get("all", {}).get("danceable"),
        "happy_probability": highlevel.get("mood_happy", {}).get("all", {}).get("happy"),
        "sad_probability": highlevel.get("mood_sad", {}).get("all", {}).get("sad"),
        "relaxed_probability": highlevel.get("mood_relaxed", {}).get("all", {}).get("relaxed"),
        "party_probability": highlevel.get("mood_party", {}).get("all", {}).get("party"),
    }


def fetch_acousticbrainz_bulk(recording_ids):
    if not recording_ids:
        return {}

    base_url = "https://acousticbrainz.org/api/v1"
    features_by_mbid = {}
    low_level_feature_list = ";".join([
        "lowlevel.average_loudness",
        "lowlevel.dynamic_complexity",
    ])

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


def fill_missing_acoustic_features(df):
    acoustic_columns = [
        "average_loudness",
        "dynamic_complexity",
        "danceable_probability",
        "happy_probability",
        "sad_probability",
        "relaxed_probability",
        "party_probability",
    ]
    public_columns = [
        "tempo_from_public_dataset",
        "danceability_from_public_dataset",
        "acousticness",
        "speechiness",
        "duration_minutes",
    ]

    donors = df[df[acoustic_columns].notna().all(axis=1)].copy()
    if donors.empty:
        raise ValueError("No complete rows are available to fill missing AcousticBrainz metrics.")

    scales = donors[public_columns].std().replace(0, 1).fillna(1)

    for idx, row in df.iterrows():
        if row[acoustic_columns].notna().all():
            continue

        distances = (((donors[public_columns] - row[public_columns]) / scales) ** 2).sum(axis=1) ** 0.5
        nearest = donors.loc[distances.idxmin()]
        for column in acoustic_columns:
            if pd.isna(df.at[idx, column]):
                df.at[idx, column] = nearest[column]

    return df


def build_2018_dataset():
    songs_df = load_2018_songs()
    all_data = []

    for song in songs_df.to_dict("records"):
        mb_recording = search_musicbrainz_recording(song["title"], song["artist"], release_year=2018)
        row = dict(song)
        row["musicbrainz_recording_id"] = mb_recording.get("id") if mb_recording else None
        all_data.append(row)
        time.sleep(1.1)

    acousticbrainz_features_by_mbid = fetch_acousticbrainz_bulk(
        [row["musicbrainz_recording_id"] for row in all_data if row["musicbrainz_recording_id"]]
    )

    for row in all_data:
        mbid = row.get("musicbrainz_recording_id")
        extracted = acousticbrainz_features_by_mbid.get(mbid.lower()) if mbid else None
        if extracted:
            row.update(extracted)

    df = pd.DataFrame(all_data)
    df = fill_missing_acoustic_features(df)
    df = df[FINAL_COLUMNS].copy()

    if int(df.isna().sum().sum()) != 0:
        raise ValueError("Output dataset still contains missing values.")

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Dataset created successfully: {OUTPUT_PATH}")
    print(f"Rows written: {len(df)}")


if __name__ == "__main__":
    build_2018_dataset()
