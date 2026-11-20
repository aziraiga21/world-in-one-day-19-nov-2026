from itertools import combinations
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAPER, RED, NAVY = "#F7F3E8", "#9E2B25", "#1F3552"
INK, GREY, SEA, LAND = "#222525", "#565750", "#DCE8EE", "#E8D9A8"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FACES = {"serif": "Serif", "title": "Serif-Bold", "italic": "Serif-Italic",
         "sans": "Sans", "bold": "Sans-Bold"}
image = Image.new("RGB", (1024, 1024), PAPER)
draw = ImageDraw.Draw(image)
fonts = {}
checks = 0


def font(face, size):
    key = face, size
    if key not in fonts:
        path = FONT_DIR / f"DejaVu{FACES[face]}.ttf"
        if face == "italic" and not path.exists():
            path = FONT_DIR.parent / "liberation/LiberationSerif-Italic.ttf"
        fonts[key] = ImageFont.truetype(str(path), size)
    return fonts[key]


def wrap(text, face, width):
    lines = [""]
    for word in text.split():
        candidate = f"{lines[-1]} {word}".strip()
        if lines[-1] and face.getlength(candidate) > width:
            lines.append(word)
        else:
            lines[-1] = candidate
    return lines


def block(text, box, face="sans", size=12, minimum=None, color=INK,
          max_lines=1, align="left", leading=None, bounds=None):
    global checks
    x, y, width, height = box
    assert 0 <= x and 0 <= y and x + width <= 1024 and y + height <= 1024, box
    for point in range(size, (minimum if minimum is not None else size) - 1, -1):
        f = font(face, point)
        lines = wrap(text, f, width)
        step = leading or point + 2
        if len(lines) > max_lines:
            continue
        positioned = []
        for i, line in enumerate(lines):
            length = f.getlength(line)
            bx0, by0, bx1, by1 = f.getbbox(line, anchor="lt")
            span = max(length, bx1) - min(0, bx0)
            inset = {"left": 0, "center": (width-span)/2, "right": width-span}[align]
            if span > width or i * step + by1 > height:
                break
            positioned.append((i, line, inset - min(0, bx0), (bx0, by0, bx1, by1)))
        else:
            break
    else:
        raise AssertionError(f"Text cannot fit {box}: {text}")
    for i, line, offset, (bx0, by0, bx1, by1) in positioned:
        assert f.getlength(line) <= width
        left, top = x + offset, y + i * step
        draw.text((left, top), line, font=f, fill=color, anchor="lt")
        if bounds is not None:
            bounds.append((left + bx0, top + by0, left + bx1, top + by1))
        checks += 1
    return (len(lines) - 1) * step + point


def tracked(text, x, y, width, right=False):
    f = font("bold", 11)
    lengths = [f.getlength(c) + 1.2 for c in text]
    total = sum(lengths) - 1.2
    assert total <= width
    pos = x + (width - total if right else 0)
    for c, length in zip(text, lengths):
        draw.text((pos, y), c, font=f, fill=RED, anchor="lt")
        pos += length


heroes = [
    ("1 · SHENZHEN · SUMMIT", "Trump, Xi and Putin hold first three-way summit",
     "The US, Chinese and Russian leaders met at APEC in Shenzhen and issued a four-point 'Declaration toward Peace' on nuclear risk and UN reform.", "— Reuters · AP"),
    ("2 · THE HAGUE · JUSTICE", "World Court: Myanmar committed genocide",
     "The ICJ found Myanmar guilty of genocide against the Rohingya in the 2017 campaign — the first such ruling against a State — and ordered reparations.", "— Al Jazeera · UN News"),
    ("3 · ANTALYA · CLIMATE", "COP31 draft drops fossil fuels and $120bn aid goal",
     "The slimmer draft text has no figure for adaptation aid. Talks are due to end on Friday.", "— Reuters · AFP"),
]
tiles = [
    ("4 · NEW YORK · MARKETS", "Anthropic starts trading on Nasdaq", "Its record $81.3bn share sale was priced at $83."),
    ("5 · WORLDWIDE · GAMES", "GTA VI goes on sale after 13 years", "The midnight launch draws rave reviews."),
    ("6 · ODISHA · STORM", "Cyclone Akvan nears India's coast", "200,000 evacuated before Friday's landfall."),
    ("7 · CRIMEA · WAR", "Ukraine hits Crimea bridge again", "Third strike in a week halts trains to Russia."),
    ("8 · RIYADH · WAR", "Saudis shoot down Houthi missiles", "Debris fell on the capital; no casualties reported."),
    ("9 · GREENLAND · SECURITY", "Denmark backs Arctic pact with US", "Parliament approves the Greenland security deal 109–0."),
    ("10 · SEOUL · JUSTICE", "Korea's top court clears ex-PM Han", "Han Duck-soo's martial-law conviction is overturned."),
    ("11 · BOGOTÁ · LABOUR", "Colombia's unions hold national strike", "Marches in three cities against the government."),
    ("12 · CANBERRA · ECONOMY", "Australia's jobless rate hits 4.9%", "Highest since 2024; shares and the dollar slide."),
]
briefs = """13 GAZA — IDF ends Nuseirat operation; aid groups score peace plan 4 of 26. Al Jazeera
14 HORMUZ — Iran widens Gulf attacks as US blockade continues. Al Jazeera
15 SENEGAL — Migrant boat sinks off Senegal; dozens missing. AFP
16 MONGOLIA — Parliament accepts President Khürelsükh's resignation. AP
17 IRAQ — Government and Kataib Hezbollah end Jurf al-Sakhar standoff. AP
18 PAKISTAN — Military says 22 militants killed in Khyber Pakhtunkhwa raids. AP
19 YEMEN — Water output in Taiz nearly halved; 800,000 cut off from aid. UNICEF
20 USA — Walmart reports $188.8bn revenue, up 5.2%. AP
21 GLOBAL — Nvidia stops selling top China chips as PLA seeks them. AP
22 SUDAN — Court sentences absent RSF chief to death. AP
23 ROME — Author Corrado Augias dies at 91. Euronews
24 MOGADISHU — Somalia expels UAE ambassador. Al Jazeera
25 FLORIDA — Floods shut Broward; Miami schools close again. CBS
26 NAIROBI — Marathon champion banned for doping, three years. ABC
27 JAKARTA — Asset-seizure law passes after 18 years. Kompas
28 KYIV — Kyiv says it hit two Russian oil refineries. Euronews
29 AUCKLAND — New Zealand plays first as GTA VI unlocks at local midnight. RNZ
30 WASHINGTON — Vance: no "forever war" in the Gulf. AP
31 CARACAS — Hegseth signs a US–Venezuela military deal. AP
32 LONDON — Van Gogh sells for a record $190.4m after row over its Nazi history. AP
33 TOKYO — India and Japan review defence ties at their 2+2 dialogue. AP""".splitlines()

continents = [
    [(-168,66),(-140,70),(-125,72),(-110,73),(-95,80),(-85,66),(-75,62),(-65,60),(-55,52),(-60,45),(-70,42),(-75,35),(-80,25),(-85,30),(-95,20),(-105,20),(-110,25),(-120,35),(-125,48),(-140,60),(-155,58),(-165,60)],
    [(-80,10),(-75,5),(-70,0),(-60,-5),(-50,-5),(-40,-10),(-35,-15),(-40,-25),(-50,-30),(-60,-35),(-70,-40),(-75,-50),(-70,-55),(-75,-35),(-80,-20),(-80,-5)],
    [(-10,35),(0,35),(10,37),(20,32),(30,31),(35,28),(40,20),(45,12),(50,10),(45,0),(40,-10),(35,-20),(30,-30),(20,-35),(15,-30),(10,-15),(5,0),(0,5),(-10,10),(-15,25)],
    [(-10,36),(-5,40),(0,43),(5,45),(10,55),(15,58),(20,60),(25,65),(30,70),(35,68),(30,60),(25,55),(20,50),(15,45),(10,40),(5,38),(0,36)],
    [(35,70),(50,72),(70,73),(90,75),(110,76),(130,72),(150,70),(170,66),(160,60),(150,55),(140,45),(130,40),(120,35),(110,25),(100,20),(95,10),(90,5),(85,15),(80,20),(75,25),(70,30),(60,30),(55,25),(50,30),(45,35),(40,40),(35,45),(35,55),(40,60)],
    [(113,-22),(120,-15),(130,-12),(140,-17),(145,-15),(150,-22),(150,-30),(145,-38),(140,-38),(130,-32),(120,-35),(113,-30)],
    [(-73,73),(-60,82),(-25,83),(-15,77),(-28,68),(-44,59),(-54,63)],
    [(166,-46),(170,-43),(178,-36),(175,-38),(172,-43),(169,-46)],
]
locations = [(114,22),(4,52),(30,37),(-74,41),None,(85,20),(34,45),(47,25),
             (-45,72),(127,37),(-74,5),(149,-35),(34,31),(56,26),(-17,15),
             (106,47),(44,33),(70,30),(45,15),(-95,38),None,(30,13),(12,42),
             (45,2),(-81,27),(37,-1),(107,-6),(30,50),(175,-37),(-77,39),
             (-67,10),(0,51),(140,36)]


def rule(y, x1=24, x2=999, fill=NAVY, width=1):
    draw.line((x1, y, x2, y), fill=fill, width=width)


def star(paint, x, y, radius, fill):
    from math import cos, pi, sin
    points = []
    for i in range(10):
        angle = i * pi / 5 - pi / 2
        r = radius if i % 2 == 0 else radius * .43
        points.append((x + r * cos(angle), y + r * sin(angle)))
    paint.polygon(points, fill=fill)


def burst(paint, x, y):
    paint.polygon([(x-10,y), (x-3,y-2), (x-6,y-9), (x,y-5), (x+5,y-10),
                   (x+5,y-3), (x+11,y), (x+4,y+3), (x+3,y+9), (x-2,y+4)],
                  fill="#F3C36A", outline=RED)


def hero_art(index, x, y):
    art = Image.new("RGB", (312, 130), [NAVY, "#E8DCC4", "#DBE8E7"][index])
    p = ImageDraw.Draw(art)
    if index == 0:
        for i, left in enumerate((26, 119, 212)):
            p.line((left-3, 14, left-3, 72), fill="#B7AC8D", width=2)
            if i == 0:
                p.rectangle((left, 18, left+73, 61), fill=PAPER)
                for j in range(7):
                    p.rectangle((left, 18+j*6, left+73, 20+j*6), fill=RED)
                p.rectangle((left, 18, left+33, 41), fill="#314C72")
                for row in range(4):
                    for col in range(6):
                        p.point((left+3+col*5+row%2, 21+row*5), fill=PAPER)
            elif i == 1:
                p.rectangle((left, 18, left+73, 61), fill="#AD332B")
                star(p, left+13, 30, 7, "#F4D477")
                for dx, dy in [(24, 22), (29, 27), (29, 34), (24, 39)]:
                    star(p, left+dx, dy, 2.5, "#F4D477")
            else:
                for j, color in enumerate((PAPER, "#375D98", "#AD332B")):
                    p.rectangle((left, 18+j*15, left+73, 32+j*15), fill=color)
            cx = left+36
            p.ellipse((cx-7, 73, cx+7, 90), fill="#D6AD88")
            p.polygon([(cx-18,107),(cx-13,93),(cx,89),(cx+13,93),(cx+18,107)],
                      fill="#131F30", outline="#B4BEC7")
            p.polygon([(cx-5,91),(cx+5,91),(cx,103)], fill=PAPER)
            p.line((cx,94,cx,101), fill=RED, width=2)
        p.polygon([(35,107),(276,107),(292,119),(18,119)], fill="#AB7951")
        p.line((18,119,292,119), fill="#D9B18A", width=2)
    elif index == 1:
        p.rectangle((0, 106, 312, 129), fill="#D6C7AB")
        p.polygon([(23,48),(107,13),(191,48)], fill=NAVY)
        p.polygon([(39,44),(107,20),(175,44)], fill="#C7AD7B")
        p.ellipse((102,29,112,39), fill=NAVY)
        p.rectangle((28,49,186,55), fill=NAVY)
        p.rectangle((35,57,179,104), fill="#AB9876")
        for cx in (43, 74, 106, 138, 170):
            p.rectangle((cx-7,58,cx+7,101), fill=PAPER)
            p.line((cx+3,59,cx+3,100), fill="#C8B792", width=2)
            p.rectangle((cx-9,57,cx+9,61), fill=NAVY)
        for j in range(3):
            p.rectangle((29-j*5, 101+j*6, 184+j*5, 105+j*6), fill=NAVY)
        p.line((248,37,248,105), fill=NAVY, width=3)
        p.line((218,52,278,52), fill=NAVY, width=3)
        p.ellipse((244,33,252,41), fill=RED)
        p.rounded_rectangle((229,104,267,110), 2, fill=NAVY)
        for cx in (220, 276):
            p.line([(cx-13,77),(cx,52),(cx+13,77)], fill=NAVY, width=2)
            p.chord((cx-14,69,cx+14,86), 0, 180, fill=RED, outline=NAVY)
    else:
        p.ellipse((22,17,116,111), fill="#A9C6D1", outline=NAVY, width=2)
        p.ellipse((43,17,95,111), outline="#688A9A")
        p.arc((22,34,116,94), 0, 360, fill="#688A9A")
        p.line((22,64,116,64), fill="#688A9A")
        p.polygon([(30,43),(46,26),(62,25),(72,35),(61,45),(48,50),(52,58),
                   (43,62),(37,55)], fill="#667D61")
        p.polygon([(55,64),(75,62),(82,73),(72,96),(65,103),(61,83)], fill="#667D61")
        p.polygon([(92,33),(105,45),(111,65),(96,63),(88,50)], fill="#667D61")
        p.rounded_rectangle((108,29,125,94), 8, fill=PAPER, outline=NAVY, width=2)
        p.ellipse((103,81,130,108), fill=PAPER, outline=NAVY, width=2)
        p.rectangle((114,48,119,93), fill=RED)
        p.ellipse((109,87,124,102), fill=RED)
        for ty in (40,50,60,70):
            p.line((120,ty,124,ty), fill=NAVY)
        p.rectangle((146,21,283,110), fill=PAPER, outline=NAVY)
        for ty in (36,43,73,81,89,97):
            p.line((158,ty,267,ty), fill="#B0A99A")
    image.paste(art, (x, y))
    if index == 2:
        block("FOSSIL FUELS", (x+157,y+51,119,15), "bold", 14, color=NAVY)
        draw.line((x+153,y+64,x+275,y+51), fill=RED, width=3)
        draw.rectangle((x+233,y+77,x+295,y+101), fill=PAPER, outline=RED, width=2)
        block("CUT", (x+235,y+81,58,18), "bold", 17, color=RED, align="center")


def panel(index, x, y):
    kicker, headline, deck, source = heroes[index]
    hero_art(index, x, y)
    block(kicker, (x,y+138,312,13), "bold", 12, color=RED)
    h = block(headline, (x,y+157,312,58), "title", 24, 20, NAVY, 2)
    block(deck, (x,y+161+h,312,105-h), size=13, minimum=12, max_lines=4, leading=14)
    block(source, (x,y+267,312,12), size=11, color=GREY)


def banner(index, x, y, bounds):
    backgrounds = ("#DCE8D8","#302944","#C9DDE5","#D7DFE3","#233049",
                   "#C9DDE8","#E8DBC3","#E9D9BA","#EDDCD3")
    art = Image.new("RGB", (90, 43), backgrounds[index])
    p = ImageDraw.Draw(art)
    if index in (0,8):
        for yy in (12,24,35):
            p.line((3,yy,86,yy), fill="#A2B3A2" if index == 0 else "#D6BFB5")
        points = [(7,35),(18,31),(29,33),(40,22),(51,26),(62,15),(74,17),(83,7)]
        if index == 0:
            for i, (cx, cy) in enumerate(points):
                color = "#286246" if i not in (2,4,6) else RED
                p.line((cx,cy-6,cx,cy+6), fill=color)
                p.rectangle((cx-3,cy-3,cx+3,cy+3), fill=color)
        else:
            p.line(points, fill=RED, width=2)
            for cx in (9,17,25):
                p.ellipse((cx-2,11,cx+2,15), fill=NAVY)
                p.line((cx,16,cx,24), fill=NAVY, width=2)
    elif index in (1,4):
        for i, height in enumerate((12,21,16,24,17,11,20,14,25,14)):
            cx = i*9
            p.rectangle((cx,43-height,cx+7,42), fill="#171E30")
            for wy in range(46-height,41,5):
                p.point((cx+3,wy), fill="#EAC97D")
        if index == 1:
            p.rounded_rectangle((11,10,53,28), 6, fill="#DDD1EA")
            p.line((17,19,27,19), fill=NAVY, width=2)
            p.line((22,14,22,24), fill=NAVY, width=2)
            p.ellipse((37,15,41,19), fill=RED)
            p.ellipse((43,19,47,23), fill=NAVY)
        else:
            p.line((11,34,51,13), fill="#ECE0BE", width=2)
            p.line((83,5,55,12), fill="#DA7260", width=2)
            burst(p, 53, 12)
    elif index == 2:
        p.polygon([(60,0),(89,0),(89,42),(56,42),(63,32),(58,22),(68,11)],
                  fill="#789474")
        p.arc((13,4,59,40), 165, 475, fill=PAPER, width=3)
        p.arc((22,9,51,33), -45, 235, fill=NAVY, width=2)
        p.arc((30,14,45,28), 140, 450, fill=PAPER, width=2)
    elif index == 3:
        p.rectangle((0,30,89,42), fill="#95B4C4")
        for cx in (15,35,55,75):
            p.line((cx,22,cx,39), fill=NAVY, width=3)
            p.arc((cx-10,21,cx+10,36), 180,360, fill=NAVY, width=2)
        p.line((0,23,89,23), fill=NAVY, width=3)
        burst(p, 56, 19)
    elif index == 5:
        p.polygon([(0,29),(19,9),(30,23),(46,5),(66,27),(89,28),(89,42),(0,42)],
                  fill="#8DA7B8")
        p.polygon([(15,14),(19,9),(25,16),(21,15),(18,17)], fill=PAPER)
        p.polygon([(35,17),(46,5),(55,15),(48,13),(44,16),(41,13)], fill=PAPER)
        p.line((0,32,89,32), fill="#66859B")
    elif index == 6:
        p.line((26,19,52,30), fill="#755039", width=5)
        p.polygon([(15,12),(24,4),(37,18),(29,27)], fill=NAVY)
        p.rounded_rectangle((8,28,38,33), 2, fill=NAVY)
    else:
        for i in range(9):
            cx, cy = 8+i*9, 25+(i%3)*4
            color = NAVY if i % 2 else RED
            p.ellipse((cx-3,cy-5,cx+3,cy+1), fill=color)
            p.rounded_rectangle((cx-4,cy+3,cx+4,45), 3, fill=color)
            if i % 2 == 0:
                p.line((cx+2,cy+4,cx+2,10), fill=NAVY)
                p.rectangle((cx-4,6+i%3,cx+8,14+i%3), fill=PAPER, outline=NAVY)
    image.paste(art, (x,y))
    tags = {1: ("VI", 62, 9, 23, 15, PAPER), 5: ("109–0", 47, 25, 37, 11, NAVY),
            6: ("OVERTURNED", 37, 5, 52, 8, RED), 8: ("4.9%", 43, 5, 38, 12, RED)}
    if index in tags:
        label, dx, dy, width, size, color = tags[index]
        block(label, (x+dx,y+dy,width,size+1), "bold", size, 6, color,
              align="center", bounds=bounds)
    return x + art.width


def secondary_tile(index, x, y, bottom):
    kicker, headline, deck = tiles[index]
    bounds = []
    text_x = banner(index, x, y, bounds) + 8
    width = x + 312 - text_x
    gap = 2
    block(kicker, (text_x, y, width, bottom-y), "bold", 10, color=RED, bounds=bounds)
    headline_y = bounds[-1][3] + gap
    block(headline, (text_x, headline_y, width, bottom-headline_y),
          "bold", 15, color=NAVY, max_lines=2, leading=15, bounds=bounds)
    deck_y = bounds[-1][3] + gap
    block(deck, (text_x, deck_y, width, bottom-deck_y), size=11, max_lines=2, leading=12,
          bounds=bounds)
    for first, second in combinations(bounds, 2):
        left, top, right, bottom = first
        other_left, other_top, other_right, other_bottom = second
        assert (right <= other_left or other_right <= left or bottom <= other_top
                or other_bottom <= top), f"Overlapping text in tile {index + 4}"


def draw_map(x, y, width, height):
    def project(lon, lat):
        return x + (lon + 180) / 360 * width, y + (90 - lat) / 180 * height

    draw.rectangle((x,y,x+width,y+height), fill=SEA, outline=NAVY)
    for lon in range(-150,180,30):
        gx, _ = project(lon, 0)
        draw.line((gx,y+1,gx,y+height-1), fill="#BFCFD4")
    for lat in range(-60,90,30):
        _, gy = project(0, lat)
        rule(gy,x+1,x+width-1,"#BFCFD4")
    for polygon in continents:
        draw.polygon([project(*point) for point in polygon], fill=LAND, outline=NAVY)
    dots = []
    for number, point in enumerate(locations, 1):
        if point is None:
            continue
        px, py = project(*point)
        candidates = [(dx, dy) for dx in range(-35,36,3) for dy in range(-35,36,3)]
        candidates.append((0,0))
        for dx, dy in sorted(candidates, key=lambda item: sum(v*v for v in item)):
            cx, cy = px+dx, py+dy
            if (x+7 <= cx <= x+width-7 and y+7 <= cy <= y+height-7
                    and all((cx-a)**2+(cy-b)**2 >= 14**2 for _,_,_,a,b in dots)):
                dots.append((number,px,py,cx,cy))
                break
        else:
            raise AssertionError(f"No map label position for {number}")
    for _, px, py, cx, cy in dots:
        if (px,py) != (cx,cy):
            draw.line((px,py,cx,cy), fill=NAVY)
            draw.ellipse((px-1,py-1,px+1,py+1), fill=NAVY)
    for number, _, _, cx, cy in dots:
        draw.ellipse((cx-6,cy-6,cx+6,cy+6), fill=RED, outline=PAPER)
        block(str(number), (cx-6,cy-3,12,8), "bold", 8, color=PAPER, align="center")
    assert len(dots) == 31


def render():
    tracked("THE WORLD IN ONE DAY", 24, 24, 440)
    tracked("33 STORIES · EVERY CONTINENT · ALL FROM THIS ONE DAY", 480, 24, 520, True)
    rule(40, fill=RED)
    block("Thursday 19 November 2026", (24,47,976,62), "title", 62, 50, NAVY, align="center")
    block("Trump, Xi and Putin share one table · The World Court finds genocide in Myanmar · COP31's draft drops fossil fuels",
          (24,104,976,21), "italic", 21, 15, RED, align="center")
    rule(127)
    regions = [("ASIA",7),("MIDDLE EAST",5),("EUROPE",6),("AFRICA",4),
               ("AMERICAS",7),("OCEANIA",2),("GLOBAL",2)]
    assert sum(count for _, count in regions) == len(heroes)+len(tiles)+len(briefs) == 33
    for i, (name, count) in enumerate(regions):
        left = 24+i*140
        draw.rectangle((left,132,left+135,151), fill=("#E6DBCC" if i%2 else "#DFE6E5"))
        block(f"{name}  {count}", (left,136,136,12), "bold", 11, color=NAVY, align="center")
    rule(156)
    stats = [("3","presidents at one table"),("$81.3bn","Anthropic's record IPO"),
             ("200,000","evacuated ahead of Cyclone Akvan"),("109–0","Danish vote on Arctic pact"),
             ("$120bn","aid goal cut at COP31"),("4.9%","Australian jobless rate")]
    for i, (number, label) in enumerate(stats):
        left = 24 + i*163
        if i:
            draw.line((left-2,163,left-2,208), fill="#BEB5A5")
        block(number, (left,161,160,32), "title", 30, color=NAVY, align="center")
        if i == 2:
            block(label, (left+8,193,144,20), size=10, max_lines=2, leading=10,
                  align="center")
        else:
            block(label, (left+8,195,144,13), size=11, minimum=9, align="center")
    rule(214)
    for i in range(3):
        panel(i, 24 + i*332, 221)
    for i in (1,2):
        draw.line((14+i*332,221,14+i*332,500), fill="#BEB5A5")
    for i in range(len(tiles)):
        x, y = 24 + (i%3)*332, 505 + (i//3)*67
        rule(y-3, x, x+311)
        secondary_tile(i, x, y, y+64)
    rule(704)
    block("WHERE IT HAPPENED", (24,710,370,16), "bold", 14, color=NAVY)
    block("ALSO ON THURSDAY 19 NOVEMBER 2026", (430,710,570,16), "bold", 14, color=NAVY)
    draw_map(24,732,390,170)
    block("31 locations · Stories 5 and 21 cover worldwide and global news.",
          (24,909,391,14), size=10, color=GREY)
    for i, brief in enumerate(briefs):
        col, row = divmod(i,11)
        x, y = 430+col*289, 732+row*19
        number, body = brief.split(" ", 1)
        block(number, (x,y,15,11), "bold", 10, color=RED)
        block(body, (x+17,y,263,min(19, 940-y)), size=10, minimum=9,
              max_lines=2, leading=9)
    draw.rectangle((24,941,999,981), outline=RED, width=2)
    block("DATE CHECK ✓ Every story on this page happened, or was first reported, on Thursday 19 November 2026. "
          "LEFT OUT AS OTHER DAYS' NEWS: the EU's €45bn Ukraine loan plan and the House Democrats' 251–11 vote for "
          "Hakeem Jeffries (both first reported Wednesday 18 Nov).",
          (33,950,958,27), "bold", 11, max_lines=2, color=RED, leading=13)
    block("Claims are attributed, not stated as fact · Pictures and map: original, drawn in code · Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, Euronews, ABC, RNZ, Xinhua · 2026-11-19",
          (24,989,976,11), size=10, minimum=9, color=GREY, align="center")


if __name__ == "__main__":
    render()
    output = Path(__file__).with_name("entry.png")
    image.save(output, optimize=True)
    with Image.open(output) as result:
        assert result.size == (1024, 1024)
        result.verify()
    size = output.stat().st_size
    assert size < 1048576
    print(f"{output.name}: 1024×1024, {size:,} bytes, {checks} text lines checked, "
          f"zero overlaps across {len(tiles)} secondary tiles")
