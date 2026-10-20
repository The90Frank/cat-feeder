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

# --- Bowl (printed, square) -------------------------------------------------------
BOWL_SIDE = 130.0
BOWL_H = 45.0
BOWL_WALL = 3.0
BOWL_FILLET = 12.0      # vertical corners, easier to clean
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
AUGER_Y0 = -25.0                    # front end of the horizontal tube
AUGER_Y1 = 110.0                    # rear end (motor flange)
# The horizontal run between the hopper inlet and AUGER_Y0 keeps kibble inside the
# auger flights when the motor is stopped: the auger itself is the shut-off.

# --- Spout: sloped tube after the auger, ends inside the bowl -----------------------
SPOUT_ANGLE = 30.0                  # degrees below horizontal; kibble slides at ~25-30
SPOUT_REACH = 20.0                  # horizontal reach past the housing; exit face is vertical
BOWL_NOTCH_CLEAR = 1.0

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
UPPER_BRACKET_Z = 240.0             # above the segment joint collar

# --- Fasteners -----------------------------------------------------------------------
M3_CLEAR = 3.4
M3_PILOT = 2.5          # self-tapping into plastic
M4_CLEAR = 4.4
M4_NUT_AF = 7.0
M4_NUT_T = 3.2
NEMA_HOLE_SPACING = 31.0
KEYHOLE_HEAD = 9.0      # screw head passes here
KEYHOLE_SHANK = 4.5
KEYHOLE_SLOT = 10.0
KEYHOLE_RECESS = 3.0    # depth of the head channel on the wall side

# --- Joints and openings ------------------------------------------------------------------
BASE_BOLT_X = 55.0
BASE_BOLT_Z = FRONT_H / 2
TAB_W = 12.0
TAB_T = 5.0
SPOUT_SLEEVE_L = 10.0
SPOUT_SLEEVE_T = 3.0
HOPPER_COLLAR_H = 10.0
HOPPER_COLLAR_T = 3.0
DOOR_T = 2.5
DC_JACK_D = 8.1
VENT_COUNT = 5

# --- VL53L0X breakout (GY-VL53L0XV2) -------------------------------------------------------
TOF_BOARD = (26.0, 12.0)
TOF_WINDOW = (10.0, 6.0)

DOC_NAME = "CatFeeder"


# --- Helpers ---------------------------------------------------------------------------
def box(x0, y0, z0, x1, y1, z1):
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl_z(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def cyl_y(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def cyl_dir(r, start, direction, length):
    d = App.Vector(direction)
    d.normalize()
    return Part.makeCylinder(r, length, start, d)


def spout_dir():
    import math
    a = math.radians(SPOUT_ANGLE)
    return V(0, -math.cos(a), -math.sin(a))


def spout_start():
    return V(0, AUGER_Y0, AUGER_Z)


def bowl_footprint(side, z0, z1, fillet):
    b = box(-side / 2, BOWL_Y - side / 2, z0, side / 2, BOWL_Y + side / 2, z1)
    edges = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1e-6]
    return b.makeFillet(fillet, edges) if fillet > 0 else b


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
def keyhole_y(x, z, y_front, y_back):
    """Keyhole through a plate normal to Y, wall side at y_back. Hang by sliding down."""
    head = cyl_y(KEYHOLE_HEAD / 2, y_front - 1, y_back + 1, x=x, z=z)
    slot = box(x - KEYHOLE_SHANK / 2, y_front - 1, z, x + KEYHOLE_SHANK / 2, y_back + 1, z + KEYHOLE_SLOT)
    top = cyl_y(KEYHOLE_SHANK / 2, y_front - 1, y_back + 1, x=x, z=z + KEYHOLE_SLOT)
    channel = box(x - KEYHOLE_HEAD / 2, y_back - KEYHOLE_RECESS, z,
                  x + KEYHOLE_HEAD / 2, y_back + 1, z + KEYHOLE_SLOT)
    cap = cyl_y(KEYHOLE_HEAD / 2, y_back - KEYHOLE_RECESS, y_back + 1, x=x, z=z + KEYHOLE_SLOT)
    return [head, slot, top, channel, cap]


def ballast_screws(y_center):
    """Pilot holes at both ends of each pocket: screw + washer hold the bar."""
    w = BAR_W + BAR_CLEAR
    l = BAR_L + BAR_CLEAR
    xs = (-(BAR_GAP / 2 + w / 2), BAR_GAP / 2 + w / 2)
    ys = (y_center - l / 2 - 3.5, y_center + l / 2 + 3.5)
    return [cyl_z(M3_PILOT / 2, -1, 8, x=x, y=y) for x in xs for y in ys]


def tab_holes():
    x = AUGER_ID / 2 + AUGER_WALL + TAB_W / 2
    return [(sx * x, y) for sx in (-1, 1) for y in (20.0, 95.0)]


def door_screws():
    return [(16.0, (REAR_FLOOR + REAR_H) / 2), (REAR_D - 16.0, (REAR_FLOOR + REAR_H) / 2)]


def make_front_base():
    hw = BASE_W / 2
    s = box(-hw, -FRONT_D, 0, hw, 0, FRONT_H)
    seat_side = BOWL_SIDE + BOWL_CLEAR
    z_seat = FRONT_H - BOWL_SEAT_DEPTH
    seat = bowl_footprint(seat_side, z_seat, FRONT_H + 1, BOWL_FILLET + BOWL_CLEAR / 2)
    g_in = seat_side + 2 * ANT_GROOVE_GAP
    g_out = g_in + 2 * ANT_GROOVE_W
    z_g = FRONT_H - ANT_GROOVE_DEPTH
    groove = bowl_footprint(g_out, z_g, FRONT_H + 1, BOWL_FILLET + ANT_GROOVE_GAP + ANT_GROOVE_W).cut(
        bowl_footprint(g_in, z_g - 1, FRONT_H + 2, BOWL_FILLET + ANT_GROOVE_GAP))
    # Antenna leads: from the groove to the rear face, into the electronics bay.
    y_groove = BOWL_Y + g_out / 2
    lead = cyl_y(2.5, y_groove - ANT_GROOVE_W, 1, z=z_g + ANT_GROOVE_DEPTH / 2)
    tools = [seat, groove, lead] + ballast_pockets(BOWL_Y) + ballast_screws(BOWL_Y)
    for sx in (-1, 1):
        x = sx * BASE_BOLT_X
        tools.append(cyl_y(M4_CLEAR / 2, -20, 1, x=x, z=BASE_BOLT_Z))
        # Nut slot, open at the bottom: drop the nut in, then bolt from inside the bay.
        tools.append(box(x - M4_NUT_AF / 2 - 0.2, -12 - M4_NUT_T / 2 - 0.2, -1,
                         x + M4_NUT_AF / 2 + 0.2, -12 + M4_NUT_T / 2 + 0.2, BASE_BOLT_Z + 4.3))
    return cut_all(s, tools)


def make_rear_base():
    hw = BASE_W / 2
    s = box(-hw, 0, 0, hw, REAR_D, REAR_H)
    bay = box(-hw + WALL, WALL, REAR_FLOOR, hw - WALL, REAR_D - WALL, REAR_H - WALL)
    s = s.cut(bay)
    # Bosses for the door screws, inside the bay.
    for y, z in door_screws():
        s = s.fuse(Part.makeCylinder(4, 6, V(hw - WALL - 6, y, z), V(1, 0, 0)))
    door = box(hw - WALL - 1, 24, REAR_FLOOR + 3, hw + 1, REAR_D - 24, REAR_H - WALL - 3)
    cable = cyl_z(6, REAR_H - WALL - 1, REAR_H + 1, y=REAR_D - 30)
    tools = [door, cable] + ballast_pockets(REAR_D / 2) + ballast_screws(REAR_D / 2)
    for y, z in door_screws():
        tools.append(Part.makeCylinder(M3_PILOT / 2, 12, V(hw - 11, y, z), V(1, 0, 0)))
    for sx in (-1, 1):  # front base bolts
        tools.append(cyl_y(M4_CLEAR / 2, -1, WALL + 1, x=sx * BASE_BOLT_X, z=BASE_BOLT_Z))
    for sx in (-1, 1):  # back plate bolts
        tools.append(cyl_y(M4_CLEAR / 2, REAR_D - WALL - 1, REAR_D + 1, x=sx * 40, z=30))
    for x, y in tab_holes():  # auger housing
        tools.append(cyl_z(M3_CLEAR / 2, REAR_H - WALL - 1, REAR_H + 1, x=x, y=y))
    # Antenna leads from the front base.
    tools.append(cyl_y(3, -1, WALL + 1, z=FRONT_H - ANT_GROOVE_DEPTH / 2))
    # Vents and DC jack on the left wall.
    for k in range(VENT_COUNT):
        y = 40 + k * 16
        tools.append(box(-hw - 1, y, REAR_FLOOR + 10, -hw + WALL + 1, y + 4, REAR_H - WALL - 10))
    tools.append(Part.makeCylinder(DC_JACK_D / 2, WALL + 2, V(-hw - 1, REAR_D - 25, 30), V(1, 0, 0)))
    return cut_all(s, tools)


def make_bay_door():
    hw = BASE_W / 2
    s = box(hw, 16, REAR_FLOOR - 1, hw + DOOR_T, REAR_D - 16, REAR_H - 2)
    holes = [Part.makeCylinder(M3_CLEAR / 2, DOOR_T + 2, V(hw - 1, y, z), V(1, 0, 0))
             for y, z in door_screws()]
    return cut_all(s, holes)


def make_bowl():
    z0 = FRONT_H - BOWL_SEAT_DEPTH
    outer = bowl_footprint(BOWL_SIDE, z0, z0 + BOWL_H, BOWL_FILLET)
    inner = bowl_footprint(BOWL_SIDE - 2 * BOWL_WALL, z0 + BOWL_WALL, z0 + BOWL_H + 1,
                           BOWL_FILLET - BOWL_WALL)
    s = outer.cut(inner)
    # Notch in the rear wall hugging the spout and its sleeve: no gap where kibble could escape.
    ro = AUGER_ID / 2 + AUGER_WALL
    notch = spout_body(ro + BOWL_NOTCH_CLEAR)
    sleeve = cyl_y(ro + SPOUT_SLEEVE_T + BOWL_NOTCH_CLEAR, AUGER_Y0 - 1, AUGER_Y0 + SPOUT_SLEEVE_L + 1,
                   z=AUGER_Z)
    return s.cut(notch).cut(sleeve)


def make_auger_housing():
    ro = AUGER_ID / 2 + AUGER_WALL
    ri = AUGER_ID / 2
    tube = cyl_y(ro, AUGER_Y0, AUGER_Y1, z=AUGER_Z)
    cradle = box(-ro, max(AUGER_Y0, 0) + 5, REAR_H, ro, AUGER_Y1, AUGER_Z)
    tabs = [box(sx * ro, 10, REAR_H, sx * (ro + TAB_W), 105, REAR_H + TAB_T) for sx in (-1, 1)]
    flange = box(-NEMA / 2 - 3, AUGER_Y1, AUGER_Z - NEMA / 2 - 3,
                 NEMA / 2 + 3, AUGER_Y1 + NEMA_FLANGE_T, AUGER_Z + NEMA / 2 + 3)
    collar_ro = HOPPER_ID / 2 + HOPPER_WALL + 3
    collar = cyl_z(collar_ro, AUGER_Z, AUGER_Z + ro + COLLAR_H, y=HOPPER_Y)
    s = tube.fuse([cradle, flange, collar] + tabs)
    bore = cyl_y(ri, AUGER_Y0 - 1, AUGER_Y1 + 1, z=AUGER_Z)
    socket = cyl_z(HOPPER_ID / 2 + HOPPER_WALL + 0.3, AUGER_Z + ro, AUGER_Z + ro + COLLAR_H + 1, y=HOPPER_Y)
    inlet = cyl_z(HOPPER_ID / 2 - 2, AUGER_Z, AUGER_Z + ro + 1, y=HOPPER_Y)
    shaft = cyl_y(11.5, AUGER_Y1 - 1, AUGER_Y1 + NEMA_FLANGE_T + 1, z=AUGER_Z)
    h = NEMA_HOLE_SPACING / 2
    nema = [cyl_y(M3_CLEAR / 2, AUGER_Y1 - 1, AUGER_Y1 + NEMA_FLANGE_T + 1, x=x, z=AUGER_Z + z)
            for x in (-h, h) for z in (-h, h)]
    tab = [cyl_z(M3_CLEAR / 2, REAR_H - 1, REAR_H + TAB_T + 1, x=x, y=y) for x, y in tab_holes()]
    return cut_all(s, [bore, socket, inlet, shaft] + nema + tab)


def spout_body(r, extend=0.0):
    """Elbow + sloped tube of radius r, between the housing end and a vertical exit plane.

    `extend` pushes both planes outward, so a bore cut with it opens both ends cleanly.
    """
    import math
    start = spout_start()
    length = SPOUT_REACH / math.cos(math.radians(SPOUT_ANGLE)) + 2 * r
    s = cyl_dir(r, start, spout_dir(), length).fuse(Part.makeSphere(r, start))
    big = 4 * r + length
    y_exit = AUGER_Y0 - SPOUT_REACH - extend
    y_back = AUGER_Y0 + extend
    front = box(-big, y_exit - big, AUGER_Z - big, big, y_exit, AUGER_Z + big)
    behind = box(-big, y_back, AUGER_Z - big, big, y_back + big, AUGER_Z + big)
    return s.cut(front).cut(behind)


def make_spout():
    """Separate part: short sloped tube with a sleeve that slips onto the auger housing.

    The exit face is vertical, so nothing sticks out toward the cat's head.
    """
    ro = AUGER_ID / 2 + AUGER_WALL
    y0, y1 = AUGER_Y0, AUGER_Y0 + SPOUT_SLEEVE_L
    sleeve = cyl_y(ro + SPOUT_SLEEVE_T, y0, y1, z=AUGER_Z).cut(cyl_y(ro + 0.2, y0 - 1, y1 + 1, z=AUGER_Z))
    s = spout_body(ro).fuse(sleeve).cut(spout_body(AUGER_ID / 2, extend=1.0))
    grub = cyl_z(M3_PILOT / 2, AUGER_Z, AUGER_Z + ro + SPOUT_SLEEVE_T + 1, y=(y0 + y1) / 2)
    return s.cut(grub)


def hopper_z0():
    return AUGER_Z + AUGER_ID / 2 + AUGER_WALL


def make_hopper_segment(i):
    z0 = hopper_z0() + i * HOPPER_SEG_H
    z1 = z0 + HOPPER_SEG_H
    ro = HOPPER_ID / 2 + HOPPER_WALL
    s = cyl_z(ro, z0, z1, y=HOPPER_Y).cut(cyl_z(HOPPER_ID / 2, z0 - 1, z1 + 1, y=HOPPER_Y))
    if i < HOPPER_SEGMENTS - 1:
        # Socket on top: the next segment drops in.
        collar = cyl_z(ro + HOPPER_COLLAR_T, z1 - HOPPER_COLLAR_H, z1 + HOPPER_COLLAR_H, y=HOPPER_Y)
        s = s.fuse(collar.cut(cyl_z(ro + 0.3, z1, z1 + HOPPER_COLLAR_H + 1, y=HOPPER_Y))
                   .cut(cyl_z(HOPPER_ID / 2, z1 - HOPPER_COLLAR_H - 1, z1 + 1, y=HOPPER_Y)))
    return s


def make_lid():
    z0 = hopper_z0() + HOPPER_SEGMENTS * HOPPER_SEG_H
    z1 = z0 + LID_H
    ro = HOPPER_ID / 2 + HOPPER_WALL + 3
    s = cyl_z(ro, z0, z1, y=HOPPER_Y)
    skirt = cyl_z(HOPPER_ID / 2 + HOPPER_WALL + 0.3, z0 - 1, z1 - 4, y=HOPPER_Y)
    bw, bd = TOF_BOARD
    ww, wd = TOF_WINDOW
    board = box(-bw / 2, HOPPER_Y - bd / 2, z1 - 2.5, bw / 2, HOPPER_Y + bd / 2, z1 + 1)
    window = box(-ww / 2, HOPPER_Y - wd / 2, z0, ww / 2, HOPPER_Y + wd / 2, z1)
    return cut_all(s, [skirt, board, window])


def make_motor():
    return box(-NEMA / 2, AUGER_Y1 + NEMA_FLANGE_T, AUGER_Z - NEMA / 2,
               NEMA / 2, AUGER_Y1 + NEMA_FLANGE_T + NEMA_L, AUGER_Z + NEMA / 2)


def make_back_plate():
    hw = BASE_W / 2
    y0, y1 = REAR_D, REAR_D + BACK_T
    s = box(-hw, y0, 0, hw, y1, BACK_H)
    tools = [cyl_y(M4_CLEAR / 2, y0 - 1, y1 + 1, x=sx * 40, z=30) for sx in (-1, 1)]
    for sx in (-1, 1):
        tools += keyhole_y(sx * 55, BACK_H - 30, y0, y1)
    return cut_all(s, tools)


def make_upper_bracket():
    z0, z1 = UPPER_BRACKET_Z, UPPER_BRACKET_Z + UPPER_BRACKET_H
    y0, y1 = REAR_D, REAR_D + BACK_T
    ro = HOPPER_ID / 2 + HOPPER_WALL
    plate = box(-60, y0, z0, 60, y1, z1)
    arm = box(-12, HOPPER_Y, z0, 12, y0, z0 + 20)
    ring = cyl_z(ro + 4, z0, z0 + 20, y=HOPPER_Y)
    hole = cyl_z(ro + 0.3, z0 - 1, z0 + 21, y=HOPPER_Y)
    tools = [hole]
    for sx in (-1, 1):
        tools += keyhole_y(sx * 40, z1 - 30, y0, y1)
    return cut_all(plate.fuse([arm, ring]), tools)


# --- Build -------------------------------------------------------------------------------
PARTS = [
    # name, builder, printable, color
    ("FrontBase", make_front_base, True, (0.85, 0.85, 0.80)),
    ("RearBase", make_rear_base, True, (0.85, 0.85, 0.80)),
    ("BayDoor", make_bay_door, True, (0.75, 0.75, 0.70)),
    ("Bowl", make_bowl, True, (0.95, 0.60, 0.30)),
    ("AugerHousing", make_auger_housing, True, (0.40, 0.65, 0.90)),
    ("Spout", make_spout, True, (0.30, 0.55, 0.85)),
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
