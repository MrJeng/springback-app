"""
เครื่องคำนวณสปริงสตริปเปอร์ - แม่พิมพ์กดตัด (Stamping Die Stripper Spring Calculator)
เวอร์ชัน GUI ด้วย tkinter (ไลบรารีมาตรฐานของ Python ไม่ต้องติดตั้งเพิ่ม)
--------------------------------------------------------------------------------
กรอกค่าด้านซ้าย ผลลัพธ์และตารางสปริงแนะนำจะอัปเดตอัตโนมัติทางขวา
"""

import math
import tkinter as tk
from tkinter import ttk

# ----------------------------------------------------------------------
# ฐานข้อมูลวัสดุแผ่นงาน: แรงเฉือน (MPa) และ K_strip เริ่มต้น (สัดส่วนของแรงตัด)
# ----------------------------------------------------------------------
MATERIALS = [
    ("เหล็กเหนียวรีดเย็น (SPCC / Mild steel)", 350, 5.0),
    ("สแตนเลส (SUS304)",                        450, 8.0),
    ("อะลูมิเนียม (Al 5052)",                    170, 3.0),
    ("ทองแดง (Copper)",                          220, 4.0),
    ("ทองเหลือง (Brass)",                        280, 4.0),
]

# ----------------------------------------------------------------------
# แคตตาล็อกสปริงมาตรฐาน (จำลองแบบประมาณ อิงมาตรฐานสี ISO 10243)
# ----------------------------------------------------------------------
ODS = [10, 13, 16, 20, 25, 32, 40, 50]
LENGTHS = [25, 32, 38, 51, 64, 76, 102, 127]
BASE_RATE_AT25 = {10: 60, 13: 90, 16: 140, 20: 220, 25: 340, 32: 520, 40: 780, 50: 1150}

DUTIES = [
    {"key": "L",  "name": "เบา (Light)",            "color_name": "เหลือง", "color": "#c9a92a", "mult": 1.0, "max_pct": 0.45},
    {"key": "M",  "name": "กลาง (Medium)",           "color_name": "น้ำเงิน", "color": "#3f7fc1", "mult": 1.6, "max_pct": 0.40},
    {"key": "H",  "name": "หนัก (Heavy)",            "color_name": "แดง",    "color": "#c9503b", "mult": 2.4, "max_pct": 0.35},
    {"key": "XH", "name": "หนักพิเศษ (Extra Heavy)", "color_name": "เขียว",  "color": "#3fb383", "mult": 3.4, "max_pct": 0.30},
]


def spring_rate(od, length, duty):
    return BASE_RATE_AT25[od] * (25 / length) * duty["mult"]


def max_deflection(length, duty):
    return length * duty["max_pct"]


def best_for_duty(duty, x_req, f_design, cap_springs):
    best = None
    for od in ODS:
        valid_lengths = [l for l in LENGTHS if max_deflection(l, duty) >= x_req]
        if not valid_lengths:
            continue
        length = min(valid_lengths)
        k = spring_rate(od, length, duty)
        f_spring = k * x_req
        n = math.ceil(f_design / f_spring) if f_spring > 0 else float("inf")
        total = n * f_spring
        candidate = {
            "duty": duty, "od": od, "length": length, "k": k,
            "max_def": max_deflection(length, duty),
            "f_spring": f_spring, "n": n, "total": total,
        }
        if n <= cap_springs:
            return candidate
        if best is None or n < best["n"]:
            best = candidate
    return best


def recommend_springs(x_req, f_design, cap_springs):
    results = []
    for duty in DUTIES:
        cand = best_for_duty(duty, x_req, f_design, cap_springs)
        if cand:
            results.append(cand)
    results.sort(key=lambda r: (r["n"] > cap_springs, r["n"], r["od"]))
    return results


# ========================================================================
# GUI
# ========================================================================
BG = "#16202b"
PANEL = "#1d2b38"
PANEL2 = "#223243"
LINE = "#33465a"
AMBER = "#e8a33d"
TEAL = "#4fd1a5"
RED = "#e2664f"
TEXT = "#eef2f5"
TEXT_DIM = "#93a7ba"


class SpringCalcApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("เครื่องคำนวณสปริงสตริปเปอร์ - แม่พิมพ์กดตัด")
        self.geometry("980x680")
        self.configure(bg=BG)
        self.minsize(860, 600)

        self._build_style()
        self._build_layout()
        self.recs = []
        self.selected_index = 0
        self.calculate()  # คำนวณครั้งแรกด้วยค่าเริ่มต้น

    # ------------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=PANEL)
        style.configure("Head.TLabel", background=BG, foreground=TEXT,
                         font=("Segoe UI", 16, "bold"))
        style.configure("Sub.TLabel", background=BG, foreground=TEXT_DIM,
                         font=("Segoe UI", 10))
        style.configure("PanelTitle.TLabel", background=PANEL, foreground=TEXT_DIM,
                         font=("Segoe UI", 10, "bold"))
        style.configure("Field.TLabel", background=PANEL, foreground=TEXT_DIM,
                         font=("Segoe UI", 9))
        style.configure("TEntry", fieldbackground=PANEL2, foreground=TEXT,
                         insertcolor=TEXT, bordercolor=LINE)
        style.configure("TCombobox", fieldbackground=PANEL2, foreground=TEXT,
                         background=PANEL2)
        style.configure("Result.TLabel", background=PANEL, foreground=TEXT,
                         font=("Consolas", 15, "bold"))
        style.configure("ResultAccent.TLabel", background=PANEL, foreground=AMBER,
                         font=("Consolas", 15, "bold"))
        style.configure("ResultKey.TLabel", background=PANEL, foreground=TEXT_DIM,
                         font=("Segoe UI", 9))
        style.configure("Status.TLabel", background=PANEL, foreground=TEAL,
                         font=("Segoe UI", 10))
        style.configure("Treeview", background=PANEL2, fieldbackground=PANEL2,
                         foreground=TEXT, rowheight=26, font=("Consolas", 10))
        style.configure("Treeview.Heading", background=PANEL, foreground=TEXT_DIM,
                         font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#2c3f52")])

    # ------------------------------------------------------------------
    def _build_layout(self):
        header = ttk.Frame(self, style="TFrame")
        header.configure(style="TFrame")
        header_wrap = tk.Frame(self, bg=BG)
        header_wrap.pack(fill="x", padx=18, pady=(16, 10))
        tk.Label(header_wrap, text="เครื่องคำนวณสปริงสตริปเปอร์ — แม่พิมพ์กดตัด",
                  bg=BG, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(header_wrap,
                  text="คำนวณแรงตัด แรงสตริป แรงกดรวม และแนะนำสเปกสปริงมาตรฐาน (ISO 10243)",
                  bg=BG, fg=TEXT_DIM, font=("Segoe UI", 9)).pack(anchor="w")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=(0, 14))
        body.columnconfigure(0, weight=0, minsize=300)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_input_panel(body)
        self._build_result_panel(body)

    # ------------------------------------------------------------------
    def _build_input_panel(self, parent):
        panel = tk.Frame(parent, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(panel, text="ค่าที่ป้อน", bg=PANEL, fg=TEXT_DIM,
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 6))

        form = tk.Frame(panel, bg=PANEL)
        form.pack(fill="x", padx=14, pady=4)

        # วัสดุ
        tk.Label(form, text="วัสดุแผ่นงาน (workpiece)", bg=PANEL, fg=TEXT_DIM,
                  font=("Segoe UI", 9)).grid(row=0, column=0, columnspan=2, sticky="w", pady=(6, 2))
        self.material_var = tk.StringVar(value=MATERIALS[0][0])
        material_names = [m[0] for m in MATERIALS] + ["กำหนดเอง..."]
        self.material_combo = ttk.Combobox(form, textvariable=self.material_var,
                                            values=material_names, state="readonly", width=34)
        self.material_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.material_combo.bind("<<ComboboxSelected>>", self.on_material_change)

        self.tau_var = tk.StringVar(value="350")
        self.thickness_var = tk.StringVar(value="1.2")
        self.perimeter_var = tk.StringVar(value="220")
        self.kstrip_var = tk.StringVar(value="5")
        self.sf_var = tk.StringVar(value="1.3")
        self.stroke_var = tk.StringVar(value="5.2")
        self.preload_var = tk.StringVar(value="3")
        self.cap_var = tk.StringVar(value="6")

        self._add_field(form, 2, "แรงเฉือนวัสดุ τ (MPa)", self.tau_var)
        self._add_field(form, 4, "ความหนาแผ่น t (mm)", self.thickness_var)
        self._add_field(form, 6, "เส้นรอบรูปตัดรวม L (mm)", self.perimeter_var)
        self._add_field(form, 8, "สัมประสิทธิ์แรงสตริป K_strip (%)", self.kstrip_var)
        self._add_field(form, 10, "ค่าความปลอดภัย Safety Factor (SF)", self.sf_var)
        self._add_field(form, 12, "ระยะสโตรกทำงานสตริปเปอร์ s (mm)", self.stroke_var)
        self._add_field(form, 14, "ระยะอัดตั้งต้น preload (mm)", self.preload_var)
        self._add_field(form, 16, "จำนวนสปริงสูงสุดต่อชุด", self.cap_var)

        form.columnconfigure(0, weight=1)

        btn = tk.Button(panel, text="คำนวณ / รีเฟรช", command=self.calculate,
                          bg=AMBER, fg="#1b1200", activebackground="#f0b45c",
                          font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2")
        btn.pack(fill="x", padx=14, pady=(10, 6))

        formula_btn = tk.Button(panel, text="สูตรที่ใช้คำนวณ", command=self.show_formula_window,
                                  bg=PANEL2, fg=TEXT, activebackground=LINE,
                                  font=("Segoe UI", 9), relief="flat", cursor="hand2",
                                  highlightbackground=LINE, highlightthickness=1)
        formula_btn.pack(fill="x", padx=14, pady=(0, 14))

    def _add_field(self, form, row, label, var):
        tk.Label(form, text=label, bg=PANEL, fg=TEXT_DIM,
                  font=("Segoe UI", 9)).grid(row=row, column=0, columnspan=2, sticky="w", pady=(6, 2))
        entry = ttk.Entry(form, textvariable=var, width=20)
        entry.grid(row=row + 1, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        entry.bind("<KeyRelease>", lambda e: self.calculate())

    def on_material_change(self, event=None):
        idx = self.material_combo.current()
        if 0 <= idx < len(MATERIALS):
            _, tau, kstrip = MATERIALS[idx]
            self.tau_var.set(str(tau))
            self.kstrip_var.set(str(kstrip))
        self.calculate()

    # ------------------------------------------------------------------
    def _build_result_panel(self, parent):
        panel = tk.Frame(parent, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        panel.grid(row=0, column=1, sticky="nsew")

        tk.Label(panel, text="ผลการคำนวณ", bg=PANEL, fg=TEXT_DIM,
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(12, 6))

        grid = tk.Frame(panel, bg=PANEL)
        grid.pack(fill="x", padx=14, pady=(0, 10))
        for c in range(3):
            grid.columnconfigure(c, weight=1)

        self.out_fcut = self._result_card(grid, 0, 0, "แรงตัด F_cut", "TEXT")
        self.out_fstrip = self._result_card(grid, 0, 1, "แรงสตริปที่ต้องการ", "TEXT")
        self.out_fdesign = self._result_card(grid, 0, 2, "แรงออกแบบสปริง (×SF)", "AMBER")
        self.out_fpress = self._result_card(grid, 1, 0, "แรงกดรวมเครื่องปั๊ม (N)", "AMBER", colspan=1)
        self.out_fpress_ton = self._result_card(grid, 1, 1, "แรงกดรวม (ตัน)", "AMBER", colspan=1)
        self.out_size = self._result_card(grid, 1, 2, "สปริงแนะนำ (OD × L)", "TEAL")

        self.status_label = tk.Label(panel, text="", bg=PANEL, fg=TEAL,
                                       font=("Segoe UI", 10), wraplength=560, justify="left")
        self.status_label.pack(anchor="w", padx=14, pady=(2, 10), fill="x")

        tk.Label(panel, text="สปริงมาตรฐานที่แนะนำ (เรียงจากเหมาะสมที่สุด)", bg=PANEL, fg=TEXT_DIM,
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(4, 6))

        cols = ("duty", "size", "k", "maxdef", "qty", "total", "fit")
        headers = {"duty": "เกรด", "size": "ขนาด OD×L", "k": "k (N/mm)",
                   "maxdef": "ยุบสูงสุด (mm)", "qty": "จำนวน", "total": "แรงรวม (N)", "fit": "สถานะ"}
        self.tree = ttk.Treeview(panel, columns=cols, show="headings", height=5)
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=110, anchor="center")
        self.tree.column("duty", width=150, anchor="w")
        self.tree.pack(fill="x", padx=14, pady=(0, 10))
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        tk.Label(panel, text="ภาพประกอบสปริงที่เลือก", bg=PANEL, fg=TEXT_DIM,
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(4, 6))
        self.spring_canvas = tk.Canvas(panel, bg=PANEL2, height=210,
                                        highlightbackground=LINE, highlightthickness=1)
        self.spring_canvas.pack(fill="x", padx=14, pady=(0, 6))
        self.spring_canvas.bind("<Configure>", lambda e: self.draw_spring_illustration())

        note = ("หมายเหตุ: ค่าอัตราสปริง (k) เป็นค่าประมาณเชิงวิศวกรรมเพื่อการศึกษา อิงมาตรฐานสี ISO 10243\n"
                "(เหลือง=เบา, น้ำเงิน=กลาง, แดง=หนัก, เขียว=หนักพิเศษ) ก่อนสั่งซื้อจริงควรเทียบกับแคตตาล็อกผู้ผลิต "
                "เช่น Misumi, Raymond, Danly")
        tk.Label(panel, text=note, bg=PANEL, fg=TEXT_DIM, font=("Segoe UI", 8),
                  wraplength=600, justify="left").pack(anchor="w", padx=14, pady=(0, 12))

    def _result_card(self, parent, row, col, title, color_key, colspan=1):
        card = tk.Frame(parent, bg=PANEL2, highlightbackground=LINE, highlightthickness=1)
        card.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=4, pady=4)
        tk.Label(card, text=title, bg=PANEL2, fg=TEXT_DIM,
                  font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        color = {"TEXT": TEXT, "AMBER": AMBER, "TEAL": TEAL, "RED": RED}[color_key]
        value_label = tk.Label(card, text="–", bg=PANEL2, fg=color, font=("Consolas", 15, "bold"))
        value_label.pack(anchor="w", padx=10, pady=(0, 10))
        return value_label

    # ------------------------------------------------------------------
    def show_formula_window(self):
        win = tk.Toplevel(self)
        win.title("สูตรที่ใช้คำนวณ")
        win.configure(bg=BG)
        win.geometry("640x620")
        win.minsize(480, 400)

        tk.Label(win, text="สูตรที่ใช้คำนวณ", bg=BG, fg=TEXT,
                  font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=(14, 8))

        outer = tk.Frame(win, bg=BG)
        outer.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        canvas = tk.Canvas(outer, bg=PANEL, highlightbackground=LINE,
                            highlightthickness=1, bd=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=PANEL)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        formulas = [
            ("แรงตัด (Cutting force)", "F_cut = L × t × τ", [
                "L = เส้นรอบรูปตัดรวม (mm) — ผลรวมความยาวคมตัดของทุกรูที่ตัดพร้อมกัน",
                "t = ความหนาแผ่นงาน (mm)",
                "τ = แรงเฉือนของวัสดุแผ่นงาน (MPa) — ขึ้นกับชนิดวัสดุที่เลือก",
            ]),
            ("แรงสตริปที่ต้องการ", "F_strip = K_strip × F_cut", [
                "K_strip = สัมประสิทธิ์แรงสตริป (%) — สัดส่วนแรงดันแผ่นงานออกจากปัญจ์ เทียบกับแรงตัด (ทั่วไป 2–20%)",
                "F_cut = แรงตัดที่คำนวณได้จากสูตรด้านบน (N)",
            ]),
            ("แรงกดรวมที่เครื่องปั๊มต้องรับ", "F_press = F_cut + F_strip", [
                "แรงรวมที่เครื่องปั๊ม (press) ต้องออกแรงตลอดสโตรก ใช้เทียบกับพิกัดตันของเครื่อง",
            ]),
            ("แรงออกแบบสปริง", "F_design = F_strip × SF", [
                "SF = ค่าความปลอดภัย (Safety Factor) — เผื่อความไม่แน่นอน เช่น ความฝืด/สนิม (ทั่วไป 1.2–1.5)",
            ]),
            ("แรงต่อสปริง ณ ระยะยุบรวม", "F_spring = k × (preload + stroke)", [
                "k = อัตราสปริง (N/mm) — แรงที่สปริงต้านต่อระยะยุบ 1 มม. (จากสปริงที่เลือกในตาราง)",
                "preload = ระยะอัดตั้งต้นตอนประกอบสปริงลงในแม่พิมพ์ (mm)",
                "stroke = ระยะสโตรกทำงานของสตริปเปอร์ขณะตัด (mm)",
            ]),
            ("จำนวนสปริง", "n = ⌈ F_design ÷ F_spring ⌉", [
                "⌈ ⌉ หมายถึงปัดเศษขึ้นเป็นจำนวนเต็ม (round up)",
                "จำนวนสปริงต้องเผื่อจนแรงรวมไม่น้อยกว่าแรงออกแบบ",
            ]),
        ]

        for i, (name, eq, legend) in enumerate(formulas):
            row = tk.Frame(inner, bg=PANEL)
            row.pack(fill="x", padx=16, pady=(12 if i == 0 else 10, 0))
            if i > 0:
                sep = tk.Frame(inner, bg=LINE, height=1)
                sep.pack(fill="x", padx=16, pady=(10, 0))

            tk.Label(row, text=name, bg=PANEL, fg=TEXT_DIM,
                      font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(row, text=eq, bg=PANEL, fg=AMBER,
                      font=("Consolas", 13, "bold")).pack(anchor="w", pady=(2, 4))
            for line in legend:
                tk.Label(row, text="•  " + line, bg=PANEL, fg=TEXT_DIM,
                          font=("Segoe UI", 9), wraplength=560, justify="left").pack(anchor="w", pady=1)

        tk.Frame(inner, bg=PANEL, height=10).pack()

        tk.Button(win, text="ปิด", command=win.destroy, bg=PANEL2, fg=TEXT,
                   activebackground=LINE, relief="flat", font=("Segoe UI", 9),
                   cursor="hand2").pack(anchor="e", padx=16, pady=(0, 14))

    # ------------------------------------------------------------------
    def _to_float(self, var, default=0.0):
        try:
            return float(var.get())
        except ValueError:
            return default

    def calculate(self):
        tau = self._to_float(self.tau_var, 350)
        t = self._to_float(self.thickness_var, 1.2)
        L = self._to_float(self.perimeter_var, 220)
        kstrip_pct = self._to_float(self.kstrip_var, 5)
        sf = self._to_float(self.sf_var, 1.3)
        stroke = self._to_float(self.stroke_var, 5.2)
        preload = self._to_float(self.preload_var, 3)
        cap_springs = int(self._to_float(self.cap_var, 6))
        if cap_springs <= 0:
            cap_springs = 1

        f_cut = L * t * tau
        f_strip = f_cut * (kstrip_pct / 100)
        f_press = f_cut + f_strip
        f_press_ton = f_press / 9806.65
        f_design = f_strip * sf
        x_req = preload + stroke

        self.out_fcut.config(text=f"{f_cut:,.0f} N")
        self.out_fstrip.config(text=f"{f_strip:,.0f} N")
        self.out_fdesign.config(text=f"{f_design:,.0f} N")
        self.out_fpress.config(text=f"{f_press:,.0f} N")
        self.out_fpress_ton.config(text=f"{f_press_ton:,.2f} ตัน")

        recs = recommend_springs(x_req, f_design, cap_springs)
        self.recs = recs
        self.selected_index = 0

        for row in self.tree.get_children():
            self.tree.delete(row)

        if not recs:
            self.out_size.config(text="–")
            self.status_label.config(
                text="ไม่พบสปริงที่รองรับระยะยุบที่ต้องการ ลองลดระยะสโตรกหรือ preload",
                fg=RED)
            self.spring_canvas.delete("all")
            return

        best = recs[0]
        self.out_size.config(text=f"⌀{best['od']} × {best['length']} mm")

        for idx, r in enumerate(recs):
            fit_ok = r["n"] <= cap_springs
            fit_text = "พอดี" if fit_ok else "เกินจำนวน"
            size = f"⌀{r['od']} × {r['length']} mm"
            item_id = self.tree.insert("", "end", iid=str(idx), values=(
                r["duty"]["name"], size, f"{r['k']:.1f}", f"{r['max_def']:.1f}",
                r["n"], f"{r['total']:,.0f}", fit_text
            ), tags=(r["duty"]["key"],))
            self.tree.tag_configure(r["duty"]["key"], foreground=r["duty"]["color"])

        self.tree.selection_set("0")

        if best["n"] > cap_springs:
            self.status_label.config(
                text=(f"สปริงเกรด {best['duty']['name']} ⌀{best['od']}×{best['length']} mm "
                      f"ต้องใช้ {best['n']} ตัว เกินจำนวนสูงสุดที่ตั้งไว้ ({cap_springs}) "
                      f"ลองเพิ่มจำนวนสูงสุด หรือใช้เกรดที่รับแรงสูงขึ้น"),
                fg=RED)
        else:
            self.status_label.config(
                text=(f"แนะนำ: สปริงเกรด {best['duty']['name']} ⌀{best['od']}×{best['length']} mm "
                      f"จำนวน {best['n']} ตัว ให้แรงรวม {best['total']:,.0f} N "
                      f"≥ แรงออกแบบ {f_design:,.0f} N (ระยะยุบใช้งาน {x_req:.1f} mm "
                      f"ไม่เกินระยะยุบสูงสุด {best['max_def']:.1f} mm)"),
                fg=TEAL)

        self.draw_spring_illustration()

    def on_tree_select(self, event=None):
        sel = self.tree.selection()
        if not sel or not self.recs:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self.recs):
            self.selected_index = idx
            r = self.recs[idx]
            self.out_size.config(text=f"⌀{r['od']} × {r['length']} mm")
            self.draw_spring_illustration()

    def draw_spring_illustration(self):
        canvas = self.spring_canvas
        canvas.delete("all")
        if not self.recs or self.selected_index >= len(self.recs):
            return
        r = self.recs[self.selected_index]
        duty = r["duty"]
        color = duty["color"]

        w = canvas.winfo_width() or 860
        h = 210
        cx = w // 2
        top_y = 34
        bottom_y = h - 40
        coil_h = bottom_y - top_y
        body_r = min(70, 14 + r["od"] * 1.7)
        turns = 8
        seg = coil_h / turns

        # end caps
        canvas.create_line(cx - body_r - 4, top_y, cx + body_r + 4, top_y, fill=color, width=4)
        canvas.create_line(cx - body_r - 4, bottom_y, cx + body_r + 4, bottom_y, fill=color, width=4)

        # zigzag coil body (classic spring symbol)
        points = []
        for i in range(turns + 1):
            x = cx + body_r if i % 2 == 0 else cx - body_r
            y = top_y + i * seg
            points.extend([x, y])
        canvas.create_line(*points, fill=color, width=4, joinstyle="round", capstyle="round")

        # OD dimension (top, horizontal)
        dim_y = top_y - 16
        canvas.create_line(cx - body_r, dim_y, cx + body_r, dim_y, fill=TEXT_DIM)
        canvas.create_line(cx - body_r, dim_y - 5, cx - body_r, top_y, fill=TEXT_DIM, dash=(2, 2))
        canvas.create_line(cx + body_r, dim_y - 5, cx + body_r, top_y, fill=TEXT_DIM, dash=(2, 2))
        canvas.create_text(cx, dim_y - 10, text=f"OD = \u2300{r['od']} mm",
                            fill=TEXT_DIM, font=("Consolas", 10), anchor="s")

        # Length dimension (left, vertical)
        dim_x = cx - body_r - 34
        canvas.create_line(dim_x, top_y, dim_x, bottom_y, fill=TEXT_DIM)
        canvas.create_line(dim_x - 5, top_y, cx - body_r, top_y, fill=TEXT_DIM, dash=(2, 2))
        canvas.create_line(dim_x - 5, bottom_y, cx - body_r, bottom_y, fill=TEXT_DIM, dash=(2, 2))
        canvas.create_text(dim_x - 10, (top_y + bottom_y) / 2, text=f"L = {r['length']} mm",
                            fill=TEXT_DIM, font=("Consolas", 10), angle=90, anchor="s")

        # spec panel on the right
        chip_x = min(cx + body_r + 60, w - 170)
        specs = [
            ("เกรด", duty["name"]),
            ("k", f"{r['k']:.1f} N/mm"),
            ("ยุบสูงสุด", f"{r['max_def']:.1f} mm"),
            ("จำนวนที่ใช้", f"{r['n']} ตัว"),
        ]
        for i, (k, v) in enumerate(specs):
            y = top_y + 10 + i * 34
            canvas.create_text(chip_x, y, text=k, fill=TEXT_DIM,
                                font=("Segoe UI", 8), anchor="w")
            canvas.create_text(chip_x, y + 15, text=v, fill=TEXT,
                                font=("Consolas", 11, "bold"), anchor="w")

        canvas.create_text(
            w / 2, h - 14,
            text=f"สปริง {duty['name']}  \u2300{r['od']} \u00d7 {r['length']} mm  "
                 f"(ภาพประกอบตามสัดส่วนโดยประมาณ ไม่ใช่ภาพถ่ายสินค้าจริง)",
            fill=TEXT_DIM, font=("Segoe UI", 8), anchor="s")


if __name__ == "__main__":
    app = SpringCalcApp()
    app.mainloop()
