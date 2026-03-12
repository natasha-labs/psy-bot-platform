from tests.registry import AVAILABLE_TESTS
import importlib


def choose_test():

    print("Доступные тесты:\n")

    tests = list(AVAILABLE_TESTS.keys())

    for i, key in enumerate(tests, start=1):
        print(f"{i}. {AVAILABLE_TESTS[key]['title']}")

    choice = int(input("\nВыберите тест: "))

    return tests[choice - 1]


def run_test():

    test_key = choose_test()

    module_name = AVAILABLE_TESTS[test_key]["module"]

    module = importlib.import_module(module_name)

    questions = module.questions

    print("\nНачинаем тест\n")

    answers = []

    for q in questions:

        print(q["text"])

        for i, option in enumerate(q["options"], start=1):
            print(f"{i}. {option}")

        answer = input("Выберите вариант: ")
        answers.append(answer)

        print()

    print("Спасибо за прохождение теста")
