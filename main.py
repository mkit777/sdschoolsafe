from numpy import argmax
import pandas as pd
from thefuzz import fuzz
from extract import Question, extract_questions
import re

def load_db(path):
  db = dict()

  df0 = pd.read_excel(path, sheet_name=0)
  df0.columns=['aa', 'bb', 'cc', 'question', 'a', 'b', 'c', 'd', 'ret', 'ee', 'ff', 'gg', 'gg']
  db['单选题'] = df0

  df1 = pd.read_excel(path, sheet_name=1)
  df1.columns = ['aa', 'bb', 'cc', 'question', 'a', 'b', 'c', 'd', 'ret', 'ee', 'ff', 'gg']
  db['多选题'] = df1

  df2 = pd.read_excel(path, sheet_name=2)
  df2.columns = ['aa', 'bb', 'cc', 'question', 'a', 'b', 'ret', 'gg', 'jj', 'ee', 'ff']
  db['判断题'] = df2
  return db

def find_answer(db, q: Question):
  db = db[q.type]
  ratios = []
  for (idx, ques) in enumerate(db['question']):
    ques = re.sub(r'[^\u4e00-\u9fa5]','',ques)
    ratio = fuzz.partial_ratio(ques, q.q)
    ratios.append(ratio)
  best_match_idx = argmax(ratios)

  if q.type == '单选题':
    row = db.iloc[best_match_idx]
    return ((row.ret, row[str.lower(row.ret)]), )
  elif q.type == '多选题':
    row = db.iloc[best_match_idx]
    opts = []
    for ch in row.ret:
      opts.append((ch, row[str.lower(ch)]))
    return tuple(opts)
  elif q.type == '判断题':
    row = db.iloc[best_match_idx]
    return ((row.ret, row[str.lower(row.ret)]), )

if __name__ == '__main__':
  questions = extract_questions('./paper.html')
  db = load_db('./data.xlsx')

  with open('result.txt', 'w', encoding='utf-8') as f:
    for question in questions:
      an = find_answer(db, question)
      f.write(f'{question.no} { "".join([item[0] for item in an])}\t  { ",".join([str(item[0]) +"." + str(item[1]) for item in an]) }\r\n')
