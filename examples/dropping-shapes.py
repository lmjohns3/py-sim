#!/usr/bin/env python

import click
import pagoda
import pagoda.viewer
import numpy as np
import numpy.random as rng


class World(pagoda.physics.World):
    def reset(self):
        for b in self.bodies:
            b.position = np.array([0, 0, 10]) + 3 * rng.randn(3)
            b.quaternion = pagoda.physics.make_quaternion(
                np.pi * rng.rand(), 0, 1, 1)


@click.command()
@click.option('n', default=20, help='number of bodies in the simulation')
def main(n=20):
    w = World()
    # set the cfm parameter below for a trampoline-like floor !
    # w.cfm = 1e-3

    def g(n, k=0.1, size=1):
        return np.clip(rng.gamma(n, k, size=size), 0.5, 1000)

    for _ in range(n):
        s, kw = sorted(dict(
            box=dict(lengths=g(8, size=3)),
            capsule=dict(radius=g(3), length=g(10)),
            cylinder=dict(radius=g(2), length=g(10)),
            sphere=dict(radius=g(2)),
            ).items())[rng.randint(4)]
        b = w.create_body(s, **kw)
        b.color = tuple(rng.uniform(0, 1, size=3)) + (0.9, )

    w.reset()

    pagoda.viewer.Viewer(w).run()


if __name__ == '__main__':
    main()
