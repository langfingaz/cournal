#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Fabian Henze
# 
# Cournal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cournal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cournal.  If not, see <http://www.gnu.org/licenses/>.

import cairo

from twisted.spread import pb

from xojtools import Stroke as XojStroke


class Stroke(XojStroke, pb.Copyable, pb.RemoteCopy):
    def __init__(self, layer, **kwargs):
        XojStroke.__init__(self, **kwargs)
        self.layer = layer
            
    @classmethod
    def fromXojStroke(cls, stroke, layer):
        color = stroke.color
        coords = stroke.coords
        width = stroke.width
        
        return cls(stroke, layer, color, coords, width)
    
    def getStateToCopy(self):
        # d would be self.__dict__.copy()
        d = dict()
        d["color"] = self.color
        d["coords"] = self.coords
        d["width"] = self.width
        return d

    def draw(self, context, scaling=1):
        context.save()
        r, g, b, opacity = self.color
        linewidth = self.width
        
        context.set_source_rgba(r/255, g/255, b/255, opacity/255)
        context.set_antialias(cairo.ANTIALIAS_GRAY)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_width(linewidth)
        
        first = self.coords[0]
        context.move_to(first[0], first[1])
        if len(self.coords) > 1:
            for coord in self.coords[1:]:
                context.line_to(coord[0], coord[1])
        else:
            context.line_to(first[0], first[1])
        x, y, x2, y2 = (a*scaling for a in context.stroke_extents())
        context.stroke()
        context.restore()
        
        return (x, y, x2, y2)
        
pb.setUnjellyableForClass(Stroke, Stroke)