#!/usr/bin/env python3
"""
astock-video-report / make_slides.py
生成 A 股复盘横屏幻灯片 (1920x1080, 7张)

依赖: pip install pillow

用法:
  python3 make_slides.py --date 2026-03-16 --outdir ~/astock-output \
    --up   "名称,代码,涨跌幅,成交额,AI归因|名称,代码,..." \
    --down "..." --vol "..." --news "标签,标题,AI关联|..." \
    --idx  "上证点位,涨跌幅,深证点位,涨跌幅,创业板点位,涨跌幅" \
    --stats "上涨家数,下跌家数,涨停家数,跌停家数,全市场成交额"
    （stats 如接口无数据请传 "暂无,暂无,暂无,暂无,暂无"）
"""
import argparse, os, sys
from datetime import date as dt
from pathlib import Path

# 确保同目录下的模块可导入（从任意工作目录执行时）
sys.path.insert(0, str(Path(__file__).parent))

# ── 字体查找（跨平台）──────────────────────────────────
def find_font():
    candidates = [
        # macOS
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/Hiragino Sans GB.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        # Linux
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        # Windows
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/simsun.ttc',
        # skill 自带（assets/fonts/）
        str(Path(__file__).parent.parent / 'assets' / 'fonts' / 'NotoSansSC-Regular.ttf'),
    ]
    return next((f for f in candidates if os.path.exists(f)), None)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ 缺少依赖：请运行 pip install pillow")
    sys.exit(1)

FONT_PATH = find_font()
if not FONT_PATH:
    # 尝试自动下载字体
    try:
        from ensure_assets import ensure_font
        downloaded = ensure_font()
        if downloaded:
            FONT_PATH = downloaded
    except ImportError:
        pass
if not FONT_PATH:
    print("⚠️  未找到中文字体，文字可能显示为方块。建议运行 python3 scripts/ensure_assets.py")

def F(size):
    try:
        return ImageFont.truetype(FONT_PATH, size) if FONT_PATH else ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

W, H = 1920, 1080
BG=(10,12,22); WHITE=(235,242,255); DIM=(90,105,135)
RED=(255,65,65); GREEN=(45,210,100); CYAN=(0,195,255)
GOLD=(255,205,50); CARD=(18,22,42); LINE=(30,42,80)

def tw(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font); return bb[2]-bb[0]
def th(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font); return bb[3]-bb[1]

def make_bg():
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    for x in range(0, W, 80): draw.line([(x,0),(x,H)], fill=(16,20,38))
    for y in range(0, H, 80): draw.line([(0,y),(W,y)], fill=(16,20,38))
    for r in range(300, 0, -8):
        c = int(15*(1-r/300)**2)
        draw.ellipse([-r,-r,r,r], outline=(c,c*2,c*5))
    for r in range(250, 0, -8):
        c = int(12*(1-r/250)**2)
        draw.ellipse([W-r,H-r,W+r,H+r], outline=(c*2,c,c*4))
    return img

def header(draw, left="非凸科技 ft.tech  ×  OpenClaw", right="AI 每日 A 股播报"):
    draw.text((60,36), left, font=F(26), fill=(40,60,100))
    draw.text((W-60,36), right, font=F(26), fill=(40,60,100), anchor='ra')
    draw.rectangle([60,80,W-60,81], fill=LINE)

def footer(draw, left="数据来源：非凸科技 ft.tech / ftshare-market-data", right=""):
    draw.rectangle([60,H-72,W-60,H-71], fill=LINE)
    draw.text((60,H-56), left, font=F(24), fill=(45,60,95))
    if right: draw.text((W-60,H-56), right, font=F(24), fill=(45,60,95), anchor='ra')

def insight(draw, text, y):
    f=F(34); ph=16; card_h=th(draw,text,f)+ph*2
    draw.rounded_rectangle([60,y,W-60,y+card_h], radius=8, fill=CARD)
    draw.rectangle([60,y,67,y+card_h], fill=GOLD)
    draw.text((100,y+ph), "AI 分析  |  ", font=f, fill=GOLD)
    off=tw(draw,"AI 分析  |  ",f)
    draw.text((100+off,y+ph), text, font=f, fill=(200,210,230))

def stock_rows(draw, stocks, y_start=192):
    row_h=(H-y_start-80)//max(len(stocks),1)
    y=y_start
    for name,code,pct,amt,ai in stocks:
        draw.rectangle([60,y,W-60,y+1], fill=LINE)
        cy=y+(row_h-80)//2
        pct_color = RED if pct.startswith('+') else GREEN
        draw.text((60,cy), name, font=F(46), fill=WHITE)
        draw.text((60,cy+54), code, font=F(28), fill=DIM)
        draw.text((480,cy), pct, font=F(52), fill=pct_color)
        draw.text((480,cy+56), amt, font=F(28), fill=DIM)
        draw.rectangle([720,cy,722,cy+80], fill=(40,55,90))
        draw.text((744,cy), "[AI]", font=F(28), fill=GOLD)
        # 截断过长的归因文案，避免溢出画面
        max_ai_w = W - 60 - 744
        ai_text = ai
        while tw(draw, ai_text, F(26)) > max_ai_w and len(ai_text) > 10:
            ai_text = ai_text[:-1]
        if ai_text != ai:
            ai_text = ai_text.rstrip() + '…'
        draw.text((744,cy+36), ai_text, font=F(26), fill=(150,170,210))
        y+=row_h

# ── 7 张幻灯片 ─────────────────────────────────────────
def s0_cover(date_str, idx, stats, title=None):
    img=make_bg(); draw=ImageDraw.Draw(img)
    header(draw)
    cover_title = title or "今日 A 股复盘"
    draw.text((60,100), cover_title, font=F(110), fill=WHITE)
    draw.text((60,240), date_str, font=F(54), fill=DIM)
    draw.rectangle([60,320,560,322], fill=CYAN)

    stat_labels=[("上涨",stats[0],"家  |  下跌",stats[1],"家"),
                 ("涨停",stats[2],"家  |  跌停",stats[3],"家"),
                 ("全市场成交额",stats[4],"","","")]
    y=355
    for parts in stat_labels:
        cx=60
        for i,p in enumerate(parts):
            if not p: continue
            is_val = (i==1 or i==3 or (i==1 and parts[0]=="全市场成交额"))
            # 数字类字段用亮色
            is_num = p not in ("家","  |  下跌","  |  跌停","上涨","涨停","跌停","全市场成交额","") and p!="暂无"
            color = CYAN if is_num else DIM
            if p == "暂无": color = (60,70,90)
            draw.text((cx,y), p, font=F(40), fill=color)
            cx+=tw(draw,p,F(40))
        y+=62

    # 指数卡片
    idx_info=[("上证指数",idx[0],idx[1]),("深证成指",idx[2],idx[3]),("创业板指",idx[4],idx[5])]
    iy=355
    for name,val,chg in idx_info:
        c = RED if chg.startswith('+') else (GREEN if chg.startswith('-') else DIM)
        draw.rounded_rectangle([1180,iy,1860,iy+140], radius=10, fill=CARD)
        draw.rectangle([1180,iy,1187,iy+140], fill=c)
        draw.text((1210,iy+12), name, font=F(32), fill=DIM)
        draw.text((1210,iy+52), val,  font=F(52), fill=WHITE)
        draw.text((1210,iy+112), chg, font=F(32), fill=c)
        iy+=160

    insight(draw, "本次复盘由 OpenClaw 自动完成：拉取真实行情 → 交叉比对新闻 → AI 归因分析", 870)
    footer(draw, right=date_str)
    return img

def s1_up(stocks):
    img=make_bg(); draw=ImageDraw.Draw(img)
    header(draw, right="涨幅 TOP5")
    draw.text((60,100),"▲  涨幅 TOP5",font=F(56),fill=RED)
    draw.rectangle([60,172,W-60,173],fill=RED)
    stock_rows(draw, stocks)
    footer(draw)
    return img

def s2_down(stocks):
    img=make_bg(); draw=ImageDraw.Draw(img)
    header(draw, right="跌幅 TOP5")
    draw.text((60,100),"▼  跌幅 TOP5",font=F(56),fill=GREEN)
    draw.rectangle([60,172,W-60,173],fill=GREEN)
    stock_rows(draw, stocks)
    footer(draw)
    return img

def s3_vol(stocks):
    img=make_bg(); draw=ImageDraw.Draw(img)
    header(draw, right="成交额 TOP5")
    draw.text((60,100),">>  成交额 TOP5  活跃度榜",font=F(56),fill=CYAN)
    draw.rectangle([60,172,W-60,173],fill=CYAN)
    stock_rows(draw, stocks)
    footer(draw)
    return img

def s4_news(news_list):
    img=make_bg(); draw=ImageDraw.Draw(img)
    header(draw, right="今日宏观")
    draw.text((60,100),"今日关键消息  &  市场关联",font=F(56),fill=GOLD)
    draw.rectangle([60,172,W-60,173],fill=GOLD)
    y=190; row_h=(H-190-80)//max(len(news_list),1)
    for tag_t,title,analysis in news_list:
        draw.rectangle([60,y,W-60,y+1],fill=LINE)
        cy=y+(row_h-76)//2
        draw.rounded_rectangle([60,cy+4,160,cy+44],radius=6,fill=(50,38,5))
        draw.text((110,cy+24),tag_t,font=F(22),fill=GOLD,anchor='mm')
        draw.text((180,cy),title,font=F(38),fill=WHITE)
        draw.text((180,cy+48),"[AI关联] "+analysis,font=F(26),fill=(195,165,55))
        y+=row_h
    footer(draw, "新闻来源：华尔街见闻 / newsnow-reader")
    return img

def s5_install():
    img=make_bg(); draw=ImageDraw.Draw(img)
    header(draw, right="如何使用")
    draw.text((60,100),"三步开始使用",font=F(80),fill=WHITE)
    draw.rectangle([60,210,600,212],fill=CYAN)
    steps=[("01","安装 OpenClaw","AI 技能运行平台  |  openclaw.ai",CYAN),
           ("02","安装数据 Skill","skillhub install ftshare-*  （四个包）",GREEN),
           ("03","告诉 AI","「帮我每天生成A股复盘并推送到微信」",GOLD)]
    y=240
    for num,title,desc,color in steps:
        draw.rounded_rectangle([60,y,W//2-40,y+160],radius=12,fill=CARD)
        draw.rectangle([60,y,68,y+160],fill=color)
        draw.text((90,y+18),num,font=F(52),fill=color)
        draw.text((90,y+78),title,font=F(40),fill=WHITE)
        draw.text((90,y+128),desc,font=F(28),fill=DIM)
        y+=178
    draw.rounded_rectangle([W//2+20,240,W-60,830],radius=14,fill=CARD)
    draw.rounded_rectangle([W//2+20,240,W-60,830],radius=14,outline=(30,50,90),width=1)
    draw.text((W//2+50,262),"# 终端执行以下命令",font=F(26),fill=(45,70,80))
    cmds=[("$ ","skillhub install ftshare-market-data"),
          ("$ ","skillhub install ftshare-announcement-data"),
          ("$ ","skillhub install ftshare-holder-data"),
          ("$ ","skillhub install ftshare-kline-data")]
    cy=316
    for prompt,cmd in cmds:
        draw.text((W//2+50,cy),prompt,font=F(30),fill=GREEN)
        draw.text((W//2+85,cy),cmd,font=F(30),fill=(120,200,255))
        cy+=68
    draw.rectangle([W//2+50,cy+10,W-90,cy+11],fill=LINE)
    draw.text((W//2+50,cy+28),"或者直接问 AI：",font=F(28),fill=DIM)
    draw.rounded_rectangle([W//2+50,cy+68,W-90,cy+148],radius=8,fill=(20,30,55))
    draw.text((W//2+70,cy+88),"「帮我安装非凸科技A股数据Skill」",font=F(28),fill=GOLD)
    footer(draw,"skillhub.com  |  openclaw.ai")
    return img

def s6_end():
    img=make_bg(); draw=ImageDraw.Draw(img)
    header(draw)
    draw.text((60,200),"非凸科技",font=F(120),fill=WHITE)
    draw.text((60,355),"ft.tech",font=F(72),fill=CYAN)
    draw.rectangle([60,460,800,462],fill=CYAN)
    draw.text((60,490),"让 AI 真正懂 A 股",font=F(52),fill=(160,190,230))
    feats=[("实时数据","非凸科技官方 API，非推测",CYAN),
           ("AI 归因","交叉比对新闻，自动分析",GOLD),
           ("自动推送","收盘后定时推送到微信",GREEN)]
    fy=220
    for title,desc,color in feats:
        draw.rounded_rectangle([1100,fy,1860,fy+180],radius=12,fill=CARD)
        draw.rectangle([1100,fy,1108,fy+180],fill=color)
        draw.text((1130,fy+20),title,font=F(48),fill=color)
        draw.text((1130,fy+84),desc,font=F(30),fill=DIM)
        fy+=200
    insight(draw,"数据仅供参考，不构成任何投资建议。非凸科技 x OpenClaw 出品。",880)
    footer(draw,"ft.tech  |  skillhub: 搜索 ftshare")
    return img

# ── 参数解析 ──────────────────────────────────────────
def parse_stocks(raw):
    result=[]
    for item in raw.split('|'):
        parts=item.strip().split(',',4)
        if len(parts)==5:
            result.append(tuple(p.strip() for p in parts))
    return result

def parse_news(raw):
    result=[]
    for item in raw.split('|'):
        parts=item.strip().split(',',2)
        if len(parts)==3:
            result.append(tuple(p.strip() for p in parts))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description='生成 A 股复盘幻灯片')
    p.add_argument('--date',   required=True, help='交易日期，格式 YYYY-MM-DD（必填，由 AI agent 根据市场状态判断传入）')
    p.add_argument('--outdir', default=os.path.expanduser('~/astock-output'), help='输出目录')
    p.add_argument('--up',   default='', help='涨幅股票，格式: 名称,代码,涨跌幅,成交额,AI归因|...')
    p.add_argument('--down', default='', help='跌幅股票，同上')
    p.add_argument('--vol',  default='', help='成交额股票，同上')
    p.add_argument('--news', default='', help='新闻，格式: 标签,标题,AI关联|...')
    p.add_argument('--idx',  default='暂无,--,暂无,--,暂无,--', help='指数: 上证点位,涨跌幅,深证点位,涨跌幅,创业板点位,涨跌幅')
    p.add_argument('--stats',default='暂无,暂无,暂无,暂无,暂无', help='上涨家数,下跌家数,涨停家数,跌停家数,全市场成交额')
    p.add_argument('--title',default=None, help='封面标题（默认「今日 A 股复盘」，盘中可传「A 股盘中快报」）')
    args=p.parse_args()

    outdir=os.path.expanduser(args.outdir)
    slides_dir=os.path.join(outdir,'slides',args.date)
    os.makedirs(slides_dir, exist_ok=True)

    idx=args.idx.split(',')
    while len(idx)<6: idx.append('--')
    stats=args.stats.split(',')
    while len(stats)<5: stats.append('暂无')

    up_stocks   = parse_stocks(args.up)
    down_stocks = parse_stocks(args.down)
    vol_stocks  = parse_stocks(args.vol)
    news_list   = parse_news(args.news)

    pages=[
        ('00_封面',      s0_cover(args.date, idx, stats, title=args.title)),
        ('01_涨幅TOP5',  s1_up(up_stocks)),
        ('02_跌幅TOP5',  s2_down(down_stocks)),
        ('03_成交额TOP5', s3_vol(vol_stocks)),
        ('04_今日消息',   s4_news(news_list)),
        ('05_安装方法',   s5_install()),
        ('06_结尾',       s6_end()),
    ]
    for name,img in pages:
        path=os.path.join(slides_dir, f'{name}.png')
        img.save(path)
        print(f'  ✅ {path}')
    print(f'\n✅ 幻灯片已生成到 {slides_dir}')
