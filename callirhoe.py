#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

#    callirhoe - high quality calendar rendering
#    Copyright (C) 2012 George M. Tzoumas

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/

# TODO:

# allow to change background color (fill), other than white
# mobile themes (e.g. 800x480)
# photo support
# implement DATA SOURCES
# python source documentation
# .callirhoe/config : default values for plugins (styles/layouts/lang...) and cmdline

# MAYBE-TODO:
# auto-landscape? should aim for matrix or bars?
# allow /usr/bin/date-like formatting %x... 
# improve file matching with __init__ when lang known
# styles and geometries could be merged, css-like
#  then we can apply a chain of --style a --style b ...
#  and b inherits from a and so on
#  however, this would require dynamically creating a class that inherits from others...

# CANNOT UPGRADE TO argparse !!! -- how to handle [[month] year] form?

_version = "0.2.1.r15"

import calendar
import sys
import time
import optparse
import lib.xcairo as xcairo

from lib.plugin import *
# TODO: SEE IF IT CAN BE MOVED INTO lib.plugin ...
def import_plugin(cat, longcat, longcat2, listopt, preset):
    try:
        found = available_files(plugin_path[0], cat, preset) + available_files(plugin_path[1], cat, preset)
        if len(found) == 0: raise IOError
        old = sys.path[0];
        sys.path[0] = found[0][1]
        m = __import__("%s.%s" % (cat,preset), globals(), locals(), [ "*" ])
        sys.path[0] = old
        return m
    except IOError:
        print >> sys.stderr, "%s definition `%s' not found, use %s to see available definitions" % (longcat,
                               preset,listopt)
        sys.exit(1)
    except ImportError:
        print >> sys.stderr, "error loading %s definition `%s'" % (longcat, preset)
        sys.exit(1)

parser = optparse.OptionParser(usage="usage: %prog [options] [[MONTH[-MONTH2|:SPAN]] YEAR] FILE", 
       description="""High quality calendar rendering with vector graphics.
By default, a calendar of the current year in pdf format is written to FILE.
Alternatively, you can select a specific YEAR (0=current), 
and a month range from MONTH (0-12, 0=current) to MONTH2 or for SPAN months.
""", version="callirhoe " + _version)
parser.add_option("-l", "--lang",  dest="lang", default="EN",
                help="choose language [%default]")
parser.add_option("-t", "--layout",  dest="layout", default="classic",
                help="choose layout [%default]")
parser.add_option("-H", "--layout-help",  dest="layouthelp", action="store_true", default=False,
                help="show layout-specific help")
parser.add_option("--examples", dest="examples", action="store_true",
                help="display some usage examples")
parser.add_option("-s", "--style",  dest="style", default="default",
                help="choose style [%default]")
parser.add_option("-g", "--geometry",  dest="geom", default="default",
                help="choose geometry [%default]")
parser.add_option("--landscape", action="store_true", dest="landscape", default=False,
                help="landscape mode")
parser.add_option("--dpi", type="float", default=72.0,
                help="set DPI (for raster output) [%default]")
parser.add_option("--paper", default="a4",
                help="set paper type; PAPER can be an ISO paper type (a0..a9) or of the "
                "form W:H; positive values correspond to W or H mm, negative values correspond to "
                "-W or -H pixels [%default]")
parser.add_option("--border", type="float", default=3,
                help="set border size (in mm) [%default]")

def print_examples():
    print """Examples:

Create a calendar of the current year (by default in a 4x3 grid):
    $ callirhoe my_calendar.pdf 

Same as above, but in landscape mode (3x4):
    $ callirhoe --landscape my_calendar.pdf 

Forcing 1 row only, we get month bars instead of boxes:
    $ callirhoe --landscape --rows=1 my_calendar.pdf
    
Calendar of 24 consecutive months, starting from current month:
    $ callirhoe 0:24 0 my_calendar.pdf
    
Create a 600-dpi PNG file so that we can edit it with some effects in order to print an A3 poster:
    $ callirhoe my_poster.png --paper=a3 --dpi=600 --opaque

Create a calendar as a full-hd wallpaper (1920x1080):
    $ callirhoe wallpaper.png --paper=-1920:-1080 --opaque --rows=3 --no-shadow -s rainbow-gfs
and do some magic with ImageMagick! ;)
    $ convert wallpaper.png -negate fancy.png
    
"""

def add_list_option(parser, opt):
    parser.add_option("--list-%s" % opt, action="store_true", dest="list_%s" % opt, default=False,
                       help="list available %s" % opt)
for x in ["languages", "layouts", "styles", "geometries"]:
    add_list_option(parser, x)

parser.add_option("--lang-var", action="append", dest="lang_assign",
                help="modify a language variable")
parser.add_option("--style-var", action="append", dest="style_assign",
                help="modify a style variable, e.g. dom.frame_thickness=0")
parser.add_option("--geom-var", action="append", dest="geom_assign",
                help="modify a geometry variable")

argv1 = []
argv2 = []
for x in sys.argv:
     y = x[0:x.find('=')] if '=' in x else x 
     if x[0] == '-' and not parser.has_option(y):
         argv2.append(x)
     else:
         argv1.append(x)
sys.argv = argv1
        
(options,args) = parser.parse_args()

if options.list_languages:
    for x in plugin_list("lang"): print x[0],
    print
if options.list_styles:
    for x in plugin_list("style"): print x[0],
    print
if options.list_geometries:
    for x in plugin_list("geom"): print x[0],
    print
if options.list_layouts:
    for x in plugin_list("layouts"): print x[0],
    print
if (options.list_languages or options.list_styles or
    options.list_geometries or options.list_layouts): sys.exit(0)    

Language = import_plugin("lang", "language", "languages", "--list-languages", options.lang)
Style = import_plugin("style", "style", "styles", "--list-styles", options.style)
Geometry = import_plugin("geom", "geometry", "geometries", "--list-geometries", options.geom)
Layout = import_plugin("layouts", "layout", "layouts", "--list-layouts", options.layout)

for x in argv2:
    if '=' in x: x = x[0:x.find('=')]
    if not Layout.parser.has_option(x):
        parser.error("invalid option %s; use --help (-h) or --layout-help (-H) to see available options" % x)

(Layout.options,largs) = Layout.parser.parse_args(argv2)
if options.layouthelp:
    #print "Help for layout:", options.layout
    Layout.parser.print_help()
    sys.exit(0)

if options.examples:
    print_examples()
    sys.exit(0)

# we can put it separately together with Layout; but we load Layout *after* lang,style,geom
if len(args) < 1 or len(args) > 3:
    parser.print_help()
    sys.exit(0)

#if (len(args[-1]) == 4 and args[-1].isdigit()):
#    print "WARNING: file name `%s' looks like a year, writing anyway..." % args[-1]

# the usual "beware of exec()" crap applies here... but come on, 
# this is a SCRIPTING language, you can always hack the source code!!!
if options.lang_assign:
    for x in options.lang_assign: exec "Language.%s" % x
if options.style_assign:
    for x in options.style_assign: exec "Style.%s" % x
if options.geom_assign:
    for x in options.geom_assign: exec "Geometry.%s" % x

calendar.month_name = Language.month_name
calendar.day_name = Language.day_name

def get_orthodox_easter(y):
    y1, y2, y3 = y - y//4 * 4, y - y//7 * 7, y - y//19 * 19
    a = 19*y3 + 15
    y4 = a - a//30 * 30
    b = 2*y1 + 4*y2 + 6*(y4 + 1)
    y5 = b - b/7 * 7
    r = 1 + 3 + y4 + y5;
    return (5, r - 30) if r > 30 else (4,r)

def itoa(s):
    try:
        k = int(s);
    except ValueError as e:
        sys.exit("invalid integer value `" + s +"'")
    return k

def parse_month(mstr):
    m = itoa(mstr)
    if m < 1: m = time.localtime()[1]
    elif m > 12: sys.exit("invalid month value `" + str(mstr) + "'")
    return m

def parse_year(ystr):
    y = itoa(ystr)
    if y == 0: y = time.localtime()[0]
    return y

if len(args) == 1:
    Year = time.localtime()[0]
    Month, MonthSpan = 1, 12
    Outfile = args[0]
elif len(args) == 2:
    Year = parse_year(args[0])
    Month, MonthSpan = 1, 12
    Outfile = args[1]
elif len(args) == 3:
    if ':' in args[0]:
        t = args[0].split(':')
        if len(t) != 2: sys.exit("invalid month range `" + args[0] + "'")
        Month = parse_month(t[0])
        MonthSpan = itoa(t[1])
        if MonthSpan < 0: sys.exit("invalid month range `" + args[0] + "'")
    elif '-' in args[0]:
        t = args[0].split('-')
        if len(t) != 2: sys.exit("invalid month range `" + args[0] + "'")
        Month = parse_month(t[0])
        MonthSpan = itoa(t[1]) - Month + 1
        if MonthSpan < 0: sys.exit("invalid month range `" + args[0] + "'")
    else:
        Month = parse_month(args[0])
        MonthSpan = 1
    Year = parse_year(args[1])
    Outfile = args[2]

Geometry.landscape = options.landscape
xcairo.XDPI = options.dpi
Geometry.pagespec = options.paper
Geometry.border = options.border

Layout.draw_calendar(Outfile, Year, Month, MonthSpan, (Style,Geometry), _version)
