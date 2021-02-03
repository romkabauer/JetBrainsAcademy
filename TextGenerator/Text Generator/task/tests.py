from hstest.stage_test import StageTest
from hstest.test_case import TestCase
from hstest.check_result import CheckResult
from random import randint
import re

PATH = "test/corpus.txt"

def tokenize():
    with open(PATH, "r", encoding="utf-8") as f:
        return f.read().split()

class TextGeneratorTests(StageTest):
    def generate(self):
        test_input1 = PATH + "\nexit\n"
        test_input2 = PATH + "\n0\n1\n2\n-1\nten\n43256236577\nexit\n"
        test_input3 = PATH + "\n" + "\n".join(
            [str(randint(0, 300000)) for _ in range(10)]) + "\nexit\n"

        return [
            TestCase(stdin=test_input1, attach=test_input1),
            TestCase(stdin=test_input2, attach=test_input2),
            TestCase(stdin=test_input3, attach=test_input3)
        ]

    def check(self, reply, attach):
        try:
            corpus = tokenize()
        except FileNotFoundError:
            return CheckResult.wrong("File not found at {}. Make sure the file "
                                     "has not been deleted or moved.".format(PATH))

        # check output format
        if not reply:
            return CheckResult.wrong("""The output cannot be empty!
            Make sure to output the results of your program!""")

        lines = re.split("\n+", reply)
        if len(lines) < 3:
            return CheckResult.wrong("The output should consist of at least 3 lines!")

        stats, res = lines[0:3], lines[3:-1]

        # check corpus statistics
        try:
            if "Corpus statistics" not in stats[0]:
                return CheckResult.wrong(
                    "The first line of the output should be "
                    "a header called 'Corpus statistics'")
            if (cres := int(stats[1].split()[-1])) != (clen := len(corpus)):
                if cres > clen:
                    return CheckResult.wrong(
                        "The number of outputted tokens is "
                        "greater then the number of tokens in the corpus. You should tokenize "
                        "the corpus by whitespaces and leave punctuation marks intact.")
                else:
                    return CheckResult.wrong(
                        "The number of outputted tokens is smaller then "
                        "the number of tokens in the corpus. You should tokenize "
                        "the corpus by whitespaces and leave punctuation marks intact.")
            if (cres := int(stats[2].split()[-1])) != (clen := len(set(corpus))):
                if cres > clen:
                    return CheckResult.wrong(
                        "The number of outputted unique tokens is greater then "
                        "the number of unique tokens in the corpus. Make sure that "
                        "every unique token is counted only once.")
                else:
                    return CheckResult.wrong(
                        "The number of outputted unique tokens is smaller then "
                        "the number of unique tokens in the corpus. "
                        "Every unique token should be counted only once, but capitalization does matter.")
        except IndexError:
            return CheckResult.wrong("Invalid format. Make sure 'Corpus statistics' is in a valid format.")
        except ValueError:
            return CheckResult.wrong(
                "Value error. Make sure that each line in the "
                "corpus statistics section ends with an integer.")

        # see if for every inputted seed there is an output present
        seeds = attach.split('\n')[1:-2]
        if len(seeds) != len(res):
            return CheckResult.wrong(
                "The number of inputted seeds should match the "
                "number of outputted results from the corpus.")

        # check every 'query'
        for j, elem in enumerate(seeds):
            try:
                i = int(elem)
                if corpus[i] != res[j]:
                    return CheckResult.wrong(
                        "Incorrect output ({0}). An other output "
                        "({1}) is expected at index {2}".format(res[i], corpus[i], i))
            except IndexError:
                if ("Index Error" or "index error" or "Index error" or "indexerror"
                    or "IndexError") not in res[j]:
                    return CheckResult.wrong(
                        "Error messages should contain the types of errors "
                        "(Index Error, Type Error, etc.)")
            except (ValueError, TypeError):
                if ("Type Error" or "type error" or "Type error"
                    or "typeerror" or "TypeError") not in res[j]:
                    return CheckResult.wrong(
                        "Error messages should contain the types of errors "
                        "(Index Error, Type Error, etc.)")

        return CheckResult.correct()


if __name__ == '__main__':
    TextGeneratorTests('text_generator.text_generator').run_tests()
