import asyncio
from pyppeteer import launch


async def main():
    browser = await launch(options={'args': ['--no-sandbox']})
    page = await browser.newPage()
    url = 'https://www.koolearn.com/ke/kaoyan2'
    await page.goto(url=url)
    path = os.getcwd()
    await page.screenshot(path=path + '/screenshot/考研.png')
    # await page.pdf(path='test_pdf.pdf')

    # 在网页上执行js 脚本
    dimensions = await page.evaluate(pageFunction='''() => {
                return {
                    width: document.documentElement.clientWidth,    // 页面宽度
                    height: document.documentElement.clientHeight,  // 页面高度
                    deviceScaleFactor: window.devicePixelRatio,     // 像素比 1.0000000149011612
                }
            }''', force_expr=False)  # force_expr=False  执行的是函数

    print(dimensions)
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
