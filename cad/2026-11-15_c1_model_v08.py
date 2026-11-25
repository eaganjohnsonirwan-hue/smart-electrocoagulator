"""v08 (round 10b, Eagan chose foam tape): ESP32 stuck with 1 mm double-sided foam tape (3M 1600T) on two 6 mm wide support bars,
no tie tunnels; bars 1 mm lower so the board stays 22 mm above the floor.
v07 (round 9b): ESP32 board moved 2 mm right (2,5 mm from both walls) so cable ties pass round its ends; support bars under the board ends
shortened to y 35-55 (clear of the header rows) with tie tunnels at y 36-40 (clear of the micro-USB plug); ESP32 size as constants; tie clearance assert.
v06 (round 8b): ESP32 raised to 22 mm (header + Dupont stack ~16,5 mm), tie tunnels through both support bars, USB window centred on the board,
INA219 raised 2 mm, ESP32-CAM rail lip overlaps the board by only 0,6 mm (header housings sit ~0,8 mm from the board edge), plate size as input (--plw, --plh).
v05 (round 7b): electronics box interior: ESP32 on two printed support bars 18 mm tall (tied with cable ties), USB window 13 x 10 mm
in the -x wall at the ESP32 port, INA219 tied to the back wall beside the DPDT, DPDT cutout moved to the left so its body clears the INA219,
clearance asserts; LED cable hole Ø4 in the optical chamber (-x wall); currents for 1-3 mA/cm2 in fit_report.txt; ESP32-CAM ledges and lips 2 mm wide (board rests 1,5 mm per side); cable notch moved to the front (-y) wall at x -44..-28, away from the M3 bolt at (-58, 47).
v04 (round 7): container inner size and height are parameters (--box, --h) with fit checks against the lid lip;
plates 99 x 149 (saw kerf); electronics box gets a 16 x 10 mm cable notch (USB plug passes) instead of the Ø8 hole;
ESP32-CAM rails raised (board on 1 mm ledges, CAM_CLEAR mm above the roof for the shield + camera module), board size and
lens offset are parameters to set from the team's measured board; siphon hole moved to (-47, -30); optical door rests on
the lid between its two guide rails; fit_report.txt gives water depth, siphon intake, marks and pipette dip for the box used.
v03: off-centre cylinders fixed, door guide rails. v02: colours, labels.
Blender model of concept C1 (integrated lid unit). Run headless:
  "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python 2026-11-15_c1_model_v08.py -- OUTDIR [--box 130] [--h 150] [--plw 99] [--plh 149]
Units: 1 Blender unit = 1 mm (STL files in mm). Dimensions follow drafts/2026-11-14_bab3_v07.md and the blueprint generator v12.
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = ARGS[0] if ARGS and not ARGS[0].startswith("--") else os.path.dirname(__file__)
def arg(name, default):
    return float(ARGS[ARGS.index(name) + 1]) if name in ARGS else default
os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)

# ---------------- design values (mm) ----------------
BOX_IN = arg("--box", 130.0)                # measured inner width = length of the container (13,0-14,0 cm allowed)
BOX_H = arg("--h", 150.0)                   # measured inner height (145-160 allowed)
WALL = 2.0
LID_T, LIP_T, LIP_D = 3.0, 2.0, 5.0
LID = BOX_IN + 14.0                         # lid overhangs the container by 7 mm per side
PL_W, PL_H, PL_T = arg("--plw", 99.0), arg("--plh", 149.0), 2.0   # measured plate after cutting (saw kerf ~1 mm)
assert 95.0 <= PL_W <= 100.0 and 145.0 <= PL_H <= 152.0, "plate must fit the 102 mm lid slots and the 132 mm hanger slot"
PLATE_Y = (-18.0, -6.0, 6.0, 18.0)          # plate centre planes, 12 mm pitch (10 mm gap)
Z_LID_TOP = BOX_H + LID_T
PL_BOT = Z_LID_TOP + 10.0 - 11.0 - 132.0    # plate hangs on bars: slot top (132 + 11 from plate bottom) = bar top
SPACER_Z = PL_BOT + 105.0
SLOT_Z0 = PL_BOT + 132.0                    # hanger slot 4 x 11 mm in plate
VOL = 1.5e6                                 # mm3 (1,5 L)
DEPTH = (VOL - 4 * PL_W * PL_T * PL_BOT) / (BOX_IN ** 2 - 4 * PL_W * PL_T)   # water depth with plates in place
HOLES = {"V1": (40, -44, 10), "V2": (-52, -42, 10), "selang": (-47, -30, 7), "pipet": (5, -55, 8),
         "termometer": (-30, -55, 5), "M3k1": (-58, 47, 3.2), "M3k2": (-6, 47, 3.2), "M3o1": (14, 36, 3.2), "M3o2": (44, 36, 3.2)}
POSTS = [(20, -24), (60, -24), (20, -64), (60, -64)]
EBOX = (-64.0, 29.0, 64.0, 36.0, 70.0)      # x0, y0, w, d, h  (outer)
NOTCH = (16.0, 10.0)                        # cable notch in the front (-y) wall, open at the lid: width (x) x height (z)
OCH = (8.0, 29.5, 42.0, 42.0, 81.0)         # optical chamber outer
# ESP32-CAM: AI-Thinker size by default. shortcut: not measured on the team's board; set from calipers, then re-export.
CAM_W, CAM_L, CAM_T = 27.0, 40.5, 1.6       # board width (x), length (y), thickness
CAM_CLEAR = 8.0                             # free height under the board for the shield + camera module
CAM_LENS = (0.0, 0.0)                       # lens centre offset from the board centre (x, y)

# ---------------- helpers ----------------
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"; sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = "MILLIMETERS"

def mat(name, rgba, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = rgba
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try: m.surface_render_method = "BLENDED"
        except Exception: pass
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    return m

def cube(name, x0, y0, z0, dx, dy, dz, m=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x0 + dx / 2, y0 + dy / 2, z0 + dz / 2))
    o = bpy.context.active_object; o.name = name; o.scale = (dx, dy, dz)
    bpy.ops.object.transform_apply(scale=True)
    if m: o.data.materials.append(m)
    return o

def cyl(name, x, y, z0, r, h, m=None, axis="Z", verts=48):
    """axis Z: base at z0. axis X/Y: centred on (x, y, z0)."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=(x, y, z0 + h / 2))
    o = bpy.context.active_object; o.name = name
    if axis == "Y":
        o.rotation_euler = (math.radians(90), 0, 0); o.location = (x, y, z0)
    if axis == "X":
        o.rotation_euler = (0, math.radians(90), 0); o.location = (x, y, z0)
    bpy.ops.object.transform_apply(rotation=True, location=False)
    if m: o.data.materials.append(m)
    return o

def cut(target, tool, keep=False):
    md = target.modifiers.new("cut", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = tool; md.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=md.name)
    if not keep: bpy.data.objects.remove(tool, do_unlink=True)

def join(target, other):
    md = target.modifiers.new("union", "BOOLEAN"); md.operation = "UNION"; md.object = other; md.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=md.name)
    bpy.data.objects.remove(other, do_unlink=True)

def shell(name, x0, y0, z0, w, d, h, t, m, open_top=False):
    o = cube(name, x0, y0, z0, w, d, h, m)
    inner = cube(name + "_in", x0 + t, y0 + t, z0 + t, w - 2 * t, d - 2 * t, h - (t if open_top else 2 * t) + (1 if open_top else 0))
    cut(o, inner)
    return o

def export_stl(o, fname):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
    path = os.path.join(OUT, "stl", fname)
    try:
        bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, global_scale=1.0, apply_modifiers=True)
    except AttributeError:
        bpy.ops.export_mesh.stl(filepath=path, use_selection=True, global_scale=1.0)
    return path

# ---------------- fit checks (fail loudly, before building) ----------------
h = BOX_IN / 2
LIP_IN = h - LIP_T                          # inner face of the lid lip
assert 130.0 <= BOX_IN <= 140.0, "container inner size must be 13,0-14,0 cm (hole layout and parts footprint)"
assert 15.0 <= PL_BOT <= 30.0, f"plate bottom {PL_BOT:.1f} mm above floor: inner height must be 145-160 mm"
for n, (x, y, d) in HOLES.items():
    assert abs(x) + d / 2 <= LIP_IN - 1.0 and abs(y) + d / 2 <= LIP_IN - 1.0, f"hole {n} hits the lid lip"
for (x0, y0, w, d) in ((EBOX[0], EBOX[1], EBOX[2], EBOX[3]), (OCH[0], OCH[1], OCH[2], OCH[3])):
    assert x0 >= -LID / 2 and x0 + w <= LID / 2 and y0 + d <= LID / 2, "box or chamber overhangs the lid"
assert DEPTH > PL_BOT + 40, "too little immersed plate height"
assert CAM_W + 1.0 <= OCH[2] - 6 - 4, "camera rails do not fit on the chamber roof"
assert abs(SLOT_Z0 + 11 - (Z_LID_TOP + 10)) < 1e-6, "slot top must rest on hanger bar top"

# ---------------- build ----------------
clear()
M_PLA = mat("PLA abu", (0.30, 0.40, 0.55, 1)); M_PLA_BK = mat("PLA hitam", (0.08, 0.08, 0.09, 1))
M_AL = mat("Al 1100", (0.62, 0.64, 0.68, 1)); M_BOX = mat("Wadah bening", (0.70, 0.85, 1.0, 1), 0.12)
M_WATER = mat("Air sungai", (0.55, 0.45, 0.30, 1), 0.35); M_NY = mat("Nilon", (0.95, 0.95, 0.9, 1))
M_TUBE = mat("Silikon", (0.92, 0.92, 0.92, 1), 0.7); M_FAN = mat("Kipas", (0.15, 0.15, 0.17, 1))
M_PCB = mat("PCB", (0.05, 0.35, 0.15, 1)); M_RED = mat("Klip", (0.8, 0.15, 0.12, 1)); M_SW = mat("Sakelar", (0.1, 0.1, 0.1, 1))

BOXNAME = f"Wadah {BOX_IN / 10:g}x{BOX_IN / 10:g}x{BOX_H / 10:g}"
box = shell(BOXNAME, -h - WALL, -h - WALL, -WALL, BOX_IN + 2 * WALL, BOX_IN + 2 * WALL, BOX_H + WALL, WALL, M_BOX, open_top=True)
water = cube("Air 1,5 L", -h, -h, 0, BOX_IN, BOX_IN, DEPTH, M_WATER)

# plates with spacer holes, hanger slots, siphon tie holes (plate 1, 5 mm from the left edge)
plates = []
for k, yc in enumerate(PLATE_Y):
    p = cube(f"Pelat {k + 1}", -PL_W / 2, yc - PL_T / 2, PL_BOT, PL_W, PL_T, PL_H, M_AL)
    for xh in (-40, 40):
        cut(p, cyl("h", xh, yc, SPACER_Z, 1.6, 10, axis="Y"))
        cut(p, cube("s", xh - 2, yc - 3, SLOT_Z0, 4, 6, 11))
    if k == 0:
        for zt in (60, 90):
            cut(p, cyl("t", -PL_W / 2 + 5, yc, PL_BOT + zt, 2.0, 10, axis="Y"))
    plates.append(p)
for xh in (-40, 40):          # nylon spacers between plates
    for a, b in zip(PLATE_Y[:-1], PLATE_Y[1:]):
        cyl("Spacer", xh, (a + b) / 2, SPACER_Z, 2.75, b - a - PL_T, M_NY, axis="Y")

# printed lid: plate + lip + posts with pins; slots and through-holes cut
lid = cube("Tutup (cetak)", -LID / 2, -LID / 2, BOX_H, LID, LID, LID_T, M_PLA)
lip = cube("bibir", -h, -h, BOX_H - LIP_D, BOX_IN, BOX_IN, LIP_D)
cut(lip, cube("bibir_in", -h + LIP_T, -h + LIP_T, BOX_H - LIP_D - 1, BOX_IN - 2 * LIP_T, BOX_IN - 2 * LIP_T, LIP_D + 2))
join(lid, lip)
for (px, py) in POSTS:
    join(lid, cyl("post", px, py, Z_LID_TOP, 3.0, 20.0))
    join(lid, cyl("pin", px, py, Z_LID_TOP + 20.0, 1.4, 4.0))
for yc in PLATE_Y:
    cut(lid, cube("slot", -51, yc - 1.5, BOX_H - 1, 102, 3, LID_T + 2))
for n, (x, y, d) in HOLES.items():
    cut(lid, cyl("hole", x, y, BOX_H - LIP_D - 1, d / 2, LIP_D + LID_T + 2))

# hanger bars (printed), standing on edge on the lid
bars = [cube(f"Batang penggantung {i + 1}", xb - 1.5, -28, Z_LID_TOP, 3, 56, 10, M_PLA) for i, xb in enumerate((-40, 40))]

# electronics box (printed): body open at top + top panel with DPDT cutout 22 x 30; cable notch at the lid in the -x wall
ex, ey, ew, ed, eh = EBOX
ebox = shell("Kotak elektronik (cetak)", ex, ey, Z_LID_TOP, ew, ed, eh - 3, 2.0, M_PLA, open_top=True)
for n in ("M3k1", "M3k2"):
    x, y, d = HOLES[n]; cut(ebox, cyl("h", x, y, Z_LID_TOP - 1, d / 2, 5))
cut(ebox, cube("takik kabel", ex + 20, ey - 1, Z_LID_TOP - 1, NOTCH[0], 4, NOTCH[1] + 1))
FLOOR = Z_LID_TOP + 2.0                     # top of the 2 mm box floor
ESP_Z = FLOOR + 22.0                        # ESP32 board underside: header 2,5 + pin 6 + Dupont housing 14 = ~16,5 mm below, plus room to bend wires
ESP_W, ESP_D = 55.0, 28.0                   # ESP32 DevKit board length (x) and width (y); measure in task 9a
ESP_X0 = ex + 4.5                           # board 2,5 mm from both inner walls (finger room to press it onto the tape)
TAPE_T = 1.0                                # 3M 1600T PE foam tape thickness
assert ESP_X0 - (ex + 2) >= 1.5 and (ex + ew - 2) - (ESP_X0 + ESP_W) >= 1.5, "board touches a side wall"
for xb in (ESP_X0 + 0.5, ESP_X0 + ESP_W - 6.5):   # two 6 mm support bars under the board ends, y 35-55 (header rows sit near y 33 and 57)
    bar = cube("batang tumpu", xb, ey + 6, FLOOR - 0.5, 6, 20, ESP_Z - TAPE_T - FLOOR + 0.5)   # 6 x 20 mm tape pad on top
    join(ebox, bar)
USB_WIN = (13.0, 10.0)                      # micro-USB plug ~11 x 7 mm; port on the board top at ESP_Z + 1,6 ... + 4,6
cut(ebox, cube("jendela USB", ex - 1, ey + 2 + 14 - USB_WIN[0] / 2,   # centred on the ESP32 board (y = ey + 16), not the box
     ESP_Z - 2.0, 4, USB_WIN[0], USB_WIN[1] - 0.0))
INA = (-29.0, Z_LID_TOP + 34.0, 25.0, 20.0)  # x0, z0, width (x), height (z); board against the back (+y) wall
for xs in (INA[0] - 2.5, INA[0] + INA[2] + 0.5):   # cable-tie slots 2 x 3 mm through the back wall, two heights
    for zs in (INA[1] + 4, INA[1] + INA[3] - 7):
        cut(ebox, cube("slot ikat", xs, ey + ed - 3, zs, 2, 4, 3))
DPDT_X0 = ex + 4.0                          # DPDT cutout 30 x 22 on the left of the roof
etop = cube("Atap kotak elektronik (cetak)", ex, ey, Z_LID_TOP + eh - 3, ew, ed, 3, M_PLA)
cut(etop, cube("dpdt", DPDT_X0, ey + ed / 2 - 11, Z_LID_TOP + eh - 4, 30, 22, 5))
cube("Sakelar DPDT", DPDT_X0 + 0.5, ey + ed / 2 - 10.5, Z_LID_TOP + eh, 29, 21, 6, M_SW)
cube("Badan + kaki DPDT (di bawah atap)", DPDT_X0 + 1, ey + ed / 2 - 10, Z_LID_TOP + eh - 3 - 30, 28, 20, 30, M_SW)
cube("ESP32 (PCB)", ESP_X0, ey + 2, ESP_Z, ESP_W, ESP_D, 1.6, M_PCB)
cube("INA219 (PCB + terminal)", INA[0], ey + ed - 2 - 12, INA[1], INA[2], 12, INA[3], M_PCB)
# clearance checks inside the box (boxes as x0, x1, y0, y1, z0, z1)
def ov(a, b):
    return all(a[2 * i] < b[2 * i + 1] and b[2 * i] < a[2 * i + 1] for i in range(3))
B_DPDT = (DPDT_X0 + 1, DPDT_X0 + 29, ey + ed / 2 - 10, ey + ed / 2 + 10, Z_LID_TOP + eh - 33, Z_LID_TOP + eh - 3)
B_INA = (INA[0], INA[0] + INA[2], ey + ed - 14, ey + ed - 2, INA[1], INA[1] + INA[3])
B_ESP = (ESP_X0, ESP_X0 + ESP_W, ey + 2, ey + 2 + ESP_D, ESP_Z - 18, ESP_Z + 6)   # incl. Dupont housings below, parts above
assert not ov(B_DPDT, B_INA) and not ov(B_DPDT, B_ESP) and not ov(B_INA, B_ESP), "parts collide inside the electronics box"
assert B_ESP[4] >= FLOOR, "Dupont plugs under the ESP32 hit the box floor"
assert B_INA[1] <= ex + ew - 2 and B_DPDT[0] >= ex + 2, "part outside the box"

# optical chamber (printed, black): walls 3 mm, door opening on +x side, lens hole, LED grooves, vial seat, camera rails
ox, oy, ow, od, oh = OCH
och = shell("Ruang optik (cetak)", ox, oy, Z_LID_TOP, ow, od, oh, 3.0, M_PLA_BK)
cut(och, cube("pintu", ox + ow - 4, oy + 6, Z_LID_TOP + 6, 6, od - 12, 66))
cx, cy = ox + ow / 2, oy + od / 2
cut(och, cyl("lensa", cx + CAM_LENS[0], cy + CAM_LENS[1], Z_LID_TOP + oh - 4, 4.0, 6))
for n in ("M3o1", "M3o2"):
    x, y, d = HOLES[n]; cut(och, cyl("h", x, y, Z_LID_TOP - 1, d / 2, 5))
cut(och, cyl("lubang kabel LED", ox, cy, Z_LID_TOP + 65, 2.0, 8, axis="X"))   # Ø4, sealed with black tape
for ys in (oy + 3 - 1.5, oy + od - 3 - 0.0):
    cut(och, cube("led", cx - 5, ys, Z_LID_TOP + 6, 10, 1.5, 50))
seat = cyl("dudukan", cx, cy, Z_LID_TOP + 3, 13.5, 3); cut(seat, cyl("in", cx, cy, Z_LID_TOP + 2, 11.5, 5)); join(och, seat)
RAIL_H = CAM_CLEAR + CAM_T + 0.5 + 1.5      # ledge, board, clearance, lip
gap_half = CAM_W / 2 + 0.5                  # 0,5 mm side clearance
for sgn in (-1, 1):                         # rails along y; board slides in from one end
    x_in = cx + sgn * gap_half
    rail = cube("rel", x_in if sgn > 0 else x_in - 2, cy - od / 2, Z_LID_TOP + oh, 2, od, RAIL_H)
    lx = x_in - 2 if sgn > 0 else x_in      # ledge and lip 2 mm wide: 1,5 mm under/over the board edge
    join(rail, cube("tumpuan", lx, cy - od / 2, Z_LID_TOP + oh, 2, od, CAM_CLEAR))
    # lip 1,1 mm wide = 0,5 mm side clearance + 0,6 mm over the board edge, so it clears the header housings
    join(rail, cube("bibir_rel", x_in - 1.1 if sgn > 0 else x_in, cy - od / 2, Z_LID_TOP + oh + CAM_CLEAR + CAM_T + 0.5, 1.1, od, 1.5))
    join(och, rail)
for yg in (oy + 4 - 2, oy + od - 4):        # door guide rails on the +x face, from the lid up
    g = cube("rel_pintu", ox + ow, yg, Z_LID_TOP, 3, 2, 76)
    join(g, cube("bibir_pintu", ox + ow + 2, yg + (1 if yg < cy else -1), Z_LID_TOP, 1, 2, 76))
    join(och, g)
# door: rests on the lid between the rails, covers the opening (6-72 mm), finger tab on top
door = cube("Pintu ruang optik (cetak)", ox + ow + 0.25, oy + 4.25, Z_LID_TOP, 1.5, od - 8.5, 76, M_PLA_BK)
join(door, cube("tab", ox + ow + 0.25, cy - 6, Z_LID_TOP + 76, 1.5, 12, 6))
cube("ESP32-CAM", cx - CAM_W / 2, cy - CAM_L / 2, Z_LID_TOP + oh + CAM_CLEAR, CAM_W, CAM_L, CAM_T, M_PCB)
cyl("Vial 10 mL", cx, cy, Z_LID_TOP + 6, 11, 50, M_TUBE)

# fan on posts, clips (one per plate), siphon, stir bar
fan = cube("Kipas 5 V 50x50", 40 - 25, -44 - 25, Z_LID_TOP + 20, 50, 50, 10, M_FAN)
cut(fan, cyl("rotor", 40, -44, Z_LID_TOP + 19, 23, 12))
for (x, y) in ((-46, -18), (-46, 6), (46, -6), (46, 18)):
    cube("Klip buaya", x - 3, y - 4, PL_BOT + PL_H - 8, 6, 8, 10, M_RED)
cyl("Selang sifon", -47, -29, DEPTH / 2, 3.0, Z_LID_TOP + 15 - DEPTH / 2, M_TUBE)
cyl("Batang pengaduk", 0, -12.5, 2, 4, 25, M_NY, axis="Y")

# ---------------- export printed parts ----------------
printed = {"Tutup (cetak)": "tutup.stl", "Batang penggantung 1": "batang_penggantung.stl",
           "Kotak elektronik (cetak)": "kotak_elektronik_badan.stl", "Atap kotak elektronik (cetak)": "kotak_elektronik_atap.stl",
           "Ruang optik (cetak)": "ruang_optik_badan.stl", "Pintu ruang optik (cetak)": "ruang_optik_pintu.stl"}
vols = {}
for name, fn in printed.items():
    o = bpy.data.objects[name]
    bm = bmesh.new(); bm.from_mesh(o.data); vols[fn] = round(abs(bm.calc_volume()) / 1000.0, 2); bm.free()   # cm3
    export_stl(o, fn)

# ---------------- render ----------------
sc = bpy.context.scene
for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
    try:
        sc.render.engine = eng; break
    except TypeError:
        continue
sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
sc.render.film_transparent = False
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.35
try:
    sc.view_settings.view_transform = "Standard"
except Exception:
    pass
bpy.ops.object.light_add(type="SUN", location=(200, -200, 400)); bpy.context.active_object.data.energy = 3.0
bpy.context.active_object.rotation_euler = (math.radians(40), 0, math.radians(35))
bpy.ops.object.camera_add(location=(330, -360, 330)); cam = bpy.context.active_object; sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = 380
direction = Vector((0, 0, 125)) - cam.location; cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
from bpy_extras.object_utils import world_to_camera_view
import json
LABELS = {"1": ("Tutup (cetak)", (-60, -60, Z_LID_TOP)), "2": ("Pelat 1", (25, -19, 60)), "3": ("Batang penggantung 1", (-40, -28, Z_LID_TOP + 10)),
          "4": ("Kipas 5 V 50x50", (15, -69, Z_LID_TOP + 30)), "5": ("Kotak elektronik (cetak)", (-64, 29, Z_LID_TOP + 50)),
          "6": ("Ruang optik (cetak)", (50, 29.5, Z_LID_TOP + 60)), "7": ("Selang sifon", (-47, -29, 60)),
          "8": ("Klip buaya", (-46, -18, PL_BOT + PL_H)), "9": (BOXNAME, (67, -67, 40)), "10": ("Batang pengaduk", (0, -12, 4)),
          "11": ("Sakelar DPDT", (-32, 47, Z_LID_TOP + 76))}
STATIC = (BOXNAME, "Air 1,5 L", "Batang pengaduk")
def dump_labels(fname, dz=0.0):
    pts = {}
    for k, (n, (x, y, z)) in LABELS.items():
        zz = z + (dz if n not in STATIC else 0.0)
        v = world_to_camera_view(sc, cam, Vector((x, y, zz)))
        pts[k] = [round(v.x, 4), round(1 - v.y, 4)]
    json.dump(pts, open(os.path.join(OUT, fname), "w"))
bpy.context.view_layer.update()
dump_labels("label_rakitan.json")
sc.render.filepath = os.path.join(OUT, "render_rakitan.png"); bpy.ops.render.render(write_still=True)

lift = 120.0                                 # exploded: lift the lid unit by 120 mm
for o in bpy.data.objects:
    if o.type == "MESH" and o.name not in STATIC:
        o.location.z += lift
cam.data.ortho_scale = 500; direction = Vector((0, 0, 185)) - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler(); bpy.context.view_layer.update()
dump_labels("label_terurai.json", dz=lift)
sc.render.filepath = os.path.join(OUT, "render_terurai.png"); bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.type == "MESH" and o.name not in STATIC:
        o.location.z -= lift

# orthographic views for the open blueprint: front (-y), right side (+x), top
sc.render.resolution_x, sc.render.resolution_y = 1400, 1400
for tag, loc, rot in (("depan", (0, -600, 110), (math.radians(90), 0, 0)),
                      ("samping", (600, 0, 110), (math.radians(90), 0, math.radians(90))),
                      ("atas", (0, 0, 700), (0, 0, 0))):
    cam.location = loc; cam.rotation_euler = rot; cam.data.ortho_scale = 280
    sc.render.filepath = os.path.join(OUT, f"ortho_{tag}.png"); bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "2026-11-15_c1_model_v08.blend"))
mass = {k: round(v * 1.24 * 0.75, 1) for k, v in vols.items()}   # g, PLA 1,24 g/cm3, ~75 % effective fill
with open(os.path.join(OUT, "print_volumes.txt"), "w", encoding="utf-8") as f:
    f.write("part,volume_cm3,mass_g_at_75pct\n")
    for k in vols: f.write(f"{k},{vols[k]},{mass[k]}\n")
    f.write(f"TOTAL (2 hanger bars),{round(sum(vols.values()) + vols['batang_penggantung.stl'], 2)},{round(sum(mass.values()) + mass['batang_penggantung.stl'], 1)}\n")
with open(os.path.join(OUT, "fit_report.txt"), "w", encoding="utf-8") as f:
    f.write(f"container inner {BOX_IN:g} x {BOX_IN:g} mm, height {BOX_H:g} mm; lid {LID:g} x {LID:g} mm\n")
    f.write(f"plate bottom above floor: {PL_BOT:.1f} mm; plate top above lid top: {PL_BOT + PL_H - Z_LID_TOP:.1f} mm\n")
    f.write(f"water depth at 1,5 L: {DEPTH:.1f} mm (fill mark); immersed plate height: {DEPTH - PL_BOT:.1f} mm\n")
    f.write(f"active area (3 anode-cathode pairs, one face each): {3 * PL_W * (DEPTH - PL_BOT) / 100:.0f} cm2 (from plan size; use measured plates)\n")
    A_cm2 = 3 * PL_W * (DEPTH - PL_BOT) / 100
    f.write("currents for 1 / 2 / 3 mA/cm2 on this area: " + " / ".join(f"{j * A_cm2 / 1000:.3f} A" for j in (1, 2, 3)) + "\n")
    f.write(f"plates {PL_W:.0f} x {PL_H:.0f} mm; ESP32 board underside {ESP_Z - FLOOR:.0f} mm above the electronics-box floor\n")
    f.write(f"siphon intake: {DEPTH / 2:.1f} mm above floor; siphon stop mark: {DEPTH / 2 + 5:.1f} mm above floor\n")
    f.write(f"pipette dip mark from lid top: {Z_LID_TOP - DEPTH / 2:.1f} mm\n")
    left = (BOX_IN ** 2 * (DEPTH / 2 + 5) - 4 * PL_W * PL_T * max(DEPTH / 2 + 5 - PL_BOT, 0)) / 1e6
    f.write(f"water left at siphon stop: {left:.2f} L; siphon yield (before sampling losses): {1.5 - left:.2f} L\n")
print("DONE", vols, "depth", round(DEPTH, 2))
