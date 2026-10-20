"""Parametric model of the cat feeder.

Run inside FreeCAD (GUI or freecadcmd):
    exec(open("cad/build.py").read(), {"__file__": "cad/build.py"})

Axes: X = width (centered), Y = depth (front/bowl is -Y, wall is +Y), Z = up.
Every printable part must fit a 180 x 180 x 180 mm bed (checked at the end).
Units: mm.
"""

import os

import FreeCAD as App
import Part
from FreeCAD import Vector as V

# --- Printer -----------------------------------------------------------------
BED = 180.0
BED_MARGIN = 5.0

# --- Base --------------------------------------------------------------------
BASE_W = 170.0          # X width of both base modules
FRONT_D = 160.0         # front module depth (bowl)
FRONT_H = 25.0
REAR_D = 160.0          # rear module depth (tower + electronics)
REAR_H = 55.0
WALL = 3.0
REAR_FLOOR = 8.0

# --- Ballast: commercial steel flat bar 40 x 5 mm, cut to length ---------------
BAR_W = 40.0
BAR_T = 5.0
BAR_L = 140.0
BAR_GAP = 10.0          # between the two bars of a module
BAR_CLEAR = 0.5

# --- Bowl (printed) --------------------------------------------------------------
BOWL_D = 130.0
BOWL_H = 45.0
BOWL_WALL = 3.0
BOWL_Y = -80.0          # bowl center
BOWL_SEAT_DEPTH = 12.0
BOWL_CLEAR = 2.0

# --- Antenna groove (134.2 kHz coil around the bowl seat) ------------------------
ANT_GROOVE_W = 4.0
ANT_GROOVE_DEPTH = 8.0
ANT_GROOVE_GAP = 2.0    # wall between bowl seat and groove

# --- Auger housing ----------------------------------------------------------------
AUGER_ID = 40.0
AUGER_WALL = 5.0
AUGER_Z = REAR_H + 28.0             # axis height
AUGER_Y0 = -30.0                    # front end (outlet over the bowl)
AUGER_Y1 = 110.0                    # rear end (motor flange)
OUTLET_W = 30.0
OUTLET_Y = -25.0                    # outlet center

# --- NEMA 17 -------------------------------------------------------------------------
NEMA = 42.3
NEMA_L = 40.0
NEMA_FLANGE_T = 5.0

# --- Hopper (Pringles-like tube) -----------------------------------------------------
HOPPER_ID = 74.0
HOPPER_WALL = 2.5
HOPPER_Y = 55.0                     # hopper axis
HOPPER_SEG_H = 115.0                # segment height; add segments for more capacity
HOPPER_SEGMENTS = 2
COLLAR_H = 18.0
LID_H = 15.0

# --- Wall mount ---------------------------------------------------------------------
BACK_T = 6.0
BACK_H = 170.0
UPPER_BRACKET_H = 90.0
UPPER_BRACKET_Z = 230.0

DOC_NAME = "CatFeeder"


# --- Helpers ---------------------------------------------------------------------------
def box(x0, y0, z0, x1, y1, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def cyl_y(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def ballast_pockets(y_center, z_bottom=0.0):
    """Two side-by-side pockets for steel flat bars, open at the bottom."""
    w = BAR_W + BAR_CLEAR
    l = BAR_L + BAR_CLEAR
    t = BAR_T + BAR_CLEAR
    xs = (-(BAR_GAP / 2 + w), BAR_GAP / 2)
    return [box(x, y_center - l / 2, z_bottom, x + w, y_center + l / 2, z_bottom + t) for x in xs]


def cut_all(shape, tools):
    for t in tools:
        shape = shape.cut(t)
    return shape


# --- Parts -------------------------------------------------------------------------------
def make_front_base():
    hw = BASE_W / 2
    s = box(-hw, -FRONT_D, 0, hw, 0, FRONT_H)
    seat_r = BOWL_D / 2 + BOWL_CLEAR / 2
    seat = cyl_z(seat_r, FRONT_H - BOWL_SEAT_DEPTH, FRONT_H + 1, y=BOWL_Y)
    g_in = seat_r + ANT_GROOVE_GAP
    groove = cyl_z(g_in + ANT_GROOVE_W, FRONT_H - ANT_GROOVE_DEPTH, FRONT_H + 1, y=BOWL_Y).cut(
        cyl_z(g_in, FRONT_H - ANT_GROOVE_DEPTH - 1, FRONT_H + 2, y=BOWL_Y))
    return cut_all(s, [seat, groove] + ballast_pockets(BOWL_Y))


def make_rear_base():
    hw = BASE_W / 2
    s = box(-hw, 0, 0, hw, REAR_D, REAR_H)
    bay = box(-hw + WALL, WALL, REAR_FLOOR, hw - WALL, REAR_D - WALL, REAR_H - WALL)
    side_door = box(hw - WALL - 1, 20, REAR_FLOOR + 5, hw + 1, REAR_D - 20, REAR_H - WALL - 5)
    cable = cyl_z(6, REAR_H - WALL - 1, REAR_H + 1, y=REAR_D - 30)
    return cut_all(s, [bay, side_door, cable] + ballast_pockets(REAR_D / 2))


def make_bowl():
    r = BOWL_D / 2
    outer = cyl_z(r, 0, BOWL_H)
    inner = cyl_z(r - BOWL_WALL, BOWL_WALL, BOWL_H + 1)
    s = outer.cut(inner)
    s.translate(V(0, BOWL_Y, FRONT_H - BOWL_SEAT_DEPTH))
    return s


def make_auger_housing():
    ro = AUGER_ID / 2 + AUGER_WALL
    ri = AUGER_ID / 2
    tube = cyl_y(ro, AUGER_Y0, AUGER_Y1, z=AUGER_Z)
    cradle = box(-ro, max(AUGER_Y0, 0) + 5, REAR_H, ro, AUGER_Y1, AUGER_Z)
    flange = box(-NEMA / 2 - 3, AUGER_Y1, AUGER_Z - NEMA / 2 - 3,
                 NEMA / 2 + 3, AUGER_Y1 + NEMA_FLANGE_T, AUGER_Z + NEMA / 2 + 3)
    collar_ro = HOPPER_ID / 2 + HOPPER_WALL + 3
    collar = cyl_z(collar_ro, AUGER_Z, AUGER_Z + ro + COLLAR_H, y=HOPPER_Y)
    s = tube.fuse([cradle, flange, collar])
    bore = cyl_y(ri, AUGER_Y0 - 1, AUGER_Y1 + 1, z=AUGER_Z)
    socket = cyl_z(HOPPER_ID / 2 + HOPPER_WALL + 0.3, AUGER_Z + ro, AUGER_Z + ro + COLLAR_H + 1, y=HOPPER_Y)
    inlet = cyl_z(HOPPER_ID / 2 - 2, AUGER_Z, AUGER_Z + ro + 1, y=HOPPER_Y)
    outlet = box(-OUTLET_W / 2, OUTLET_Y - OUTLET_W / 2, AUGER_Z - ro - 1,
                 OUTLET_W / 2, OUTLET_Y + OUTLET_W / 2, AUGER_Z)
    shaft = cyl_y(11.5, AUGER_Y1 - 1, AUGER_Y1 + NEMA_FLANGE_T + 1, z=AUGER_Z)
    return cut_all(s, [bore, socket, inlet, outlet, shaft])


def hopper_z0():
    return AUGER_Z + AUGER_ID / 2 + AUGER_WALL


def make_hopper_segment(i):
    z0 = hopper_z0() + i * HOPPER_SEG_H
    ro = HOPPER_ID / 2 + HOPPER_WALL
    return cyl_z(ro, z0, z0 + HOPPER_SEG_H, y=HOPPER_Y).cut(
        cyl_z(HOPPER_ID / 2, z0 - 1, z0 + HOPPER_SEG_H + 1, y=HOPPER_Y))


def make_lid():
    z0 = hopper_z0() + HOPPER_SEGMENTS * HOPPER_SEG_H
    ro = HOPPER_ID / 2 + HOPPER_WALL + 3
    s = cyl_z(ro, z0, z0 + LID_H, y=HOPPER_Y)
    skirt = cyl_z(HOPPER_ID / 2 + HOPPER_WALL + 0.3, z0 - 1, z0 + LID_H - 4, y=HOPPER_Y)
    sensor = box(-8, HOPPER_Y - 8, z0 + LID_H - 5, 8, HOPPER_Y + 8, z0 + LID_H + 1)
    return cut_all(s, [skirt, sensor])


def make_motor():
    return box(-NEMA / 2, AUGER_Y1 + NEMA_FLANGE_T, AUGER_Z - NEMA / 2,
               NEMA / 2, AUGER_Y1 + NEMA_FLANGE_T + NEMA_L, AUGER_Z + NEMA / 2)


def make_back_plate():
    hw = BASE_W / 2
    return box(-hw, REAR_D, 0, hw, REAR_D + BACK_T, BACK_H)


def make_upper_bracket():
    z0, z1 = UPPER_BRACKET_Z, UPPER_BRACKET_Z + UPPER_BRACKET_H
    ro = HOPPER_ID / 2 + HOPPER_WALL
    plate = box(-60, REAR_D, z0, 60, REAR_D + BACK_T, z1)
    arm = box(-12, HOPPER_Y, z0, 12, REAR_D, z0 + 20)
    ring = cyl_z(ro + 4, z0, z0 + 20, y=HOPPER_Y)
    hole = cyl_z(ro + 0.3, z0 - 1, z0 + 21, y=HOPPER_Y)
    return plate.fuse([arm, ring]).cut(hole)


# --- Build -------------------------------------------------------------------------------
PARTS = [
    # name, builder, printable, color
    ("FrontBase", make_front_base, True, (0.85, 0.85, 0.80)),
    ("RearBase", make_rear_base, True, (0.85, 0.85, 0.80)),
    ("Bowl", make_bowl, True, (0.95, 0.60, 0.30)),
    ("AugerHousing", make_auger_housing, True, (0.40, 0.65, 0.90)),
    *[(f"HopperSegment{i + 1}", (lambda i=i: make_hopper_segment(i)), True, (0.80, 0.90, 1.00))
      for i in range(HOPPER_SEGMENTS)],
    ("Lid", make_lid, True, (0.40, 0.65, 0.90)),
    ("BackPlate", make_back_plate, True, (0.70, 0.70, 0.70)),
    ("UpperBracket", make_upper_bracket, True, (0.70, 0.70, 0.70)),
    ("NEMA17", make_motor, False, (0.20, 0.20, 0.20)),
]


def build():
    if App.listDocuments().get(DOC_NAME):
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    report = []
    for name, fn, printable, color in PARTS:
        shape = fn()
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        if App.GuiUp:
            obj.ViewObject.ShapeColor = color
            if name.startswith("Hopper"):
                obj.ViewObject.Transparency = 50
        bb = shape.BoundBox
        dims = sorted((bb.XLength, bb.YLength, bb.ZLength), reverse=True)
        fits = dims[0] <= BED - BED_MARGIN
        if printable:
            report.append((name, dims, fits))
    doc.recompute()

    here = os.path.dirname(os.path.abspath(globals().get("__file__", "cad/build.py")))
    doc.saveAs(os.path.join(here, "cat-feeder.FCStd"))

    total = doc.getObject("NEMA17").Shape.BoundBox
    for o in doc.Objects:
        total.add(o.Shape.BoundBox)
    print(f"Assembly: {total.XLength:.0f} x {total.YLength:.0f} x {total.ZLength:.0f} mm")
    for name, dims, fits in report:
        d = " x ".join(f"{v:.0f}" for v in dims)
        print(f"{'OK ' if fits else 'BIG'} {name:15s} {d}")
    if not all(f for _, _, f in report):
        print(f"WARNING: some parts exceed {BED - BED_MARGIN:.0f} mm")
    return doc


build()
