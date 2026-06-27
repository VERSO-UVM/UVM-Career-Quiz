import pandas as pd
import re

class UserQuizData:

    def __init__(
        self,
        u_id: str,
        completed_quiz_count: int,
        to_do_str: str,
        completed_str: str,
        answers_str: str,
    ):
        self.u_id = u_id
        self.completed_quiz_count = completed_quiz_count
        self.quizzes_to_do: list[str] = to_do_str.split(",")

        self.completed_quizzes: list[tuple[str, str]] = self.parse_tuples(
            completed_str
        )
        self.answers: list[tuple[str, str]] = self.parse_tuples(answers_str)
    
    # String representation of UserDataObject
    def __repr__(self) -> str:
        return (
            f"  u_id='{self.u_id}',\n"
            f"  completed_quiz_count={self.completed_quiz_count},\n"
            f"  quizzes_to_do={self.quizzes_to_do},\n"
            f"  completed_quizzes={self.completed_quizzes},\n"
            f"  answers={self.answers}\n"
        )

    # Adds all tuples for completed_quizzes and answers to a list "(),(),()" --> [(),(),()]
    def parse_tuples(self, raw_str: str):
        matches = re.findall(r"\(([^)]+)\)", raw_str)
        parsed_list = []

        for match in matches:
            parts = match.split(",")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                parsed_list.append((key, val))
        return parsed_list
    
    # gets names of all the quizzes an individual user has completed
    def get_completed_quiz_names(self) -> list[str]:
        completed_quiz_names = []
        for quiz_name in self.completed_quizzes:
            completed_quiz_names.append(quiz_name[0])
        return completed_quiz_names

    # gets names of all the quizzes an individual user has NOT taken
    def get_uncompleted_quiz_names(self) -> list[str]:
        uncompleted_quiz_names = []
        for quiz_name in self.quizzes_to_do:
            uncompleted_quiz_names.append(quiz_name)
        return uncompleted_quiz_names


    # (quiz_id-ques_id, answer) --> (quiz_id, ques_id, answer)
    def parse_answer_tuple(self) -> list[str,str,str]:
        all_parsed_answers = []
        for answer in self.answers:
            parsed_answer = answer[0].split("-")
            parsed_answer.append(answer[1])
            all_parsed_answers.append(parsed_answer)
        return all_parsed_answers

# Loads csv data into UserQuizData objects
def load_users_into_objects(filename):
    df = pd.read_csv(filename)
    
    all_users = [
        UserQuizData(
            u_id=row.u_id,
            completed_quiz_count=row.num_completed_quizzes, 
            to_do_str=row.quizzes_to_do,
            completed_str=row.quizzes_completed,
            answers_str=row.user_answers,
        )
        for row in df.itertuples(index=False)
    ]
    return all_users


if __name__ == "__main__":

    all_users = load_users_into_objects("user_quiz_data.csv")       

    print(all_users[0].get_uncompleted_quiz_names())
