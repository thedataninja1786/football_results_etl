class FootballAPIConfig:
    API_KEY = "API_KEY"
    HOST = "api-football-v1.p.rapidapi.com"
    DATE_FORMAT = "%Y-%m-%d"
    DATA_WINDOW = 5
    DATA_SHIFT = 1
    BASE_URL = "https://api-football-v1.p.rapidapi.com/fixtures/date/"
    UNICODE_MAPPING = {
                        "u00e9": "e",
                        "u00e8": "e",
                        "u00e1": "a",
                        "u00e0": "a",
                        "u00e2": "a",
                        "u00f3": "o",
                        "u00f3": "n",
                        "u015e": "s",
                        "u0131": "i",
                        "u00e7": "c",
                        "u00f6": "o",
                        "u00fc": "u",
                        "u0105": "a",
                        "u0142": "l",
                        "u00f1": "n",
                        "u00e" : "e"
    }

class SchemaConfigs:
    DATABASE_NAME = "football_results.db"
    TABLE_NAME = "fixtures"
    TABLE_DATA = {
                    "fixture_id": "INTEGER",
                    "event_timestamp":"TEXT",
                    "event_date":"DATE",
                    "league_id":"INTEGER",
                    "homeTeam_id":"INTEGER",
                    "awayTeam_id":"INTEGER",
                    "homeTeam":"TEXT",
                    "awayTeam":"TEXT",
                    "status": "TEXT",
                    "statusShort":"TEXT",
                    "goalsHomeTeam":"INTEGER",
                    "goalsAwayTeam":"INTEGER",
                    "halftime_score":"TEXT",
                    "final_score":"TEXT",
                    "penalty":"INTEGER",
                    "elapsed":"TEXT",
                    "firstHalfStart":"TEXT",
                    "secondHalfStart":"TEXT",
                    "processing_timestamp":"TEXT",
                    "round":"TEXT"
        }