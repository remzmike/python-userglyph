# todo:
#http://www.gravatar.com/avatar/4f2c66bad7d8be89d32ff1030fbf2887?s=128&d=identicon&r=PG
#http://www.gravatar.com/avatar/f146f9cee79cd2dc8bceff7f1191ce09?s=128&d=identicon&r=PG
#http://i2.asp.net/fan-cdn/avatar/CLprogrammer.jpg?forceidenticon=False&dt=634910875800000000&cdn_id=2012-11-20-h19

# wish: maybe the mids has least variety, or maybe they are a high place
# wish: obfuscate the ordering with mod cycle technique, don't care for now
# blog: look familiar?
# http://en.wikipedia.org/wiki/Natural_Color_System

from __future__ import division
import math, cairo
from math import ceil, floor
from colorsys import hls_to_rgb

r0 = (1,0), (0,1)
t0 = (0,0)
r90 = (0,-1), (1,0)
t90 = (1,0)
r180 = (-1,0), (0,-1)
t180 = (1,1)
r270 = (0,1), (-1,0)
t270 = (0,1)
mrotates=[r0,r90,r180,r270]
mtranslates=[t0,t90,t180,t270]

def deg2rad(deg):
    return deg * math.pi / 180
assert int(deg2rad(360))==6

def normcolor(r,g,b):
    return (r/255, g/255, b/255)

# matrix transform
def transform(pt, rotate=r0, translate=t0):
    assert len(pt) == 2
    x = pt[0] * rotate[0][0] + pt[1] * rotate[0][1]
    y = pt[0] * rotate[1][0] + pt[1] * rotate[1][1]
    x = x + translate[0]
    y = y + translate[1]
    return x, y

class Glyph:
    def __init__(o, shape, rotate=0, flip_bg=False):
        # wish: support multiple shapes per glyph, to allow double spotlight
        o.shape = shape
        o.rotate = rotate
        o.flip_bg = flip_bg
    def get_polys(o):
        mrotate = mrotates[o.rotate]
        mtranslate = mtranslates[o.rotate]
        polys = []
        for poly in o.shape:
            newpoly = []
            for pt in poly:
                newpt = transform(pt,mrotate,mtranslate)
                newpoly.append(newpt)
            polys.append(newpoly)
        return polys

# make glyphs with rotate & bg/fg flip
def make_glyphs(shape, rotates=3, use_flip_bg=True):
    result = []
    for i in range(rotates+1):
        mrotate = mrotates[i]
        result.append(Glyph(shape, i))
        if use_flip_bg:
            result.append(Glyph(shape, i, True))
    return result

# return tuple id (inner, mid, corner, color)
def int2id(x):
    bases = [len(inners), len(mids), len(corners), len(colors)]
    bases.reverse()
    basei = 0
    result = []
    while x != 0:
        base = bases[basei]
        r = x % base
        x = x // base
        result.append(r)        
        basei += 1    
    pad = 4 - len(result) # pad with zero
    result.extend([0]*pad) # [0]*-1 = []
    result.reverse()
    return tuple(result)

def test():
    global inners, mids, corners, colors
    _inners, _mids, _corners, _colors = inners, mids, corners, colors
    inners = range(12*4)
    mids = range(12*4)
    corners = range(12*4)
    colors = range(20)    
    assert int2id(0) == (0,0,0,0)
    assert int2id(1) == (0,0,0,1)
    assert int2id(19) == (0,0,0,19)
    assert int2id(20) == (0,0,1,0)
    assert int2id(48) == (0,0,2,8)
    assert int2id(48*48*20) == (1,0,0,0)
    assert int2id(48*48*20-1) == (0,47,47,19)
    inners, mids, corners, colors = _inners, _mids, _corners, _colors
    assert transform((0.38,.42)) == (0.38,0.42)    
    assert transform((0,.75), r90) == (-.75,0)    
    assert transform((0,.75), r90, t90) == (1-.75,0)
    assert transform((.75,0), r90, t90) == (1,.75)
    assert transform((.75,.5), r90, t90) == (.5,.75)
    assert transform((0.5,0), r90, t90) == (1,0.5)

def draw_and_save(x):
    id = int2id(x)
    #print 'drawing #{0}, id = {1}'.format(x, id)
    img = draw(id)
    idstr = '_'.join([format(x, '03d') for x in id])
    fn = 'userglyph-{0}.png'.format(idstr)
    fpath = 'images\\'+fn
    img.write_to_png(fpath)
    return fpath

def draw(id):
    inneri, midi, corneri, colori = id    
    inner, mid, corner, color = inners[inneri], mids[midi], corners[corneri], colors[colori]
    
    size = 64
    
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    cr = cairo.Context(img)

    # draw one quadrant, transform, redraw
    # wish: path preservation
    cr.scale(size/2, size/2)
    
    transforms = [
        [(1,0),  0], # top right
        [(2,1), 90], # bot right
        [(1,2),180], # bot left
        [(0,1),270], # top left
    ]
    for tx, rx in transforms:
        cr.save()
        cr.translate(*tx)
        cr.rotate(deg2rad(rx))
        draw_quadrant(cr, inner, mid, corner, color)
        cr.restore()        
            
    return img

def draw_quadrant(cr, inner, mid, corner, color):
    
    cr.save() # 32

    cr.scale(0.5,0.5)
    
    # draw inner
    cr.save()
    cr.translate(0,1)    
    draw_glyph(cr, inner, color)
    cr.restore()
    # draw mid 1
    cr.save()
    draw_glyph(cr, mid, color)
    cr.restore()
    # draw mid 2
    cr.save()
    cr.translate(2,1)
    cr.rotate(deg2rad(90))    
    draw_glyph(cr, mid, color)
    cr.restore()
    # draw corner
    cr.save()
    cr.translate(1,0)
    draw_glyph(cr, corner, color)
    cr.restore()

    cr.restore() # 32

def draw_glyph(cr, glyph, color):
    cr.save()

    bg = (1,1,1)
    fg = color
    if glyph.flip_bg:
        bg, fg = fg, bg    
    
    cr.set_source_rgb(*bg)
    cr.rectangle(0,0,1,1)
    cr.fill()

    cr.set_source_rgb(*fg)

    cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    for poly in glyph.get_polys():
        assert type(poly) == list
        if len(poly)>0:
            start = poly[0]
            cr.move_to(*start)
        for point in poly:
            cr.line_to(*point)
        cr.close_path()
    cr.fill()
    
    cr.restore()

def draw_and_save_glyphset():
    scale = 32
    pad = 2
    scalepad = scale + pad
    cols = 8
    rows = int( ceil( len(glyphs) / cols ) )
    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, scalepad*cols+pad, scalepad*rows+pad)
    cr = cairo.Context(img)        
    cr.set_source_rgb(0.3,0.3,0.3)
    cr.paint()
                        
    cr.scale(scale,scale)
    for i,glyph in enumerate(glyphs):
        x = i % cols
        y = floor( i / cols )
        cr.save()
        cr.translate(x*scalepad/scale+pad/scale,y*scalepad/scale+pad/scale)
        draw_glyph(cr,glyph,(0,0.5,0.7))
        cr.restore()
        
    img.write_to_png('_glyphset.png')

# ---

# points on 4x4 grid
xvalues = [0,.25,.5,.75,1]
a0, a1, a2, a3, a4 = [(x,0.00) for x in xvalues]
b0, b1, b2, b3, b4 = [(x,0.25) for x in xvalues]
c0, c1, c2, c3, c4 = [(x,0.50) for x in xvalues]
d0, d1, d2, d3, d4 = [(x,0.75) for x in xvalues]
e0, e1, e2, e3, e4 = [(x,1.00) for x in xvalues]

glyphs = []
glyphs.extend(
    # +0, but still flip bg
    make_glyphs( [[b1,b3,d3,d1]], 0 ) + # square
    make_glyphs( [[b2,c3,d2,c1]], 0 ) + # diamond    
    make_glyphs( [[a2,c4,e2,c0],[b2,c3,d2,c1]], 0 ) + # hollow diamond    
    #make_glyphs( [[a2,(.125*5,.125*3),c4,(5*.125,5*.125),e2,(3*.125,5*.125),c0,(3*.125,3*.125)]], 0 ) + # elusive star
    make_glyphs( [[a0,b2,a4,c3,e4,d2,e0,c1]], 0 ) + # angled star
    make_glyphs( [[a0,b2,c1],[b2,a4,c3],[c3,e4,d2],[d2,e0,c1]], 0 ) + # hollow star
    make_glyphs( [[a0,a4,c2,e4,e0,c2]], 0 ) + # hourglass
    # skipping checker
    # +1    
    make_glyphs( [[a0,a4,c3,e4,e0,c1]], 1) + # fat hourglass
    make_glyphs( [[e0,b1,a4,d3]], 1) + # slant diamond
    make_glyphs( [[e0,b1,d3]], 1) + # half slant diamond
    make_glyphs( [[a2,c3,e2,c1]], 1) + # long diamond
    #~make_glyphs( [[a2,c3,c1]], 1) + # half long diamond # ambiguous mid
    make_glyphs( [[e0,b1,a4,d3],[b2,c3,d2,c1]], 1) + # hollow slant diamond
    #~make_glyphs( [[a2,b3,c2,b1]], 1) + # midtop diamond # ambiguous mid
    #~make_glyphs( [[c2,d3,e2,d1]], 1) + # midbot diamond # ambiguous mid
    make_glyphs( [[a1,b2,c1,b0],[c3,d4,e3,d2]], 1) + # diagonal diamonds
    make_glyphs( [[a0,a2,c1],[a2,a4,c3],[e0,c1,e2],[e2,c3,e4]], 1 ) + # double hourglass
    #~make_glyphs( [[a2,b3,c2,b1],[c2,d3,e2,d1]], 1) + # midtop+midbot diamond # ambiguous mid
    make_glyphs( [[e0,a4,e4]], 1) + # full right tri
    make_glyphs( [[a0,a2,b2,c0],[d2,c4,e4,e2]], 1) + # offset passage
    make_glyphs( [[c0,c4,e4,e0]], 1 ) + # full half-square
    make_glyphs( [[a0,a2,e4,e2]], 1 ) + # slant bar down
    make_glyphs( [[a2,a4,e2,e0]], 1 ) + # slant bar up
    make_glyphs( [[a0,a2,c0],[e2,c4,e4]], 1 ) + # opposing corner medium tris
    # +3
    make_glyphs( [[a0,c4,e4,e2]] ) + # spotlight
    make_glyphs( [[a0,c4,e2]] ) + # side tri    
    make_glyphs( [[a0,e4,c0]] ) + # thick sliver top
    make_glyphs( [[c0,a4,e0]] ) + # thick sliver bot
    make_glyphs( [[a0,a4,c0]] ) + # top long flag
    make_glyphs( [[c0,c4,e0]] ) + # bot long flag
    make_glyphs( [[a0,a4,c0],[c0,c4,e0]] ) + # double flags
    make_glyphs( [[a0,a2,c0],[c0,c4,e0]] ) + # double flags, top smaller    
    make_glyphs( [[a0,a4,c0],[c0,c2,e0]] ) + # double flags, bottom smaller        
    make_glyphs( [[a0,c2,c0]] ) + # top 1st tri
    make_glyphs( [[c0,e2,e0]] ) + # bot 1st tri
    make_glyphs( [[a0,c2,c0],[c0,e2,e0]] ) + # top+bot 1st tri
    make_glyphs( [[a0,a2,c0]] ) + # top 2nd tri
    make_glyphs( [[c0,c2,e0]] ) + # bot 2nd tri
    make_glyphs( [[a0,a2,c0],[c0,c2,e0]] ) + # top+bot 2nd tri
    make_glyphs( [[a0,a2,c2]] ) + # top 3rd tri
    make_glyphs( [[c0,c2,e2]] ) + # bot 3rd tri
    make_glyphs( [[a0,a2,c2],[c0,c2,e2]] ) + # top+bot 3rd tri
    make_glyphs( [[a2,c2,c0]] ) + # top 4th tri
    make_glyphs( [[c2,e2,e0]] ) + # bot 4th tri
    make_glyphs( [[a2,c2,c0],[c2,e2,e0]] ) + # top+bot 4th tri
    
    #~make_glyphs( [[a2,a4,c2],[c0,c2,e0],[c2,c4,e2]] ) + # 3 tris 
    #~make_glyphs( [[a2,a4,c2],[c0,c2,e0],[c2,c4,e2],[a0,a2,c0]] ) + # 4 tris 
    make_glyphs( [[a0,c2,e0]] ) + # left fat tri    
    make_glyphs( [[a2,c4,e2]] ) + # right fat tri    
    make_glyphs( [[a0,c2,e0],[a2,c4,e2]] ) + # left+right fat tri    
    #make_glyphs( [a0,a2,e4],[e0,a4,e2] ), # dual spotlight, wish: shapelist support
    #~make_glyphs( [[a2,c4,e2,c0,c1,d2,c3,b2]] ) + # tuning
    # tri joint is good, but not generic enough, clashes
    # probably try not to end/start edges on odd rows/cols
    #~make_glyphs( [[d0,a3,a4,b4,c3,d4,e4,e3,d2,e1,e0],[a0,a1,b0]] ) + # tri-joint deluxe
    #~make_glyphs( [[b0,a1,b2,b3,c3,d4,e3,e1,d2,c1,d0]] ) + # invader
    #~make_glyphs( [[a0,a1,b1,c2,d2,e3,e0]] ) + # irregular steppe    
    make_glyphs( [[e0,c0,a2,c4,e4]] ) + # house    
    make_glyphs( [[e0,a2,e4]] ) + # pyramid      
    make_glyphs( [[e0,a2,e4],[c1,c3,e2]] ) + # triforce    
    make_glyphs( [[e0,c1,c3,e4]] ) + # pyramid cut
    make_glyphs( [[a0,c2,c0],[c2,e4,e2]] ) + # duo diag tris 1
    make_glyphs( [[a0,a2,c0],[c2,c4,e2]] ) + # duo diag tris 2
    make_glyphs( [[a0,c2,c0],[c2,c4,e2]] ) + # duo diag tris 1&2
    make_glyphs( [[a0,a2,c0],[c2,e4,e2]] ) + # duo diag tris 2&1
    #make_glyphs( [[a0,a2,c2],[c2,c4,e4]] ) + # duo diag tris 3 # dupe
    #make_glyphs( [[a2,c2,c0],[c4,e4,e2]] ) + # duo diag tris 4 # dupe   
    make_glyphs( [[a0,a2,c4,e4,e2,d2,c1,c0]] ) + # turn
    make_glyphs( [[a1,b2,c1,b0]] ) + # top diamond
    make_glyphs( [[c1,d2,e1,d0]] ) + # bot diamond
    make_glyphs( [[a1,b2,c1,b0],[c1,d2,e1,d0]] ) + # top+bot diamond
    make_glyphs( [[a0,b1,c0]] ) + # top horn
    make_glyphs( [[c0,d1,e0]] ) + # bot switch
    make_glyphs( [[a0,b1,c0],[c0,d1,e0]] ) + # top+bot horn
    make_glyphs( [[c0,a1,c2]] ) + # top pyramid 1
    make_glyphs( [[e0,c1,e2]] ) + # bot pyramid 1
    make_glyphs( [[c0,a1,c2],[e0,c1,e2]] ) + # top+bot pyramid 1
    make_glyphs( [[a0,b2,c0]] ) + # top pyramid 2
    make_glyphs( [[c0,d2,e0]] ) + # bot pyramid 2
    make_glyphs( [[a0,b2,c0],[c0,d2,e0]] ) + # top+bot pyramid 2
    make_glyphs( [[a0,a2,c1]] ) + # top pyramid 3
    make_glyphs( [[c0,c2,e1]] ) + # bot pyramid 3
    make_glyphs( [[a0,a2,c1],[c0,c2,e1]] ) + # top+bot pyramid 3
    make_glyphs( [[a2,c2,b0]] ) + # top pyramid 4
    make_glyphs( [[c2,e2,d0]] ) + # bot pyramid 4
    make_glyphs( [[a2,c2,b0],[c2,e2,d0]] ) + # top+bot pyramid 4
    make_glyphs( [[a0,a2,c2,e4,e0]] ) + # boot
    make_glyphs( [[a0,a2,c2,c0],[c0,e2,e0]] ) + # top block + bot tri 1
    make_glyphs( [[a0,a2,c2,c0],[c0,c2,e0]] ) + # top block + bot tri 2
    make_glyphs( [[a0,a2,c2,c0],[c0,c2,e2]] ) + # top block + bot tri 3
    make_glyphs( [[a0,a2,c2,c0],[c2,e2,e0]] ) + # top block + bot tri 4
    make_glyphs( [[a0,a2,c2,c0]] ) + # top block
    make_glyphs( [[c0,c2,e2,e0]] ) + # bot block
    make_glyphs( [[a0,a2,b2,c1,c0]] ) + # top cut block
    make_glyphs( [[c0,c2,d2,e1,e0]] ) + # bot cut block
    make_glyphs( [[a0,a2,b2,c1,c0],[c0,c2,d2,e1,e0]] ) + # bot+top cut block
    []
)

inners = glyphs
mids = glyphs
corners = glyphs
#colors = [
#    normcolor(236,208,120),
#    normcolor(192,41,66),
#    normcolor(83,119,122),
#    (0,0.5,0.7),
#]
colors = []
for hue in [0, 25, 50, 75, 120, 150, 180, 200, 220, 260, 280, 300, 320]:
    h = hue / 360
    s = 0.8
    light_range = 2
    for light in range(light_range):
        l = .25 + (light+1)/light_range * .4
        color = hls_to_rgb(h,l,s)
        colors.append(color)

combinations = len(inners) * len(mids) * len(corners) * len(colors)

if __name__=='__main__':
    import os        
    test()
    print "{:,} combinations".format(combinations) # dont work in 2.6.5
    draw_and_save_glyphset()    
    os.system('start _glyphset.png')
    if True:
        count = min(727,combinations)
        for i in range(count):
            x = int(i/count * combinations)
            fpath = draw_and_save(x)
        os.system('start {0}'.format(fpath))
    
    if False:
        count = len(colors) * 10
        for i in range(count):
            fpath = draw_and_save(i)
        os.system('start {0}'.format(fpath))

    # 20 base shapes, 4 colors = 5 million glyphs