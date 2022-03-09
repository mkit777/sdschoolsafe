import asyncio
from time import sleep
from pyppeteer import launch
from extract import do_extract_questions
from main import load_db, find_answer


class Opts:
  def __init__(self) -> None:
    self.username = None
    self.password = None

OPT_MAP = {
  'A': 1,
  'B': 2,
  'C': 3,
  'D': 4,
}


async def single_select(page, block, b_no, option):
  print(block, b_no, option)
  await page.click(f'body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.paper-content > .title-contain:nth-child({block + 1}) > .question-contain:nth-child({b_no + 2}) > .single-choice uni-label:nth-child({OPT_MAP[option]})')

async def multi_select(page, block, b_no, options):
  print(block, b_no, options)
  for option in options:
    await page.click(f'body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.paper-content > .title-contain:nth-child({block + 1}) > .question-contain:nth-child({b_no + 2}) > .multiple-choice uni-label:nth-child({OPT_MAP[option]})')

async def judge_select(page, block, b_no, option):
  print(block, b_no, option)
  await page.click(f'body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.paper-content > .title-contain:nth-child({block + 1}) > .question-contain:nth-child({b_no + 2}) > .true-false-choice uni-label:nth-child({OPT_MAP[option]})')


async def main(opts: Opts):
  db = load_db('./data.xlsx')

  browser = await launch(devtools=True, args=['--disable-infobars'])
  page = await browser.newPage()
  await page.evaluateOnNewDocument('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
  # 打开网页
  await page.goto('http://exam.sdschoolsafe.cn:7007/')
  page.waitForSelector('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view.input-content.margin-bottom-1.margin-top-24-px > div > div > input')
  
  # 选择学校
  await page.click('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view.input-content.margin-bottom-1.margin-top-24-px > div > div > input')
  sleep(1)
  await page.click('body > div.el-select-dropdown.el-popper > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap.el-scrollbar__wrap--hidden-default > ul > li:nth-child(88)')
  sleep(1)
  # 输入账号
  await page.type('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view:nth-child(2) > uni-view:nth-child(1) > uni-input > div > input', opts.username)
  sleep(1)
  # 输入密码
  await page.type('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view:nth-child(2) > uni-view:nth-child(2) > input[type="password"]',  opts.password)
  sleep(1)
  # 确认
  await page.click("body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-button")
  page.waitForSelector("body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view:nth-child(5) > uni-view > uni-view")
  sleep(3)
  # 点击开始
  await page.click('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view:nth-child(5) > uni-view > uni-view')
  page.waitForSelector('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view:nth-child(5) > uni-view > uni-view')
  sleep(1)
  # 确定
  await page.click('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.uni-popup.center > uni-view:nth-child(2) > uni-view > uni-view > uni-view.paper-foot.margin-top-1.display-flex.flex-justify-content-space-between > uni-button:nth-child(2)')
  page.waitForSelector('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.uni-popup.center > uni-view:nth-child(2) > uni-view > uni-view > uni-view.paper-foot.margin-top-1.display-flex.flex-justify-content-space-between > uni-button:nth-child(2)')
  sleep(1)
  # 获取内容
  content = await page.content()

  questions = do_extract_questions(content)
  
  for q in questions:
    an = find_answer(db, q)
    if q.type == '单选题':
      await single_select(page, q.block, q.block_no, an[0][0])
    elif q.type == '多选题':
      await multi_select(page, q.block, q.block_no, [item[0] for item in an])
    elif q.type == '判断题':
      await judge_select(page, q.block, q.block_no, an[0][0])
    sleep(1)
  input('enter any key.')
  await browser.close()


opts = Opts()
opts.username = ''
opts.password = ''


asyncio.get_event_loop().run_until_complete(main(opts))