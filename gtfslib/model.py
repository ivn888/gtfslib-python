# -*- coding: utf-8 -*-
#    This file is part of Gtfslib-python.
#
#    Gtfslib-python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Gtfslib-python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with gtfslib-python.  If not, see <http://www.gnu.org/licenses/>.
import six
"""
@author: Laurent GRÉGOIRE <laurent.gregoire@mecatran.com>
"""

import datetime
from functools import total_ordering


class FeedInfo(object):
    
    def __init__(self, feed_id):
        self.feed_id = feed_id

    def __repr__(self):
        return "<%s(id=%s)>" % (
                self.__class__.__name__, self.feed_id)

class Agency(object):
    
    def __init__(self, feed_id, agency_id, agency_name, agency_url, agency_timezone, **kwargs):
        self.feed_id = feed_id
        self.agency_id = agency_id
        self.agency_name = agency_name
        self.agency_url = agency_url
        self.agency_timezone = agency_timezone
        for key in kwargs:
            setattr(self, key, kwargs[key])
        
    def __repr__(self):
        return "<%s(id=%s/%s, %s)>" % (
                self.__class__.__name__, self.feed_id, self.agency_id, _public_vars(self))

class Stop(object):
    
    TYPE_STOP = 0
    TYPE_STATION = 1
    
    WHEELCHAIR_UNKNOWN = 0
    WHEELCHAIR_YES = 1
    WHEELCHAIR_NO = 2

    def __init__(self, feed_id, stop_id, stop_name, stop_lat, stop_lon,
                 location_type=TYPE_STOP,
                 parent_station_id=None,
                 wheelchair_boarding=WHEELCHAIR_UNKNOWN, **kwargs):
        self.feed_id = feed_id
        self.stop_id = stop_id
        self.location_type = location_type
        self.stop_name = stop_name
        self.stop_lat = stop_lat
        self.stop_lon = stop_lon
        self.parent_station_id = parent_station_id
        self.wheelchair_boarding = wheelchair_boarding
        for key in kwargs:
            setattr(self, key, kwargs[key])
            
    def lat(self):
        return self.stop_lat

    def lon(self):
        return self.stop_lon

    def __repr__(self):
        return "<%s(id=%s/%s, %s)>" % (
                self.__class__.__name__, self.feed_id, self.stop_id, _public_vars(self))

class Route(object):
    
    # TODO types
    TYPE_BUS = 3
    
    def __init__(self, feed_id, route_id, agency_id, route_type, **kwargs):
        self.feed_id = feed_id
        self.route_id = route_id
        self.agency_id = agency_id
        self.route_type = route_type
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __repr__(self):
        return "<%s(id=%s/%s, %s)>" % (
                self.__class__.__name__, self.feed_id, self.route_id, _public_vars(self))

class Calendar(object):
    
    def __init__(self, feed_id, service_id):
        self.feed_id = feed_id
        self.service_id = service_id
        
    def __repr__(self):
        return "<%s(id=%s/%s)>" % (
                self.__class__.__name__, self.feed_id, self.service_id)

@total_ordering
class CalendarDate(object):

    def __init__(self, date):
        self.feed_id = None
        self.date = date
        
    @classmethod
    def ymd(cls, year, month, day):
        return cls(datetime.date(year, month, day))
    
    @classmethod
    def fromYYYYMMDD(cls, yyyymmdd):
        return cls.ymd(int(yyyymmdd[:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))

    @classmethod
    def range(cls, start, end):
        cursor = start
        while cursor < end:
            yield cursor
            cursor = cursor.next_day()
            
    def next_day(self, ndays=1):
        return CalendarDate(self.date + datetime.timedelta(days=ndays))
    
    def dow(self):
        return self.date.weekday()
    
    def _coerce(self, other):
        if isinstance(other, str):
            ymd = other.split("-")
            return datetime.date(int(ymd[0]), int(ymd[1]), int(ymd[2]))
        if isinstance(other, datetime.date):
            return other
        if isinstance(other, CalendarDate):
            return other.date
        raise ValueError("Can't coerce %s to a CalendarDate (use either a CalendarDate, a 'yyyy-mm-dd' string or a datetime.date)" % other)
    
    def as_date(self):
        # Note: add a getter if internal representation change some day
        return self.date

    def __lt__(self, other):
        return self.date < self._coerce(other)

    def __eq__(self, other):
        return self.date == self._coerce(other)

    def __ne__(self, other):
        return self.date != self._coerce(other)
    
    def __hash__(self):
        return self.date.year * 384 + self.date.month * 32 + self.date.day
    
    def __repr__(self):
        if hasattr(self, 'feed_id') and self.feed_id is not None and hasattr(self, 'service_id') and self.service_id is not None:
            return "<%s(id=%s/%s %s)>" % (
                self.__class__.__name__, self.feed_id, self.service_id, self.date)
        else:
            return "<%s(%s)>" % (
                self.__class__.__name__, self.date)

class Trip(object):

    # Same values as Stop, but duplicated as they may differ one day    
    WHEELCHAIR_UNKNOWN = 0
    WHEELCHAIR_YES = 1
    WHEELCHAIR_NO = 2
    
    # Note: YES here really means "at least one"
    BIKES_UNKNOWN = 0
    BIKES_YES = 1
    BIKES_NO = 2
    
    TIME_APPROX = 0
    TIME_EXACT = 1
    
    def __init__(self, feed_id, trip_id, route_id, service_id,
                 wheelchair_accessible=WHEELCHAIR_UNKNOWN,
                 bikes_allowed=BIKES_UNKNOWN,
                 exact_times=TIME_EXACT, **kwargs):
        self.feed_id = feed_id
        self.trip_id = trip_id
        self.route_id = route_id
        self.service_id = service_id
        self.wheelchair_accessible = wheelchair_accessible
        self.bikes_allowed = bikes_allowed
        self.exact_times = exact_times
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def hops(self):
        # Python rocks for this kind of stuff
        return zip(self.stop_times[0:], self.stop_times[1:])

    def __repr__(self):
        return "<%s(id=%s/%s, %s)>" % (
                self.__class__.__name__, self.feed_id, self.trip_id, _public_vars(self))

@total_ordering
class StopTime(object):
    
    PICKUP_DROPOFF_REGULAR = 0
    PICKUP_DROPOFF_NONE = 1
    PICKUP_DROPOFF_PHONE = 2
    PICKUP_DROPOFF_ASKDRIVER = 3
    
    TIMEPOINT_APPROX = 0
    TIMEPOINT_EXACT = 1

    def __init__(self, feed_id, trip_id, stop_id, stop_sequence, arrival_time, departure_time,
                shape_dist_traveled, interpolated=False,
                timepoint=TIMEPOINT_EXACT,
                pickup_type=PICKUP_DROPOFF_REGULAR,
                dropoff_type=PICKUP_DROPOFF_REGULAR, **kwargs):
        self.feed_id = feed_id
        self.trip_id = trip_id
        self.stop_id = stop_id
        self.stop_sequence = stop_sequence
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.interpolated = interpolated
        self.shape_dist_traveled = shape_dist_traveled
        self.timepoint = timepoint
        self.pickup_type = pickup_type
        self.dropoff_type = dropoff_type
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __lt__(self, other):
        return self.stop_sequence < other.stop_sequence

    def __eq__(self, other):
        if not isinstance(other, StopTime):
            return False
        return _generic_eq(self._primary_keys(), other._primary_keys())
        
    def __hash__(self):
        return _generic_hash(self._primary_keys())
    
    def _primary_keys(self):
        return (self.feed_id, self.trip_id, self.stop_id, self.stop_sequence)

    def __repr__(self):
        return "<%s(id=%s/%s/%s, %s)>" % (
                self.__class__.__name__, self.feed_id, self.trip_id, self.stop_sequence, _public_vars(self))

# ---------------------------
# Some private helper methods

def _public_vars(obj):
    # By default only include primitive types
    # Otherwise there will be too much data (think "route.trips"...)
    PRIMITIVE_TYPES = (str, unicode, int, float, bool) if six.PY2 else (str, int, float, bool)
    return { k: v for k, v in vars(obj).items() if k[0] != '_' and isinstance(v, PRIMITIVE_TYPES) }

def _generic_hash(ids):
    h = 0
    for myid in ids:
        h += myid.__hash__()
        h *= 97
    return h

def _generic_eq(a_ids, b_ids):
    for a_id, b_id in zip(a_ids, b_ids):
        if a_id != b_id:
            return False
    return True

