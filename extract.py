from enum import EnumMeta
from bs4 import BeautifulSoup
import re


class Question:
  def __init__(self) -> None:
    self.block = None
    self.no = None
    self.block_no = None
    self.question = None
    self.q = None
    self.type = None
    self.choices = []

  def __str__(self) -> str:
      return f'{self.type} {self.no} {self.question} {" ".join(self.choices)}'

  def __repr__(self) -> str:
      return self.__str__()


def do_extract_questions(content):
  soup = BeautifulSoup(content, features='html.parser')
  questions = []
  blocks = soup.select('.title-contain')
  for (block_idx, block) in enumerate(blocks):
    type = block.select_one('.title.exam-qustion-content').getText().strip()
    questions_doc = block.select('.question-contain')
    for (b_no, question_doc) in enumerate(questions_doc):
      question_title = question_doc.select_one('.exam-qustion-content').get_text()
      parted = re.split('\s+', question_title)
      # 序号
      no = parted[0]
      # 问题
      title = ''.join(parted[1:])

      q = Question()
      q.block = block_idx
      q.block_no = b_no
      q.no = no
      q.question = title
      q.type = type
      q.q = re.sub(r'[^\u4e00-\u9fa5]','' ,title)

      # 选项
      if type == '单选题':
        choice_docs = question_doc.select('.question-radio-group .exam-qustion-content')
        for choice_doc in choice_docs:
          choice = re.sub('\s+', '', choice_doc.get_text())
          q.choices.append(choice)
      elif type == '多选题':
        choice_docs = question_doc.select('.question-checkbox-group .exam-qustion-content')
        for choice_doc in choice_docs:
          choice = re.sub('\s+', '', choice_doc.get_text())
          q.choices.append(choice)
      elif type == '判断题':
        choice_docs = question_doc.select('.question-true-false-group .exam-qustion-content')
        for choice_doc in choice_docs:
          choice = re.sub('\s+', '', choice_doc.get_text())
          q.choices.append(choice)
      
      questions.append(q)
  return questions



def extract_questions(path):
  with open(path, encoding='utf-8') as f:
    return do_extract_questions(f)


if __name__ == '__main__':
  questions = extract_questions('./a.html')
  for q in questions:
    print(q)