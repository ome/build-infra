#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2019 University of Dundee & Open Microscopy Environment
# All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import print_function
from builtins import object
import argparse
import os
import os.path
import xml.etree.ElementTree as ET


class POM(object):
    def __init__(self, path):
        self.path = path
        self.root = ET.parse(self.path).getroot()
        self.ns = self.root.tag[1:self.root.tag.index('}')]

    def get_modules(self):
        m = self.root.find('{%s}modules' % self.ns)
        if m is None:
            return []
        return [x.text for x in m.findall('{%s}module' % self.ns)]

    def get_version(self):
        """Returns the component version as a tuple"""
        artifactId = self.root.find('{%s}artifactId' % self.ns).text
        parent = self.root.find('{%s}parent' % self.ns)
        if parent is not None:
            # Assume the groupId and version are inherited from the parent
            groupId = parent.find('{%s}groupId' % self.ns).text
            version = parent.find('{%s}version' % self.ns).text
        else:
            groupId = self.root.find('{%s}groupId' % self.ns).text
            version = self.root.find('{%s}version' % self.ns).text
        return (groupId, artifactId, version)

    def get_module_versions(self):
        versions = []
        for module in self.get_modules():
            pom = POM(os.path.join(
                os.path.dirname(self.path), module, 'pom.xml'))
            versions.append(pom.get_version())
            if pom.get_modules():
                versions.extend(pom.get_module_versions())
        return versions


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--recursive', action='store_true',
        help='Get all versions recursively')
    args = parser.parse_args()

    pom = POM(os.path.join(os.getcwd(), 'pom.xml'))
    print("\t".join(pom.get_version()))
    pom.get_module_versions()
    if args.recursive:
        for v in pom.get_module_versions():
            print("\t".join(v))
