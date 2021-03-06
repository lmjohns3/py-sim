'''This module contains OpenGL code for rendering a world.'''

from __future__ import division

import numpy as np
import os

from . import physics
from . import window


class Null(object):
    '''This viewer does nothing!

    It is here for headless simulation runs, i.e., where the world does not need
    to be rendered to a graphics window but some measurements or other
    side-effects of repeatedly stepping the world are useful.
    '''

    def __init__(self, world):
        self.world = world

    def run(self):
        while not self.world.step():
            if self.world.needs_reset():
                self.world.reset()


class Viewer(window.Window):
    '''A viewer window for pagoda worlds.

    This viewer adds the following default keybindings:
    - F: freeze state of current bodies in the world
    - RIGHT-ARROW: advance world state by 1 frame (10 if SHIFT)
    - ENTER: reset the world

    Parameters
    ----------
    world : :class:`pagoda.World`
        A world object to view in this window.

    Attributes
    ----------
    world : :class:`pagoda.World`
        The world object being viewed in this window.
    '''

    def __init__(self, world, *args, **kwargs):
        super(Viewer, self).__init__(*args, **kwargs)
        self.world = world
        self._frozen = []

    def grab_key_press(self, key, modifiers, keymap):
        if self.world.on_key_press(key, modifiers, keymap):
            return True
        if key == keymap.F:
            self.freeze_bodies()
            return True
        if key == keymap.RIGHT:
            steps = int(1 / self.world.dt)
            if modifiers & keymap.MOD_SHIFT:
                steps *= 10
            [self.step(self.world.dt) for _ in range(steps)]
            return True

    def step(self, dt):
        if self.world.step():
            self.exit()
        if self.world.needs_reset():
            self.world.reset()

    def freeze_bodies(self):
        bodies = []
        for b in self.world.bodies:
            if getattr(b, 'can_freeze', None) is False:
                continue
            shape = {}
            if isinstance(b, physics.Sphere):
                shape = dict(radius=b.radius)
            if isinstance(b, physics.Box):
                shape = dict(lengths=b.lengths)
            if isinstance(b, physics.Cylinder):
                shape = dict(radius=b.radius, length=b.length)
            if isinstance(b, physics.Capsule):
                shape = dict(radius=b.radius, length=b.length)
            bp = b.__class__(b.name, self.world, mass=b.mass.mass, **shape)
            bp.color = list(b.color[:3]) + [0.5]
            bp.position = b.position
            bp.quaternion = b.quaternion
            bp.is_kinematic = True
            bodies.append(bp)
        self._frozen.append(bodies)

    def render(self, dt):
        '''Draw all bodies in the world.'''
        for frame in self._frozen:
            for body in frame:
                self.draw_body(body)
        for body in self.world.bodies:
            self.draw_body(body)

        if hasattr(self.world, 'markers'):
            # draw line between anchor1 and anchor2 for marker joints.
            window.glColor4f(0.9, 0.1, 0.1, 0.9)
            window.glLineWidth(3)
            for j in self.world.markers.joints.values():
                window.glBegin(window.GL_LINES)
                window.glVertex3f(*j.getAnchor())
                window.glVertex3f(*j.getAnchor2())
                window.glEnd()

    def draw_body(self, body):
        '''
        '''
        x, y, z = body.position
        r = body.rotation
        with window.gl_context(mat=(r[0, 0], r[1, 0], r[2, 0], 0.,
                                      r[0, 1], r[1, 1], r[2, 1], 0.,
                                      r[0, 2], r[1, 2], r[2, 2], 0.,
                                      x, y, z, 1.),
                                 color=body.color):
            if isinstance(body, physics.Box):
                x, y, z = body.lengths
                window.glScalef(x / 2., y / 2., z / 2.)
                self.box.draw(window.GL_TRIANGLES)
            elif isinstance(body, physics.Sphere):
                r = body.radius
                window.glScalef(r, r, r)
                self.sphere.draw(window.GL_TRIANGLES)
            elif isinstance(body, physics.Cylinder):
                l = body.length
                r = body.radius
                window.glScalef(r, r, l / 2)
                self.cylinder.draw(window.GL_TRIANGLES)
            elif isinstance(body, physics.Capsule):
                r = body.radius
                l = body.length
                with window.gl_context(scale=(r, r, l / 2)):
                    self.cylinder.draw(window.GL_TRIANGLES)
                with window.gl_context(mat=(r, 0, 0, 0,
                                              0, r, 0, 0,
                                              0, 0, r, 0,
                                              0, 0, -l / 2, 1),
                                         color=body.color):
                    self.sphere.draw(window.GL_TRIANGLES)
                with window.gl_context(mat=(r, 0, 0, 0,
                                              0, r, 0, 0,
                                              0, 0, r, 0,
                                              0, 0, l / 2, 1),
                                         color=body.color):
                    self.sphere.draw(window.GL_TRIANGLES)
