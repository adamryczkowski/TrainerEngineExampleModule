from module import randomize_question, Settings, check_answer, AnswerType, calc_score, QuestionType, _infer_skills


class Trainer:
    settings: Settings
    positive_skills: list[str]
    negative_skills: list[str]

    def __init__(self, settings: Settings = None, positive_skills: list[str] = None, negative_skills: list[str] = None):
        if settings is None:
            settings = Settings()
        if positive_skills is None:
            positive_skills = []
        if negative_skills is None:
            negative_skills = []

        self.settings = settings
        self.positive_skills = positive_skills
        self.negative_skills = negative_skills

    def ask_manual_question(self, operand1:int, operator:str, operand2:int):
        if operator == "+":
            answer = operand1 + operand2
        elif operator == "-":
            answer = operand1 - operand2
        else:
            raise ValueError(f"Unknown operator: {operator}")

        question = QuestionType(first_operand=operand1, second_operand=operand2, operator=operator)

        correct = AnswerType(answer=answer)

        skills = _infer_skills(question, correct)

        self._ask_question(question, correct, skills)


    def describe_the_skills(self):
        if len(self.positive_skills) == 0 and len(self.negative_skills) == 0:
            print("Asking question without any constraints.")
            return
        print("The questions is randomized with the following constraints:")
        for skill in self.positive_skills:
            if skill == "twodigit":
                print(f" - The answer and operands are all two-digit number.")
            elif skill == "subtract":
                print(f" - The question will be a subtraction.")
            elif skill == "overflow10":
                print(f" - The sum of the last digits will be greater than 10, requiring a carry.")
            elif skill == "underflow10":
                print(f" - The unit of the first operand is smaller than unit of the second, requiring a borrow.")
            elif skill == "negative":
                print(f" - The question will be a subtraction with a negative result.")
            else:
                raise ValueError(f"Unknown skill: {skill}")
        for skill in self.negative_skills:
            if skill == "twodigit":
                print(f" - All numbers are one-digit.")
            elif skill == "subtract":
                print(f" - The question will be an addition.")
            elif skill == "overflow10":
                print(f" - The sum of the last digits will be less than 10, not requiring a borrow.")
            elif skill == "underflow10":
                print(
                    f" - The unit of the first operand is greater or equal than unit of the second, not requiring a carry.")
            elif skill == "negative":
                print(f" - All numbers are positive.")
            else:
                raise ValueError(f"Unknown skill: {skill}")

    def _ask_question(self, question:QuestionType, correct: AnswerType, skills: list[str]):
        print(f"Question: {question.first_operand} {question.operator} {question.second_operand} = ?")
        # Asks for answer as integer
        answer_int = int(input("Answer: "))
        answer = AnswerType(answer_int)

        judgement = check_answer(question, answer, correct, skills)

        scoring = calc_score(judgement, correct, skills)

        for skill, (score, total) in scoring.items():
            print(f"Judgement in {skill}: {int(score)} out of {int(total)} ({score/total * 100:.0f}%)")

        if judgement.score_in_sign is not None and judgement.score_in_sign < 0.5:
            print("The sign was wrong.")
        if judgement.score_in_ordering is not None and judgement.score_in_ordering < 0.5:
            print(
                f"You mistook the order of the operands. You answered {question.second_operand} {question.operator} {question.first_operand} instead.")

        if judgement.score_in_operand is not None and judgement.score_in_operand < 0.5:
            if question.operator == "+":
                print(
                    f"You mistook the operands. I asked for ADDITION (+) and you answered {question.first_operand} - {question.second_operand} instead.")
            else:
                print(
                    f"You mistook the operands. I asked for SUBTRACTION (-) and you answered {question.first_operand} + {question.second_operand} instead.")

        if -9 <= correct.answer <= 9:
            if judgement.score_in_units < 0.5:
                print(f"You made mistake. The correct answer is {correct.answer}.")
            else:
                print(f"Correct!")
        else:

            if judgement.score_in_units < 0.5:
                if judgement.score_in_tens is not None and judgement.score_in_tens < 0.5:
                    print(f"You gave a wrong answer. The correct is {correct.answer}.")
                else:
                    print(f"You made mistake in the units. The correct answer is {correct.answer}.")
            else:
                if judgement.score_in_tens is not None and judgement.score_in_tens < 0.5:
                    print(f"You made mistake in the tens. The correct answer is {correct.answer}.")
                else:
                    if correct.answer == answer_int:
                        print(f"Correct!")


    def ask_question(self):
        """Asks the question using the console"""
        question, correct, skills = randomize_question(self.positive_skills, self.negative_skills, self.settings)
        if question is None:
            print("No questions available.")
            return
        self._ask_question(question, correct, skills)



def test1():
    # trainer = Trainer(positive_skills=["overflow10", "underflow10", "twodigit"])
    trainer = Trainer(positive_skills=[])
    trainer.ask_manual_question(2, "+", 3)
    trainer.describe_the_skills()
    while True:
        trainer.ask_question()


if __name__ == '__main__':
    test1()
