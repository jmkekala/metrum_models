# SPDX-License-Identifier: GPL-2.0-only

"""Handrails on an entrance flight: a steel rail on posts along one side of
the steps, level along the landing and following the nosings down the flight,
as closed solids for a build.py to union into its tier.

    import handrails as HR
    FRONT = HR.Flight(a0, a1, wall, -1.0, STEP_PROFILE)
    for B, name in HR.solids([FRONT], level, RS.Paint(L.ATLAS, strip=L.PIPE_STRIP)):
        parts.append(to_object(B, name))
    bad += HR.problems(FRONT, "the front handrail", door_w=0.90)

A flight is given the way every build.py's steps() takes it: extruded across
*a0*..*a1*, its back on the wall at *wall*, running *outward* (+1 or -1) along
*axis* ("y" off a front or rear wall, "x" off a side wall), and its *profile*
the (distance out from the wall, z) outline of the steps: a back edge under
the wall, then level treads falling to the ground. The first, highest tread is
the landing at the door. A flight that comes down from a deck instead, with
no landing of its own, passes the deck's height as *top*: the rail then
starts on the deck just behind its edge.

Why modelled. A flight of three risers or more reaches a landing that is a
fall of half a metre or more, and it gets a handrail, which is how a Finnish
entrance reads as much as its canopy does. One rail, on the right going up,
as the hand holds it on the way in: *side* "left" puts it on the other side
where the right is blocked, and the build records why. The parts are 4-5 cm,
under the 0.25 m relief threshold, but placement-specific: no tiling band can
paint a rail that follows one flight, and it is seen by its outline against
the wall and its shadow on the treads.

Shape. The rail runs INSET in from the flight's edge, its top HEIGHT
above the landing and above the line through the nosings, on posts: one on
the landing by the wall, one at the head of the flight and one on the bottom
tread. The rail's two runs and the posts are separate boxes that overlap, so
the build's union joins them and cuts the posts' feet into the treads. The
balusters are left out: a see-through infill would need alpha or a great many
triangles, and at play distance the rail and posts are what read.

UVs. The rails take the gutter's colour, like the downpipes and the roof
safety kit: pass the same roof_safety.Paint, sampling PIPE_STRIP.

Tiers. MODES keeps them on LOD0 and LOD1. A 4.5 cm rail is about two pixels
at 70 m and one at 120 m, and a single one of them costs as much as a window
does, so they go at LOD2. They stand inside the steps' footprint and under the
eaves, so dropping them changes no tier's extents.

Runs inside Blender only.
"""

from mathutils import Vector

import roof_safety as RS

HEIGHT = 0.90               # rail top above the landing and the nosing line
RAIL = 0.045                # the rail, square
POST = 0.045                # the posts, square
INSET = 0.05                # rail centre in from the flight's side
WALL_GAP = 0.05             # the landing's post clear of the wall
FOOT_END = 0.10             # the bottom post in from the last nosing
BURY = 0.05                 # posts run this far into the tread below
DOOR_CLEAR = 0.10           # the least between the rail and the door's jamb

# whether each tier, LOD0 to LOD3, keeps the rails
MODES = (True, True, False, False)


class Flight:
    """The handrail of one flight of steps."""

    def __init__(self, a0, a1, wall, outward, profile, axis="y", top=None,
                 inset=INSET, side="right"):
        if side not in ("right", "left"):
            raise ValueError("side is 'right' or 'left', seen going up")
        self.a0, self.a1 = min(a0, a1), max(a0, a1)
        self.side = side
        self.wall, self.outward, self.axis, self.inset = wall, outward, axis, inset
        flats = []
        for (d0, z0), (d1, z1) in zip(profile, profile[1:] + profile[:1]):
            if abs(z1 - z0) < 1e-6 and z0 > 1e-6:
                flats.append((min(d0, d1), max(d0, d1), z0))
        flats.sort(key=lambda f: -f[2])
        if top is None:
            land, treads = flats[0], flats[1:]
            self.upper = (land[1], land[2])
            self.inner = max(0.0, land[0]) + WALL_GAP + POST / 2.0
        else:
            treads = flats
            self.upper = (0.0, top)
            self.inner = -WALL_GAP - POST / 2.0      # on the deck behind its edge
        if not treads:
            raise ValueError("a flight needs at least one tread below its head")
        self.treads = treads
        last = treads[-1]
        du, zu = self.upper
        self.slope = (last[2] - zu) / (last[1] - du)
        self.foot = last[1] - FOOT_END
        self.foot_z = last[2]

    def _dirs(self):
        o = self.outward
        if self.axis == "y":
            return Vector((0.0, o, 0.0)), Vector((1.0, 0.0, 0.0))
        return Vector((o, 0.0, 0.0)), Vector((0.0, 1.0, 0.0))

    def W(self, a, d, z):
        dv, av = self._dirs()
        base = Vector((0.0, self.wall, 0.0)) if self.axis == "y" else \
            Vector((self.wall, 0.0, 0.0))
        return base + dv * d + av * a + Vector((0.0, 0.0, z))

    def rail_top(self, d):
        """The rail's top at *d* out from the wall."""
        du, zu = self.upper
        if d <= du:
            return zu + HEIGHT
        return zu + HEIGHT + self.slope * (d - du)

    def rail_a(self):
        """The rail's centre across the flight: on *side*, seen by someone
        climbing it, facing the wall."""
        dv, av = self._dirs()
        right = (-dv).cross(Vector((0.0, 0.0, 1.0)))
        on_high = (right.dot(av) > 0.0) == (self.side == "right")
        return self.a1 - self.inset if on_high else self.a0 + self.inset

    def posts(self):
        """(d, floor z) of each post."""
        du, zu = self.upper
        head = du - POST / 2.0 - 0.02
        out = [(self.inner, zu)]
        if head - self.inner > POST * 2:
            out.append((head, zu))
        out.append((self.foot, self.foot_z))
        return out

    def solids(self, paint):
        dv, _ = self._dirs()
        up = Vector((0.0, 0.0, 1.0))
        du, zu = self.upper
        r2, p2 = RAIL / 2.0, POST / 2.0
        out = []
        for a in (self.rail_a(),):
            # the level run over the landing, into the head of the flight
            ay = up.cross(dv)
            zc = zu + HEIGHT - r2
            out.append(RS.box(RS.Mesh(paint), self.W(a, 0.0, 0.0), dv, ay, up,
                              (self.inner - p2, du + r2), (-r2, r2), (zc - r2, zc + r2)))
            # the run down the flight, along the nosing line
            p0 = self.W(a, du, zu + HEIGHT)
            p1 = self.W(a, self.foot, self.rail_top(self.foot))
            ax = (p1 - p0).normalized()
            az = (up - ax * up.dot(ax)).normalized()
            ay = az.cross(ax)
            length = (p1 - p0).length
            out.append(RS.box(RS.Mesh(paint), p0 - az * r2, ax, ay, az,
                              (-r2, length + p2), (-r2, r2), (-r2, r2)))
            for d, zf in self.posts():
                ztop = self.rail_top(d) - r2
                out.append(RS.box(RS.Mesh(paint), self.W(a, d, 0.0), dv, up.cross(dv),
                                  up, (-p2, p2), (-p2, p2), (zf - BURY, ztop)))
        return out


def solids(flights, level, paint, modes=MODES):
    """(solid, object name) for each part of *flights* at *level*; none on a
    tier that drops the rails. *modes* replaces MODES for a building that
    keeps them further out or drops them sooner."""
    if not modes[level]:
        return []
    out = []
    for f in flights:
        for M in f.solids(paint):
            out.append((M, "tmp_handrail%d" % len(out)))
    return out


def problems(flight, name, door_w=None, door_c=None):
    """What is wrong with *flight*'s rail: a door of width *door_w*, centred
    at *door_c* across the flight (its middle when None), with less than
    DOOR_CLEAR between its jamb and the rail; a bottom post off its tread; a
    flight too short to carry the rail down it."""
    bad = []
    a = flight.rail_a()
    if door_w is not None:
        c = (flight.a0 + flight.a1) / 2.0 if door_c is None else door_c
        if abs(a - c) - RAIL / 2.0 < door_w / 2.0 + DOOR_CLEAR:
            bad.append("%s crowds the door" % name)
    t0, t1, _ = flight.treads[-1]
    if not (t0 + POST / 2.0 < flight.foot < t1 - POST / 2.0):
        bad.append("%s: the bottom post is off its tread" % name)
    if flight.foot - flight.upper[0] < 0.3:
        bad.append("%s: the flight is too short for a sloping rail" % name)
    return bad
