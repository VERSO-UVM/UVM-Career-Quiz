import pandas as pd
import re

# Object that contains all of a users quiz data the will be displayed on the dashboard
class UserQuizData:
    '''
    # Object that contains all of a users quiz data the will be displayed on the dashboard

    :param u_id: Users ID
    :param completed_quiz_count: Number of quizzes that the user has completed
    :param to_do_str: Titles of quizzes that aren't completed 
    :param completed_str: Titles of quizzes that are completed
    :param answers_str: A users answers to all the completed quizzes
    '''
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

    def parse_tuples(self, raw_str: str):
        '''
        Adds all tuples for completed_quizzes and answers to a list

        :param raw_str: tuples in string form : "(),(),()"

        :returns parsed_list: list of tuples : [(),(),()]
        '''
        matches = re.findall(r"\(([^)]+)\)", raw_str)
        parsed_list = []

        for match in matches:
            parts = match.split(",")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                parsed_list.append((key, val))
        return parsed_list
    
    def get_completed_quiz_names(self) -> list[str]:
        '''
        Gets names of all the quizzes an individual user has completed

        :returns completed_quiz_names: list of completed quiz names
        '''
        completed_quiz_names = []
        for quiz_name in self.completed_quizzes:
            completed_quiz_names.append(quiz_name[0])
        return completed_quiz_names

    def get_uncompleted_quiz_names(self) -> list[str]:
        '''
        gets names of all the quizzes an individual user has NOT taken

        :returns uncompleted_quiz_names: list of uncompleted quiz names
        '''
        uncompleted_quiz_names = []
        for quiz_name in self.quizzes_to_do:
            uncompleted_quiz_names.append(quiz_name)
        return uncompleted_quiz_names

    #------------------------ FUNCTIONS THAT PROBABLY WONT BE USED ONCE DATABASE IS UP ------------------------#

    def parse_answer_tuple(self) -> list[str,str,str]:
        '''
        Parse the quiz and question id into separate indexes

        :param self: tuple in format of : (quiz_id-ques_id, answer)

        :returns: tuple in format of : (quiz_id, ques_id, answer)
        '''
        all_parsed_answers = []
        for answer in self.answers:
            parsed_answer = answer[0].split("-")
            parsed_answer.append(answer[1])
            all_parsed_answers.append(parsed_answer)
        return all_parsed_answers

def load_users_into_objects(file_name):
    '''
    Loads test csv data into UserQuizData objects

    :param file_name: name of csv file

    :returns all_users: list of UserQuizData objects 
    '''
    df = pd.read_csv(file_name)
    
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
#------------------------ FUNCTIONS THAT PROBABLY WONT BE USED ONCE DATABASE IS UP ------------------------#

if __name__ == "__main__":
    # Test Code
    all_users = load_users_into_objects("user_quiz_data.csv")       

    print(all_users[0].get_uncompleted_quiz_names())
