#!/usr/bin python3
# conding=utf-8

import requests
from bs4 import BeautifulSoup as bs
import re
import datetime
import os
import json
from pyecharts.charts import Pie
from pyecharts.charts import Bar
from pyecharts.charts import Grid
from pyecharts.charts import Page
from pyecharts.charts import Calendar
from pyecharts.charts import PictorialBar
from pyecharts.charts import WordCloud
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType
from pyecharts.globals import SymbolType
from pyecharts import options as opts

def crawlWebsite(url, headers):
    try:
        r = requests.get(url, headers = headers, timeout = 30)
        #访问网页失败抛出异常
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        return ""
    
#该软件的各年更新频率
def updateRate(soup):
    strong = soup.find_all('strong')
    #有些数据写入时对齐的不好，加空格方便读取
    for i in range(68, 74):
        temp = list(strong[i].string)
        temp.insert(6, ' ')
        strong[i].string = ''.join(temp)

    strong.remove(strong[0])
    strong.remove(strong[0])
    strong.remove(strong[0])
    temp = list(strong[1].string)
    temp.insert(19, ' ')
    strong[1].string = ''.join(temp)

    time = {}
    for i in strong:
        num = re.findall(r' .*? ', i.string)
        date = re.findall(r'201\d[年/].*', i.string)
        if len(date) == 0 or len(num) == 0:
            continue
        num = num[0][1:-1]
        time[num] = date[0]

    years = [0,0,0,0,0,0]
    year = [x for x in range(2014, 2020)]
    for value in time.values():
        if re.search(r'2014', value):
            years[0] = years[0] + 1
        elif re.search(r'2015', value):
            years[1] = years[1] + 1
        elif re.search(r'2016', value):
            years[2] = years[2] + 1
        elif re.search(r'2017', value):
            years[3] = years[3] + 1
        elif re.search(r'2018', value):
            years[4] = years[4] + 1
        elif re.search(r'2019', value):
            years[5] = years[5] + 1
    pie = Pie(init_opts=opts.InitOpts(width = '500px'))
    pie.add("", [(year[i], years[i]) for i in range(6)],
            radius=["75px", "200px"],
            center=["75%", "50%"],
            rosetype="area")
    pie.set_global_opts(title_opts=opts.TitleOpts(title="Dism++各年更新频率", pos_left='55%', pos_top="75px",
            title_textstyle_opts=opts.TextStyleOpts(color="white")),
            legend_opts=opts.LegendOpts(
                orient="vertical", pos_top="25%", pos_left="55%"
            ))

    bar = Bar(init_opts=opts.InitOpts(bg_color={
                    "type": "pattern",
                    "image": JsCode("img"),
                    "repeat": "no-repeat",
                }))
    bar.add_xaxis(year)
    bar.add_yaxis("更新次数", years)
    bar.set_global_opts(title_opts=opts.TitleOpts(title="Dism++各年更新次数", pos_top="75px",title_textstyle_opts=opts.TextStyleOpts(color="white")),
            legend_opts=opts.LegendOpts(is_show=True, pos_top = "37%", pos_left="2%"),
            graphic_opts=opts.GraphicGroup(graphic_item=opts.GraphicItem(
                        # 控制整体的位置
                        left="center",
                        top="10px",
                    ),
                    children=[
                        opts.GraphicText(
                            graphic_item=opts.GraphicItem(
                                left="center",
                                top="top",
                                z=100,
                            ),
                            graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                                text="DISM++ 更新记录分析",
                                font="32px Microsoft YaHei",
                                graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                                    fill="white"
                                )
                            ))]))
    grid = Grid(init_opts=opts.InitOpts(height= '650px',width = '1250px',theme=ThemeType.WALDEN))
    grid.add(bar, grid_opts=opts.GridOpts(pos_right="55%",pos_top="125px", pos_bottom="150px"))
    grid.add(pie, grid_opts=opts.GridOpts(pos_left="55%",pos_top="125px", pos_bottom="150px"))
    grid.add_js_funcs(
        """
        var img = new Image(); img.src = 'bg.jpg';
        """
    )
    return grid

def updateContent(soup):
    #更新内容所属类别
    div = soup.find('div', attrs={'id':'readme'})
    ul = div.findAll('ul')
    ul.remove(ul[0])
    num = [0 for i in range(8)]
    
    for u in ul:
        li = u.findAll('li')
        for i in li:
            if(len(re.findall(r'升级', str(i))) != 0):
                num[0] = num[0] + 1
            elif(len(re.findall(r'更新', str(i))) != 0):
                num[1] = num[1] + 1
            elif(len(re.findall(r'新增', str(i))) != 0):
                num[2] = num[2] + 1
            elif(len(re.findall(r'语言|Languages|languages', str(i))) != 0):
                num[3] = num[3] + 1
            elif(len(re.findall(r'调整', str(i))) != 0):
                num[4] = num[4] + 1
            elif(len(re.findall(r'改进', str(i))) != 0):
                num[5] = num[5] + 1
            elif(len(re.findall(r'修复|解决|BUG', str(i))) != 0):
                num[6] = num[6] + 1
            else:
                num[7] = num[7] + 1

    categories = ['升级库','更新功能','新增功能','新语言支持','调整界面或逻辑','改进用户体验','修复BUG或解决其他问题','其他']
    pie = Pie(init_opts=opts.InitOpts(width='1250px', theme=ThemeType.WALDEN, bg_color={
                    "type": "pattern",
                    "image": JsCode("img"),
                    "repeat": "no-repeat",
                }))
    pie.add('', [(categories[j], num[j]) for j in range(8)])
    pie.set_global_opts(title_opts=opts.TitleOpts(title="Dism++更新分类",pos_top='10px',title_textstyle_opts=opts.TextStyleOpts(color="white")),
            legend_opts=opts.LegendOpts(
                orient="vertical", pos_top="15%", pos_left="2%"
            ),graphic_opts=opts.GraphicGroup(graphic_item=opts.GraphicItem(
                        # 控制整体的位置
                        left="75%",
                        top="20%",
                    ),
                    children=[
                        opts.GraphicText(
                            graphic_item=opts.GraphicItem(
                                left="center",
                                top="5px",
                                z=100,
                            ),
                            graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                                text="通过对更新内容进行分类，该软件\n更新主要是解决BUG及一些特殊的\n问题，增添功能改善体验的更新较少",
                                font="16px Microsoft YaHei",
                                graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                                    fill="white"
                                )
                            ))]))
    pie.add_js_funcs(
        """
        var img = new Image(); img.src = 'bg3.jpg';
        """
    )
    return pie

def monthlyUpdateRate(soup,flag):
    div = soup.find('div', attrs={'id':'readme'})
    p = div.findAll('p')
    dates = {}#存储日期与次数的对应

    for i in p:
        r1 = re.findall(r'/\d+/', str(i))
        r2 = re.findall(r'/\d+[(<（日]', str(i))
        if len(r1) == 0 or len(r2) == 0:
            continue
        date = datetime.date(2019, int(r1[0][1:-1]), int(r2[0][1:-1]))
        if str(date) in dates.keys():
            dates[str(date)] = dates[str(date)] + 1
        else:
            dates[str(date)] = 1

    with open(os.path.join("fixtures", "symbol.json"), "r", encoding="utf-8") as f:
        symbols = json.load(f)
    pic = PictorialBar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN, width='1250px', bg_color={
                    "type": "pattern",
                    "image": JsCode("img"),
                    "repeat": "no-repeat",
                }))
    month = [str(num) + "月" for num in range(1,13)]
    nums = [0 for i in range(12)]
    for date in dates.keys():
        nums[int(date[5:7]) - 1] = nums[int(date[5:7]) - 1] + dates[date]
    pic.add_xaxis(month)
    pic.add_yaxis("", nums,
                  label_opts=opts.LabelOpts(is_show=False),
                  symbol_size=18,
                  symbol_repeat="fixed",
                  symbol_offset=[0, 0],
                  is_symbol_clip=True,
                  symbol=SymbolType.ROUND_RECT)
    pic.reversal_axis()
    pic.set_global_opts(title_opts=opts.TitleOpts(title="月更新次数",pos_top='10px',title_textstyle_opts=opts.TextStyleOpts(color="white")),
                        xaxis_opts=opts.AxisOpts(is_show=False),
                        yaxis_opts=opts.AxisOpts(
                            axistick_opts=opts.AxisTickOpts(is_show=False),
                            axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(opacity=0))
                            ),graphic_opts=opts.GraphicGroup(graphic_item=opts.GraphicItem(
                        # 控制整体的位置
                        left="65%",
                        top="20%",
                    ),
                    children=[
                        opts.GraphicText(
                            graphic_item=opts.GraphicItem(
                                left="center",
                                top="5px",
                                z=100,
                            ),
                            graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                                text="通过上边图例分析，我们发现，DISM++的开\n发团队在15~17年更新较为频繁，近两年来更\n新较少;通过月更新次数可以看出其主要更新时\n间集中在夏季的6,7月。",
                                font="16px Microsoft YaHei",
                                graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                                    fill="white"
                                )
                            ))]))
    pic.add_js_funcs(
        """
        var img = new Image(); img.src = 'bg2.jpg';
        """
    )
    
    cal = Calendar(init_opts=opts.InitOpts(height='300px', width='1250px',theme=ThemeType.WALDEN, bg_color={
                    "type": "pattern",
                    "image": JsCode("img"),
                    "repeat": "no-repeat",
                }))
    cal.add("", [[key, dates[key]] for key in dates.keys()], calendar_opts = opts.CalendarOpts(range_="2019",yearlabel_opts=opts.LabelOpts(is_show=False)))
    cal.set_global_opts(
        title_opts=opts.TitleOpts(title="月更新频率",pos_top='10px',title_textstyle_opts=opts.TextStyleOpts(color="white")),
        visualmap_opts=opts.VisualMapOpts(
            max_=3,
            min_=0,
            orient="horizontal",
            is_piecewise=True,
            pos_left='120px',
            pos_bottom='30px',
            split_number = 3
        ))
    cal.add_js_funcs(
        """
        var img = new Image(); img.src = 'bg1.jpg';
        """
    )
    if flag == 1:
        return pic
    else:
        return cal

def thanksUser(soup):
    #bug贡献者词云图(按贡献者贡献次数排列)
    div = soup.find('div', attrs={'id':'readme'})
    li = div.findAll('li')
    thanks = {}
    for i in li:
        users = re.findall(r'感谢 .*）', str(i))
        if len(users) == 0:
            continue
        user = re.split('、| ', users[0][3:-1])
        for u in user:
            if u in thanks.keys():
                thanks[u] = thanks[u] + 1
            else:
                thanks[u] = 1
    thanks.pop('反馈')
    wordcloud = WordCloud(init_opts=opts.InitOpts(theme=ThemeType.WALDEN, width='1250px', bg_color={
                    "type": "pattern",
                    "image": JsCode("img"),
                    "repeat": "no-repeat",
                }))
    wordcloud.add("", [(key, thanks[key]) for key in thanks], word_size_range = [20, 100], shape=SymbolType.DIAMOND)
    wordcloud.set_global_opts(title_opts=opts.TitleOpts(title="BUG贡献者词云图",pos_top='10px',title_textstyle_opts=opts.TextStyleOpts(color="white")),
                graphic_opts=opts.GraphicGroup(graphic_item=opts.GraphicItem(
                        # 控制整体的位置
                        right='right',
                        top="30%",
                    ),
                    children=[
                        opts.GraphicText(
                            graphic_item=opts.GraphicItem(
                                left="center",
                                top="5px",
                                z=100,
                            ),
                            graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                                text="对BUG贡献者进行词云\n图分析，对该软件贡献\n最大的几个人为“原罪，\nHexhu，Vasiliy，显然\n是对该软件感兴趣并且\n乐意奉献自己的时间的\n技术人才。”",
                                font="16px Microsoft YaHei",
                                graphic_basicstyle_opts=opts.GraphicBasicStyleOpts(
                                    fill="white"
                                )
                            ))]))
    wordcloud.add_js_funcs(
        """
        var img = new Image(); img.src = 'bg4.jpg';
        """
    )
    return wordcloud

if __name__ == "__main__":
    url = "https://github.com/Chuyu-Team/Dism-Multi-language/blob/master/UpdateHistory.md"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    html = crawlWebsite(url, headers)
    soup = bs(html, 'html.parser')

    page = Page(page_title='Dism++更新记录分析',interval = 0)
    rate = updateRate(soup)
    content = updateContent(soup)
    monthly = monthlyUpdateRate(soup,1)
    day = monthlyUpdateRate(soup, 2)
    wordcloud = thanksUser(soup)
    page.add(rate)
    page.add(day)
    page.add(monthly)
    page.add(content)
    page.add(wordcloud)
    page.render(f"Dism++更新记录分析.html")
