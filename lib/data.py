# -*- coding: utf-8 -*-

#    callirhoe - high quality calendar rendering
#    Copyright (C) 2012-2013 George M. Tzoumas

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

# *****************************************
#                                         #
"""      ics data support routines      """
#                                         #
# *****************************************

from datetime import date
from icalendar import Calendar, Event
from pytz import UTC

def _strip_empty(sl):
    """strip empty strings from list I{sl}

    @rtype: [str,...]
    """
    return [z for z in sl if z] if sl else []

def _flatten(sl):
    """join list I{sl} into a comma-separated string

    @rtype: str
    """
    if not sl: return None
    return ', '.join(sl)

class Date(object):
    """class holding a Date object (date is I{not} stored, use L{DateProvider} for that)

    @ivar str_list: string list
    """
    def __init__(self, str_list = []):
        self.str_list = str_list.copy()

    def merge_with(self, date_list):
        """merge a list of holiday objects into this object"""
        for d in date_list:
            self.str_list.extend(d.str_list)

    def text(self):
        """return a comma-separated string for L{header_list}

        @rtype: str
        """
        return _flatten(self.str_list)

    def __str__(self) :
        if(self.str_list): return "<Date " + self.text() + ">"
        else: return "<Date None>"

class DataProvider(object):
    """class holding the holidays throught the year(s)

    
    @ivar fixed: fixed date events, indexed by a C{date()} object
    @ivar cache: for each year requested, all dates occuring
    within that year are precomputed and stored into
    dict C{cache}, indexed by a C{date()} object
    @ivar ycache: set holding cached years; each new year requested, triggers a cache-fill
    operation
    """
    def __init__(self, style):
        """initialize a C{DataProvider} object

        @param style: draw style
        """
        self.fixed = dict() # key = date()
        self.cache = dict() # key = date()
        self.ycache = set() # key = year
        self.style = style
    
    def load_data_file(self, filename) :
        with open(filename,'rb') as f:
            gcal = Calendar.from_ical(f.read())
            for component in gcal.walk():
                if component.name == "VEVENT":
                    event_name = component.get('summary')
                    dt = component.get('dtstart').dt
                    entry = Date([event_name])
                    if dt not in self.fixed: self.fixed[dt] = []
                    self.fixed[dt].append(entry)
        return

    def get_date(self, y, m, d):
        """return a L{Date} object for the specified date (y,m,d) or C{None} if no holiday is defined

        @rtype: Date
        @note: If year I{y} has not been requested before, the cache is updated first
        with all holidays that belong in I{y}, indexed by C{date()} objects.
        """
        if y not in self.ycache:
            # fill-in events for year y
            # fixed
            for dt in [z for z in self.fixed if z.year == y]:
                if not dt in self.cache: self.cache[dt] = Date()
                self.cache[dt].merge_with(self.fixed[dt])

            self.ycache.add(y)

        dt = date(y,m,d)
        return self.cache[dt] if dt in self.cache else None

    def __call__(self, year, month, dom, dow):
        """returns (header,footer,day_style)

        @rtype: (str,str,Style)
        @param month: month (0-12)
        @param dom: day of month (1-31)
        @param dow: day of week (0-6)
        """
        hol = self.get_date(year,month,dom)
        if hol:
            return (hol.text(), self.style)
        else:
            return (None, self.style)
