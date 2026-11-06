#the code uses tturtle and tkinter to create a awindow and drow on its canvas. it works in 4 stages
#stage1: computes the hart shape (with a math fourmalss and turen it into pyolygons)
#stage2: fill the hart with words in diffrent languages(spilt  into horizonal rows and pack wprdes innto each row according to the available width)
#stage3: color the words in shades of red depennding on how close each wordes is to the center of edge 
#stage4: animate (words appear gradually (lift drop, flash) then a never-ending random shimmer starts.)


#changeing any of these valies changes the look of the result without toutching the rest of the code (so you can changed it)

import math as m              #maths: finctions(sin,cos,hypot,)for the heart shape and distance 
import random as r            #random: phrase order,font size,color,variation
import turtle as t            #creates: the drowing window and controls it
import tkinter.font as tkf    #measures: text and hight precisely before drawing

SC = 21                      #scale factor for that eniarges the hart(the fourmal is tiny by default)
OY = 20                      #vertical ooffset to  center the hart inthe window
DURATION = 10                #total time in seconds for all words appear
TICK = 16                    #milliseconds between each frames (about 60 seconds per second)
ANIM = 42                    #number of frames for each word to animate from shadow to final position
LIFT = 34                    #how far  above its final spot a word at the start before dropping
GAP = 7                      #space between tow words in the same row (in pixels)
SIZES = (9, 10, 11, 12)      #font sizes picked at random for each word (in pixels)
FONT = "Arial"               #font family (defines the style of the letters)
BG = "#040006"             #background color(near-black with a purple tint) 

s = t.Screen()               #create the main turtle window 
s.setup(800, 800)            #sets its size to 800*800 pixels
s.bgcolor(BG)                #background color and window title
s.title("Love Heart")        #same as the (BG)
s.tracer(0)                  #turns off turtles autoumatic redraw , since thee code controls drwoing itself

cv = s.getcanvas()           #gets the undelying tkinter canvas so the code can call (create_text),(itemconfing),(coords) directly, wich is faster and more flixablethan turtle commands
rng = r.Random(11)           #a random generator with a fixed seed (11) so every run produes the same layout

#useing (random(11)) istaed of the global random is why the result is repeatable. for the different layout each run, chang the number , remove it 
#the 20 "ilove you" phrases in diffrent languages (the code picks them at random to fill the hart)

#you can custem the phrases as you want 

PHRASES = [
    "I love you", "Seni seviyorum", "Te amo", "Je t'aime",
        "Ich liebe dich", "Ti amo", "Eu te amo", "Я тебя люблю",
        "사랑해", "愛してる", "我爱你", "मैं तुमसे प्यार करता हूँ",
        "Σ' αγαπώ", "Ik hou van jou", "Jag älskar dig", "Kocham cię",
        "ฉันรักเธอ", "Anh yêu em", "Aku cinta kamu", "Я тебе кохаю"
]

#(font,hart and color functions)
_fonts = {}


def font_for(size):                                                                        # returns a tkinter font object of the requested size and caches it in the (_fonts) dictionary so the same font is never created twice. A font object is needed because it can measure text with (measure)and (metrics)                            
    if size not in _fonts:                                                                 
        _fonts[size] = tkf.Font(                                                          
            root=cv, family=FONT, size=size, weight="bold"
        )
    return _fonts[size]


def heart(a):                                                                             # takes an angel a and returns a point (x,y) on the hart outling useing the classic parametic fourmal

    x = 16 * (m.sin(a) ** 3)                                                              # the result is multiplied by (SC) to enlarge it and shifted by (OY) changing the numbers in the fourmals change the hearts shape  and size
    y = (                                                                                 
        13 * m.cos(a)
        - 5 * m.cos(2 * a)
        - 2 * m.cos(3 * a)
        - m.cos(4 * a)
    )
    return x * SC, y * SC + OY


# color functions (color are (RGB)triplets with values between 0 and 1)

def hx(c):                                                                               #converts the triole into ahex color string such as #e60d24 that tkinter understands. it clamps the values to the rang 0-1 and multipplies them by 225 to convert them to the range 0-255 and then formats them as a hex string
    return "#%02x%02x%02x" % tuple(
        int(max(0, min(1, v)) * 255) for v in c
    )


def mix(a, b, k):                                                                       # this one usally to put the thing on the right place so if you change one of it maybe you will ruind all the code 
    return tuple(p + (q - p) * k for p, q in zip(a, b))                                 


def dim(c, k):
    return tuple(v * k for v in c)


POLY = [heart(2 * m.pi * i / 720) for i in range(720)]                                 # its can be used for thw range of the hart place in tthe  window or the screenS
EDGES = list(zip(POLY, POLY[1:] + POLY[:1]))
YMAX = max(p[1] for p in POLY)                                            
YMIN = min(p[1] for p in POLY)
CY = (YMAX + YMIN) / 2                   


def spans(y):
    xs = []
    for (x1, y1), (x2, y2) in EDGES:
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    xs.sort()
    return list(zip(xs[0::2], xs[1::2]))


def intersect(A, B):
    out = []
    for a in A:
        for b in B:
            lo, hi = max(a[0], b[0]), min(a[1], b[1])
            if hi - lo > 14:
                out.append((lo, hi))
    return out


def phrase_cycle():
    while True:
        order = PHRASES[:]
        rng.shuffle(order)
        yield from order


def build():
    cycle = phrase_cycle()
    row_h = max(font_for(z).metrics("linespace") for z in SIZES) + 4
    half = row_h / 2
    placed = []

    y = YMAX - half
    while y > YMIN + half:
        row = intersect(spans(y + half), spans(y - half))

        for lo, hi in row:
            lo += 4
            hi -= 4
            cur = lo + rng.uniform(0, 8)
            line = []

            while True:
                fit = None
                for _ in range(10):
                    text = next(cycle)
                    size = rng.choice(SIZES)
                    w = font_for(size).measure(text)
                    if cur + w <= hi:
                        fit = (text, size, w)
                        break
                if not fit:
                    break
                text, size, w = fit
                line.append([cur + w / 2, text, size, w])
                cur += w + GAP

            if not line:
                continue

            if len(line) > 1:
                left = hi - (line[-1][0] + line[-1][3] / 2)
                for i, it in enumerate(line):
                    it[0] += left * i / (len(line) - 1)
            else:
                line[0][0] = (lo + hi) / 2

            for i, (x, text, size, w) in enumerate(line):
                edge = i == 0 or i == len(line) - 1
                placed.append(dict(x=x, y=y, text=text, size=size, edge=edge))

        y -= row_h

    wine = (0.58, 0.0, 0.09)
    crimson = (0.90, 0.05, 0.14)
    blood = (0.98, 0.10, 0.16)
    for p in placed:
        rad = min(1.0, math_dist(p["x"], p["y"]))
        base = mix(wine, crimson, 0.25 + 0.75 * rad)
        base = mix(base, blood, rng.uniform(0, 0.35) + (0.3 if p["edge"] else 0))
        p["color"] = tuple(min(1, v) for v in base)
        p["rad"] = rad

    edges = [p for p in placed if p["edge"]]
    inner = [p for p in placed if not p["edge"]]
    edges.sort(key=lambda p: m.atan2(p["x"], p["y"] - CY) % (2 * m.pi))
    inner.sort(key=lambda p: -p["rad"] + rng.uniform(0, 0.08))
    return edges + inner


def math_dist(x, y):
    return m.hypot(x / (16 * SC), (y - CY) / (14.5 * SC))


FLASH = (1.0, 0.78, 0.78)
main_ids = []
active = []
tick_no = 0


def clamp(v):
    return max(0.0, min(1.0, v))


def spawn(p):
    x, y = p["x"], -p["y"]
    size, text, c = p["size"], p["text"], p["color"]
    font = (FONT, size, "bold")
    big = (FONT, size + 1, "bold")

    shadow = cv.create_text(x + 2, y + 3, text=text, font=font, fill=BG)
    halo = cv.create_text(x, y, text=text, font=big, fill=BG)
    main = cv.create_text(x, y - LIFT, text=text, font=font, fill=BG)

    p.update(shadow=shadow, halo=halo, main=main,
             f=0, dx=rng.uniform(-10, 10))
    main_ids.append((main, c))
    active.append(p)


def animate(p):
    p["f"] += 1
    u = clamp(p["f"] / ANIM)
    e = 1 - (1 - u) ** 3
    c = p["color"]
    x, y = p["x"], -p["y"]
    hover = (1 - e) * LIFT
    px = x + p["dx"] * (1 - e)
    py = y - hover

    cv.itemconfig(p["shadow"], fill=hx(mix(BGC, dim(c, 0.30), e)))
    cv.itemconfig(p["halo"], fill=hx(mix(BGC, dim(c, 0.20), e * e)))
    cv.coords(p["halo"], px, py)

    flash = 0.75 * math_sin(clamp((u - 0.55) / 0.45))
    col = mix(mix(BGC, c, e ** 1.5), FLASH, flash)
    cv.itemconfig(p["main"], fill=hx(col))
    cv.coords(p["main"], px, py)

    if u >= 1:
        cv.coords(p["halo"], x, y)
        cv.coords(p["main"], x, y)
        cv.itemconfig(p["main"], fill=hx(c))
        return False
    return True


def math_sin(v):
    return m.sin(m.pi * v)


BGC = tuple(int(BG[i:i + 2], 16) / 255 for i in (1, 3, 5))
ORDER = build()
items = iter(ORDER)
RATE = len(ORDER) / (DURATION * 1000 / TICK)
acc = 0.0
spawning = True


def step():
    global spawning, acc
    if spawning:
        acc += RATE
        try:
            while acc >= 1:
                acc -= 1
                spawn(next(items))
        except StopIteration:
            spawning = False

    active[:] = [p for p in active if animate(p)]

    if not spawning and not active:
        shimmer()
        return
    cv.after(TICK, step)


def _safe(i, c):
    try:
        cv.itemconfig(i, fill=hx(c))
    except Exception:
        pass


def shimmer():
    for _ in range(1):
        i, c = rng.choice(main_ids)
        _safe(i, mix(c, FLASH, 0.6))
        cv.after(260, lambda i=i, c=c: _safe(i, c))
    cv.after(140, shimmer)


try:
    cv.after(200, step)
    t.done()
except (t.Terminator, Exception):
    pass