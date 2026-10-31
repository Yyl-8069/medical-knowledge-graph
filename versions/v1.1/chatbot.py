from question_classifier import QuestionClassifier
from question_parser import QuestionParser
from answer_search import AnswerSearcher

class Red_Spider:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionParser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sentence):
        classification = self.classifier.classify(sentence)
        queries = self.parser.parser_main(classification)
        answers = self.searcher.search_main(queries)
        return '\n'.join(answers) if answers else '未查到对应图谱信息。'

    def close(self):
        self.searcher.close()

if __name__ == '__main__':
    bot = Red_Spider()
    try:
        while True:
            question = input('用户（q 退出）: ')
            if question.lower() == 'q':
                break
            print(bot.chat_main(question))
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        bot.close()
