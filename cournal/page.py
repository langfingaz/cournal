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

class Page:
    def __init__(self, document, page, number):
        self.document = document
        self.pdf = page
        self.number = number
        self.newdata_callback = []
        
        self.width, self.height = page.get_size()
        self.strokes = []
        
    def add_newdata_callback(self, callback):
        self.newdata_callback.append(callback)
       
    def somecallback(self, stroke):
        for callback in self.newdata_callback:
            callback(stroke)
       
