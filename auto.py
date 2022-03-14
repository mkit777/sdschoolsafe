import asyncio
from calendar import c
from playwright.async_api import async_playwright
from pyrsistent import b
from extract import do_extract_questions
from main import load_db, find_answer
import ddddocr


ocr = ddddocr.DdddOcr(show_ad=False)

class Opts:
  def __init__(self) -> None:
    self.url = 'http://exam.sdschoolsafe.cn:7007'
    self.db = './data.xlsx'
    self.username = None
    self.password = None
    self.school = None

OPT = Opts()

# 修改用户名
OPT.username = ''
# 修改密码
OPT.password = ''
# 修改学校
OPT.school = ''

OPT_MAP = {
  'A': 1,
  'B': 2,
  'C': 3,
  'D': 4,
}

async def init_page(browser):
  page = await browser.new_page()
  js="""
  Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
  """
  await page.add_init_script(js)
  return page

async def select_school(page, school):
  school_input = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view.input-content.margin-bottom-1.margin-top-24-px > div > div > input')
  await school_input.click()
  school_options = page.locator('body > div.el-select-dropdown.el-popper > div.el-scrollbar > div.el-select-dropdown__wrap.el-scrollbar__wrap.el-scrollbar__wrap--hidden-default > ul > li')
  for opt_hd in await school_options.element_handles():
    if (await opt_hd.inner_text()).strip() == '山东科技大学':
        await opt_hd.click()
        break

async def input_username(page, username):
  id_input = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view:nth-child(2) > uni-view:nth-child(1) > uni-input > div > input')
  await id_input.fill(username)


async def input_password(page, password):
  pwd_input = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view:nth-child(2) > uni-view:nth-child(2) > input[type=password]')
  await pwd_input.fill(password)

async def refresh_vrcode(page):
  vrc_img = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view:nth-child(2) > uni-view:nth-child(3) > uni-image > img')
  await vrc_img.click()

async def input_vrcode(page):
  vrc_img = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view:nth-child(2) > uni-view:nth-child(3) > uni-image > img')
  vrc_img = await vrc_img.element_handle()
  vrc_img = await vrc_img.screenshot(path='vrcode.png', type='png')

  res = ocr.classification(vrc_img)
  print(f'vrcode: {res}')
  vrc_input = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-view:nth-child(2) > uni-view:nth-child(3) > uni-view > uni-input > div > input')
  # await vrc_input.fill(res)
  await vrc_input.fill(res)


async def login(page):
  confirm_btn = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view > uni-view.wrapper > uni-button')
  await confirm_btn.click()
  resp = await page.wait_for_event('response')
  ret = await resp.json()
  print(f'loing result: {ret}')
  if ret['code'] == 1:
    return True
  return False
  

async def start_exam(page):
  start_btn = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view:nth-child(5) > uni-view > uni-view')
  await start_btn.click()

async def conform_start(page):
  confirm_btn = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.uni-popup.center > uni-view:nth-child(2) > uni-view > uni-view > uni-view.paper-foot.margin-top-1.display-flex.flex-justify-content-space-between > uni-button:nth-child(2)')
  await confirm_btn.click()


async def single_select(page, b, no_in_b, opt):
  locator = page.locator(f'body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.paper-content > .title-contain:nth-child({b + 1}) > .question-contain:nth-child({no_in_b + 2}) > .single-choice uni-label:nth-child({OPT_MAP[opt]})')
  await locator.click()


async def multi_select(page, b, no_in_b, opts):
 for opt in opts:
    locator = page.locator(f'body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.paper-content > .title-contain:nth-child({b + 1}) > .question-contain:nth-child({no_in_b + 2}) > .multiple-choice uni-label:nth-child({OPT_MAP[opt]})')
    await locator.click()

async def judge_select(page, b, no_in_b, opt):
  locator = page.locator(f'body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.paper-content > .title-contain:nth-child({b + 1}) > .question-contain:nth-child({no_in_b + 2}) > .true-false-choice uni-label:nth-child({OPT_MAP[opt]})')
  await locator.click()


async def save_result(page):
  score_ele = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.uni-popup.center > uni-view:nth-child(2) > uni-view > uni-view > uni-view.display-flex.margin-bottom-1 > uni-view:nth-child(2)')
  score = await score_ele.inner_text()
  print(f'分数 {score}')
  qr_code = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.uni-popup.center > uni-view:nth-child(2) > uni-view > uni-view > uni-view:nth-child(2) > uni-image > img')
  await qr_code.wait_for_element_state('stable')
  await page.screenshot(path='result.png', type='png')


async def submit_paper(page):
  locator = page.locator('body > uni-app > uni-page > uni-page-wrapper > uni-page-body > uni-view > uni-view.paper-foot > uni-button')
  await locator.click()


async def start_paper(page):
  await page.wait_for_selector('.paper-title.exam-qustion-content')
  content = await page.content()
  questions = do_extract_questions(content)

  db = load_db(OPT.db)

  for q in questions:
    an = find_answer(db, q)
    if q.type == '单选题':
      await single_select(page, q.block, q.block_no, an[0][0])
    elif q.type == '多选题':
      await multi_select(page, q.block, q.block_no, [item[0] for item in an])
    elif q.type == '判断题':
      await judge_select(page, q.block, q.block_no, an[0][0])

    await page.wait_for_timeout(200)

async def main():
  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=False, slow_mo=100)
    page = await init_page(browser)

    await page.goto(OPT.url)
    await select_school(page, OPT.school)
    # await page.wait_for_timeout(1000)
    await input_username(page, OPT.username)
    # await page.wait_for_timeout(1000)
    await input_password(page, OPT.password)
    # await page.wait_for_timeout(1000)
    await input_vrcode(page)

    success = await login(page)
      
    if success:
      await start_exam(page)
      await conform_start(page)
      await start_paper(page)
      await submit_paper(page)
      await save_result(page)
    await browser.close()

asyncio.run(main())