from tests.shadow.questions import questions


def run_test():

    print("Shadow Test\n")

    answers = []

    for q in questions:

        print(q["text"])

        for i, option in enumerate(q["options"], start=1):
            print(f"{i}. {option}")

        answer = input("Выберите вариант: ")
        answers.append(answer)

        print()

    print("Спасибо за прохождение теста")
