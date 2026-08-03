from __future__ import annotations

import json
import os
import sqlite3
import sys
import types
import tempfile
from pathlib import Path
from pprint import pformat

import database_interaction as db

if "app" not in sys.modules:
    sys.modules["app"] = types.ModuleType("app")

import response_table_interaction as rti


def banner(title: str) -> None:
    print()
    print("=" * 18 + f" {title} " + "=" * 18)


def format_value(value):
    if isinstance(value, (bytes, bytearray)):
        try:
            return rti.return_from_serial(value)
        except Exception:
            return value
    if isinstance(value, tuple):
        return tuple(format_value(item) for item in value)
    if isinstance(value, list):
        return [format_value(item) for item in value]
    return value


def print_result(label: str, value) -> None:
    print(f"{label}:")
    print(pformat(format_value(value), sort_dicts=False))


def run_case(name: str, fn, *args, **kwargs):
    banner(name)
    if args:
        print_result("args", args)
    if kwargs:
        print_result("kwargs", kwargs)
    try:
        result = fn(*args, **kwargs)
    except Exception as exc:
        print(f"raised {type(exc).__name__}: {exc}")
        return None
    else:
        print_result("result", result)
        return result


def make_sample_quiz_folder(base_dir: Path) -> Path:
    quiz_dir = base_dir / "testing_quiz"
    quiz_dir.mkdir(parents=True, exist_ok=True)

    quiz_payload = {
        "title": "Sample Career Quiz",
        "categories": [
            {
                "items": [
                    {"id": "wu2k8f4", "text": "What is your preferred work style?"},
                    {"id": "umdk5o3", "text": "What major area interests you most?"},
                    {"id": "5u83jdb", "text": "Where do you want to live after graduation?"},
                ]
            }
        ],
    }
    (quiz_dir / "pjo4roy.json").write_text(json.dumps(quiz_payload, indent=2), encoding="utf-8")
    return quiz_dir


def make_sample_lookup_csv(base_dir: Path) -> Path:
    csv_path = base_dir / "question_keyword_lookup.csv"
    csv_path.write_text(
        "\n".join(
            [
                "topic,question_a,question_b,question_c",
                "career,id1,id2,id3",
                "resume,id4,id5,id6",
                "majors,id7,id8,id9",
            ]
        ),
        encoding="utf-8",
    )
    return csv_path


def seed_database(db_path: Path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    db.user_responses(cur)
    cur.execute(
        """
        CREATE TABLE USER_RESPONSE (
            u_ID TEXT NOT NULL UNIQUE,
            num_completed_quizzes INT,
            quizzes_to_do TEXT,
            completed_quizzes TEXT,
            user_answers TEXT
        )
        """
    )

    canonical_rows = [
        (
            "1",
            1,
            rti.serialize(["pjo4roy", "605ab9c6-4087-496f-b0f9-03e736387715"]),
            rti.serialize([("pjo4roy", 3)]),
            rti.serialize(
                [
                    ("clippn2", "m36a7h0", "HI"),
                    ("zaxz8fd", "qhlk9ks", "c"),
                    ("wu2k8f4", "t2u0y1r", "HELLO"),
                ]
            ),
        ),
        (
            "2",
            2,
            rti.serialize(["pjo4roy"]),
            rti.serialize([("pjo4roy", 3), ("605ab9c6-4087-496f-b0f9-03e736387715", 2)]),
            rti.serialize(
                [
                    ("wu2k8f4", "u1a", "Yes"),
                    ("umdk5o3", "u2b", "CEMS"),
                    ("5u83jdb", "u3c", "Burlington"),
                    ("clippn2", "u4d", "Maybe"),
                    ("zaxz8fd", "u5e", "No"),
                ]
            ),
        ),
    ]

    legacy_rows = [
        (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
        )
        for row in canonical_rows
    ]

    cur.executemany(
        """
        INSERT INTO USER_RESPONSES (
            u_ID, num_completed_quizzes, quizzes_assigned, quizzes_completed, quiz_response_answers
        ) VALUES (?, ?, ?, ?, ?)
        """,
        canonical_rows,
    )
    cur.executemany(
        """
        INSERT INTO USER_RESPONSE (
            u_ID, num_completed_quizzes, quizzes_to_do, completed_quizzes, user_answers
        ) VALUES (?, ?, ?, ?, ?)
        """,
        legacy_rows,
    )

    conn.commit()
    conn.close()


def fetch_table(db_path: Path, table_name: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name} ORDER BY u_ID")
    rows = cur.fetchall()
    conn.close()
    return rows


def main():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        db_path = tmp_path / "career_quiz_test.db"
        quiz_dir = make_sample_quiz_folder(tmp_path)
        make_sample_lookup_csv(tmp_path)
        seed_database(db_path)

        def temp_connecting_to_sql():
            conn = sqlite3.connect(db_path)
            return conn, conn.cursor()

        rti.connecting_to_sql = temp_connecting_to_sql

        banner("DATABASE SETUP")
        print_result("USER_RESPONSES", fetch_table(db_path, "USER_RESPONSES"))
        print_result("USER_RESPONSE", fetch_table(db_path, "USER_RESPONSE"))

        banner("SERIALIZATION HELPERS")
        sample_list = ["pjo4roy", "605ab9c6-4087-496f-b0f9-03e736387715"]
        serialized = run_case("serialize", rti.serialize, sample_list)
        if serialized is not None:
            run_case("return_from_serial", rti.return_from_serial, serialized)

        banner("JSON PARSING")
        run_case("_json_data_convert", rti._json_data_convert, rti.TEST_STRING_TWO)

        banner("CONNECTION")
        conn, cur = run_case("connecting_to_sql", rti.connecting_to_sql) or (None, None)
        if conn is not None:
            conn.close()

        banner("DB MUTATION HELPERS")
        run_case("_increment_quiz_ctr", rti._increment_quiz_ctr, "1")
        print_result("USER_RESPONSE after _increment_quiz_ctr", fetch_table(db_path, "USER_RESPONSE"))
        run_case("_move_quiz_id_todo_cmp", rti._move_quiz_id_todo_cmp, "1", "pjo4roy", 3)
        print_result("USER_RESPONSE after _move_quiz_id_todo_cmp", fetch_table(db_path, "USER_RESPONSE"))
        run_case("_append_answers", rti._append_answers, "1", [("wu2k8f4", "t2u0y1r", "HELLO")])
        print_result("USER_RESPONSE after _append_answers", fetch_table(db_path, "USER_RESPONSE"))
        run_case("quiz_complete", rti.quiz_complete, rti.TEST_STRING_TWO)
        print_result("USER_RESPONSE after quiz_complete", fetch_table(db_path, "USER_RESPONSE"))

        banner("LOOKUP HELPERS")
        old_cwd = Path.cwd()
        os.chdir(tmp_path)
        try:
            run_case("csv_lookup_to_list", rti.csv_lookup_to_list, "career")
            run_case("check_user_lookup_status", rti.check_user_lookup_status, "admin-1", "1")
            run_case("findall_users_cmp_quiz", rti.findall_users_cmp_quiz, ["1", "2"], "pjo4roy")
            run_case("get_user_response_to_quiz", rti.get_user_response_to_quiz, "1", "pjo4roy")
            run_case("get_user_responses_of_question_id", rti.get_user_responses_of_question_id, "wu2k8f4", ["1", "2"])
            run_case("get_users_completed_quiz_quiz_id", rti.get_users_completed_quiz_quiz_id, ["1", "2"], "pjo4roy")
            run_case("lookup_kw_arg_on_user_set", rti.lookup_kw_arg_on_user_set, "career", ["1", "2"])
            run_case("lookup_user_todo_completed_quizzes", rti.lookup_user_todo_completed_quizzes, "1")
        finally:
            os.chdir(old_cwd)

        banner("QUIZ TRANSLATORS")
        test_answers = [
            ("wu2k8f4", "t2u0y1r", "HELLO"),
            ("umdk5o3", "43zaysu", "Dragon Fruit"),
            ("5u83jdb", "umo3d5g", "VT"),
        ]
        run_case("quiz_id_to_quiz_title_translator", rti.quiz_id_to_quiz_title_translator, "pjo4roy", str(quiz_dir))
        run_case("question_id_to_text_translator", rti.question_id_to_text_translator, "pjo4roy", test_answers, str(quiz_dir))

        banner("GENERIC QUERY")
        run_case(
            "__generic_query_response",
            rti.__generic_query_response,
            temp_connecting_to_sql,
            "SELECT quizzes_assigned FROM USER_RESPONSES WHERE u_ID = ?",
            lambda row: row,
            "UPDATE USER_RESPONSES SET quizzes_assigned = ? WHERE u_ID = ?",
            ("[]", "1"),
            ["1"],
            False,
        )


if __name__ == "__main__":
    main()
