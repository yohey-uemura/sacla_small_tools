#!/usr/bin/env python3
"""
SACLA BL3 Custom Scan Parameter Editor.
Originally composed by Yohei Uemura and modified by Gemini.
"""
import math
import os
import re
import tkinter as tk
from tkinter import messagebox, ttk

# SACLA BL3 Monochromator & Delay Stage Constants
HC_KEV_A = 12.3984                  # h*c [keV * Angstrom]
TWO_D_SI111 = 6.270832              # 2 * d_Si(111) [Angstrom]
E_MIN_SI111_EV = (HC_KEV_A / TWO_D_SI111) * 1000.0  # ~1977.15 eV Bragg cutoff
CC_PULSES_PER_DEG = 250000.0        # 10^6 / 4 pulses per degree[span_11](start_span)[span_11](end_span)
DELAY_PULSES_PER_PS = 150.0         # bl3_st2_pm001 conversion [pls/ps][span_12](start_span)[span_12](end_span)
CHANNEL_CUT_GAP_M = 0.008           # 8 mm channel-cut gap [m][span_13](start_span)[span_13](end_span)
SPEED_OF_LIGHT = 299792458.0        # [m/s][span_14](start_span)[span_14](end_span)

BOX_WIDTH = 58

# X-ray Absorption Edge Energies [eV] from reference tables (Z = 15..92)[span_15](start_span)[span_15](end_span)[span_16](start_span)[span_16](end_span)[span_17](start_span)[span_17](end_span)[span_18](start_span)[span_18](end_span)[span_19](start_span)[span_19](end_span)[span_20](start_span)[span_20](end_span)[span_21](start_span)[span_21](end_span)
XRAY_EDGES: dict[str, dict[str, float]] = {
    "P":  {"K": 2143.5},
    "S":  {"K": 2470.5},
    "Cl": {"K": 2819.6},
    "Ar": {"K": 3202.9},
    "K":  {"K": 3607.8},
    "Ca": {"K": 4038.1},
    "Sc": {"K": 4489.0},
    "Ti": {"K": 4964.5},
    "V":  {"K": 5463.9},
    "Cr": {"K": 5988.8},
    "Mn": {"K": 6537.6},
    "Fe": {"K": 7111.2},
    "Co": {"K": 7709.5},
    "Ni": {"K": 8331.7},
    "Cu": {"K": 8980.3},
    "Zn": {"K": 9660.7},
    "Ga": {"K": 10368.2},
    "Ge": {"K": 11103.6},
    "As": {"K": 11865.0},
    "Se": {"K": 12654.5},
    "Br": {"K": 13470.0},
    "Kr": {"K": 14324.4},
    "Rb": {"K": 15202.3},
    "Sr": {"K": 16107.0},
    "Y":  {"K": 17038.0},
    "Zr": {"K": 17998.9},
    "Nb": {"K": 18986.9, "LI": 2710.0},
    "Mo": {"K": 20003.9, "LIII": 2523.4, "LII": 2627.4, "LI": 2881.0},
    "Tc": {"K": 21047.3, "LIII": 2678.0, "LII": 2794.8, "LI": 3055.0},
    "Ru": {"K": 22119.3, "LIII": 2837.7, "LII": 2966.3, "LI": 3233.0},
    "Rh": {"K": 23219.8, "LIII": 3002.1, "LII": 3144.8, "LI": 3417.0},
    "Pd": {"K": 23348.0, "LIII": 3173.0, "LII": 3330.3, "LI": 3607.0},
    "Ag": {"K": 25516.5, "LIII": 3351.0, "LII": 3525.8, "LI": 3807.2},
    "Cd": {"K": 26715.9, "LIII": 3537.6, "LII": 3728.0, "LI": 4019.0},
    "In": {"K": 27942.0, "LIII": 3730.2, "LII": 3939.3, "LI": 4237.3},
    "Sn": {"K": 29194.7, "LIII": 3928.8, "LII": 4157.3, "LI": 4464.8},
    "Sb": {"K": 30486.0, "LIII": 4132.3, "LII": 4381.9, "LI": 4698.4},
    "Te": {"K": 31811.4, "LIII": 4341.8, "LII": 4612.6, "LI": 4939.7},
    "I":  {"K": 33166.5, "LIII": 4558.7, "LII": 4854.0, "LI": 5192.0},
    "Xe": {"K": 34590.0, "LIII": 4782.2, "LII": 5103.7, "LI": 5452.8},
    "Cs": {"K": 35987.0, "LIII": 5011.3, "LII": 5358.1, "LI": 5721.0},
    "Ba": {"K": 37452.0, "LIII": 5247.0, "LII": 5623.3, "LI": 5996.0},
    "La": {"K": 38934.0, "LIII": 5484.0, "LII": 5889.0, "LI": 6268.0},
    "Ce": {"K": 40453.0, "LIII": 5723.0, "LII": 6161.0, "LI": 6548.0},
    "Pr": {"LIII": 5963.0,  "LII": 6439.0,  "LI": 6834.0},
    "Nd": {"LIII": 6209.2,  "LII": 6723.4,  "LI": 7129.4},
    "Pm": {"LIII": 6460.5,  "LII": 7014.0,  "LI": 7436.0},
    "Sm": {"LIII": 6717.2,  "LII": 7313.2,  "LI": 7747.8},
    "Eu": {"LIII": 6980.6,  "LII": 7619.9,  "LI": 8060.7},
    "Gd": {"LIII": 7243.0,  "LII": 7931.0,  "LI": 8386.4},
    "Tb": {"LIII": 7515.3,  "LII": 8252.7,  "LI": 8716.7},
    "Dy": {"LIII": 7789.7,  "LII": 8583.0,  "LI": 9054.8},
    "Ho": {"LIII": 8067.6,  "LII": 8916.4,  "LI": 9399.4},
    "Er": {"LIII": 8357.5,  "LII": 9262.2,  "LI": 9757.4},
    "Tm": {"LIII": 8649.6,  "LII": 9617.1,  "LI": 10120.6},
    "Yb": {"LIII": 8944.1,  "LII": 9976.1,  "LI": 10490.1},
    "Lu": {"LIII": 9249.0,  "LII": 10344.8, "LI": 10874.0},
    "Hf": {"LIII": 9557.7,  "LII": 10736.2, "LI": 11274.0},
    "Ta": {"LIII": 9876.6,  "LII": 11132.0, "LI": 11682.0},
    "W":  {"LIII": 10199.9, "LII": 11538.0, "LI": 12099.6},
    "Re": {"LIII": 10530.6, "LII": 11954.0, "LI": 12530.0},
    "Os": {"LIII": 10868.3, "LII": 12381.0, "LI": 12972.0},
    "Ir": {"LIII": 11212.0, "LII": 12820.0, "LI": 13423.0},
    "Pt": {"LIII": 11562.0, "LII": 13272.3, "LI": 13883.0},
    "Au": {"LIII": 11921.2, "LII": 13736.1, "LI": 14353.7},
    "Hg": {"LIII": 12286.0, "LII": 14215.0, "LI": 14842.0},
    "Tl": {"LIII": 12660.0, "LII": 14699.0, "LI": 15353.0},
    "Pb": {"LIII": 13040.6, "LII": 15205.3, "LI": 15855.0},
    "Bi": {"LIII": 13426.0, "LII": 15719.0, "LI": 16376.0},
    "Ra": {"LIII": 15444.0, "LII": 18486.0, "LI": 19236.0},
    "Th": {"LIII": 16299.0, "LII": 19683.0, "LI": 20464.0},
    "U":  {"LIII": 17165.0, "LII": 20945.0, "LI": 21771.0},
}

# Standard Periodic Table layout: (Z, Symbol, grid_row, grid_col)
PERIODIC_TABLE_LAYOUT: list[tuple[int, str, int, int]] = [
    # Period 1
    (1, "H", 0, 0), (2, "He", 0, 17),
    # Period 2
    (3, "Li", 1, 0), (4, "Be", 1, 1),
    (5, "B", 1, 12), (6, "C", 1, 13), (7, "N", 1, 14), (8, "O", 1, 15), (9, "F", 1, 16), (10, "Ne", 1, 17),
    # Period 3
    (11, "Na", 2, 0), (12, "Mg", 2, 1),
    (13, "Al", 2, 12), (14, "Si", 2, 13), (15, "P", 2, 14), (16, "S", 2, 15), (17, "Cl", 2, 16), (18, "Ar", 2, 17),
    # Period 4
    (19, "K", 3, 0), (20, "Ca", 3, 1), (21, "Sc", 3, 2), (22, "Ti", 3, 3), (23, "V", 3, 4), (24, "Cr", 3, 5),
    (25, "Mn", 3, 6), (26, "Fe", 3, 7), (27, "Co", 3, 8), (28, "Ni", 3, 9), (29, "Cu", 3, 10), (30, "Zn", 3, 11),
    (31, "Ga", 3, 12), (32, "Ge", 3, 13), (33, "As", 3, 14), (34, "Se", 3, 15), (35, "Br", 3, 16), (36, "Kr", 3, 17),
    # Period 5
    (37, "Rb", 4, 0), (38, "Sr", 4, 1), (39, "Y", 4, 2), (40, "Zr", 4, 3), (41, "Nb", 4, 4), (42, "Mo", 4, 5),
    (43, "Tc", 4, 6), (44, "Ru", 4, 7), (45, "Rh", 4, 8), (46, "Pd", 4, 9), (47, "Ag", 4, 10), (48, "Cd", 4, 11),
    (49, "In", 4, 12), (50, "Sn", 4, 13), (51, "Sb", 4, 14), (52, "Te", 4, 15), (53, "I", 4, 16), (54, "Xe", 4, 17),
    # Period 6
    (55, "Cs", 5, 0), (56, "Ba", 5, 1),
    (72, "Hf", 5, 3), (73, "Ta", 5, 4), (74, "W", 5, 5), (75, "Re", 5, 6), (76, "Os", 5, 7), (77, "Ir", 5, 8),
    (78, "Pt", 5, 9), (79, "Au", 5, 10), (80, "Hg", 5, 11), (81, "Tl", 5, 12), (82, "Pb", 5, 13), (83, "Bi", 5, 14),
    (84, "Po", 5, 15), (85, "At", 5, 16), (86, "Rn", 5, 17),
    # Period 7
    (87, "Fr", 6, 0), (88, "Ra", 6, 1),
    (104, "Rf", 6, 3), (105, "Db", 6, 4), (106, "Sg", 6, 5), (107, "Bh", 6, 6), (108, "Hs", 6, 7), (109, "Mt", 6, 8),
    (110, "Ds", 6, 9), (111, "Rg", 6, 10), (112, "Cn", 6, 11), (113, "Nh", 6, 12), (114, "Fl", 6, 13), (115, "Mc", 6, 14),
    (116, "Lv", 6, 15), (117, "Ts", 6, 16), (118, "Og", 6, 17),
    # Lanthanides (row 8)
    (57, "La", 8, 2), (58, "Ce", 8, 3), (59, "Pr", 8, 4), (60, "Nd", 8, 5), (61, "Pm", 8, 6), (62, "Sm", 8, 7),
    (63, "Eu", 8, 8), (64, "Gd", 8, 9), (65, "Tb", 8, 10), (66, "Dy", 8, 11), (67, "Ho", 8, 12), (68, "Er", 8, 13),
    (69, "Tm", 8, 14), (70, "Yb", 8, 15), (71, "Lu", 8, 16),
    # Actinides (row 9)
    (89, "Ac", 9, 2), (90, "Th", 9, 3), (91, "Pa", 9, 4), (92, "U", 9, 5), (93, "Np", 9, 6), (94, "Pu", 9, 7),
    (95, "Am", 9, 8), (96, "Cm", 9, 9), (97, "Bk", 9, 10), (98, "Cf", 9, 11), (99, "Es", 9, 12), (100, "Fm", 9, 13),
    (101, "Md", 9, 14), (102, "No", 9, 15), (103, "Lr", 9, 16),
]

SYMBOL_TO_Z: dict[str, int] = {sym: z for z, sym, _, _ in PERIODIC_TABLE_LAYOUT}


class PeriodicTableDialog(tk.Toplevel):
    """Interactive Periodic Table popup for Tkinter."""

    def __init__(self, parent: tk.Misc, current_symbol: str = "Fe"):
        super().__init__(parent)
        self.title("Select Element for E0")
        self.resizable(False, False)
        self.selected_symbol: str | None = None

        grid = tk.Frame(self, padx=8, pady=8)
        grid.pack()

        # Spacer row between main periods and Lanthanides/Actinides
        grid.grid_rowconfigure(7, minsize=10)

        for row, label in ((5, "57-71"), (6, "89-103")):
            lbl = tk.Label(
                grid, text=label, width=5, height=2,
                fg="#666666", font=("Arial", 9), relief=tk.GROOVE, bd=1
            )
            lbl.grid(row=row, column=2, padx=1, pady=1)

        for z, sym, row, col in PERIODIC_TABLE_LAYOUT:
            edges = XRAY_EDGES.get(sym, {})
            if not edges:
                lbl = tk.Label(
                    grid, text=f"{z}\n{sym}", width=5, height=2,
                    bg="#ececec", fg="#999999", font=("Arial", 9), relief=tk.FLAT, bd=1
                )
                lbl.grid(row=row, column=col, padx=1, pady=1)
            else:
                has_k = "K" in edges
                has_l = any(k.startswith("L") for k in edges)
                if has_k and has_l:
                    bg = "#cdeee6"
                elif has_k:
                    bg = "#d4e8fc"
                else:
                    bg = "#fce8c8"

                is_curr = sym == current_symbol
                # Use Label with click binding so background colors render natively on macOS Aqua
                tile = tk.Label(
                    grid,
                    text=f"{z}\n{sym}",
                    width=5,
                    height=2,
                    bg="#fff59d" if is_curr else bg,
                    fg="#111111",
                    font=("Arial", 9, "bold" if is_curr else "normal"),
                    relief=tk.SOLID if is_curr else tk.RAISED,
                    bd=2 if is_curr else 1,
                    cursor="hand2",
                )
                tile.grid(row=row, column=col, padx=1, pady=1)
                tile.bind("<Button-1>", lambda _, s=sym: self._choose(s))
                tile.bind("<Enter>", lambda _, w=tile: w.configure(bg="#fff59d"))
                tile.bind(
                    "<Leave>",
                    lambda _, w=tile, orig=("#fff59d" if is_curr else bg): w.configure(bg=orig),
                )

        # Color legend
        legend = tk.Frame(self, padx=8, pady=6)
        legend.pack(fill=tk.X)
        for color, text in (
            ("#d4e8fc", "K-edge"),
            ("#cdeee6", "K + L-edges"),
            ("#fce8c8", "L-edges"),
            ("#ececec", "Not in table"),
        ):
            tk.Label(
                legend, text=f" {text} ", bg=color, fg="#111111",
                font=("Arial", 10), relief=tk.SOLID, bd=1
            ).pack(side=tk.LEFT, padx=(0, 8))

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _choose(self, symbol: str):
        self.selected_symbol = symbol
        self.destroy()


def calc_cc_pulses(energy_ev: float) -> int:
    """Convert photon energy [eV] to SACLA BL3 channel-cut motor pulses."""
    if energy_ev <= E_MIN_SI111_EV:
        raise ValueError(f"Energy {energy_ev:.2f} eV must exceed Si(111) cutoff ({E_MIN_SI111_EV:.2f} eV).")
    sin_theta = (HC_KEV_A * 1000.0) / (TWO_D_SI111 * energy_ev)
    theta_deg = math.degrees(math.asin(sin_theta))
    return round(theta_deg * CC_PULSES_PER_DEG)


def calc_delay_compensation_pulses(energy_ev: float, e0_ev: float, t0_pls: int) -> int:
    """Calculate optical delay stage pulses needed to compensate channel-cut path length."""
    if energy_ev <= E_MIN_SI111_EV or e0_ev <= E_MIN_SI111_EV:
        raise ValueError(f"Both E ({energy_ev:.2f} eV) and E0 ({e0_ev:.2f} eV) must exceed {E_MIN_SI111_EV:.2f} eV.")
    sin_theta = (HC_KEV_A * 1000.0) / (TWO_D_SI111 * energy_ev)
    sin_theta_0 = (HC_KEV_A * 1000.0) / (TWO_D_SI111 * e0_ev)
    path_diff_m = 4.0 * CHANNEL_CUT_GAP_M * (sin_theta - sin_theta_0)
    delay_fs = round((path_diff_m / SPEED_OF_LIGHT) * 1e15, 1)
    return -int(delay_fs / 1000.0 * DELAY_PULSES_PER_PS) + t0_pls


def generate_segment(start: float, end: float, step: float, dupl: int, include_end: bool = False) -> list[float]:
    """Generate evenly spaced points with duplication without cumulative float drift."""
    if step == 0:
        raise ValueError(f"Step size cannot be zero ({start}, {end}, {step}, {dupl}).")
    if dupl < 1:
        raise ValueError(f"Duplication count must be >= 1 (got {dupl}).")
    if (end > start and step < 0) or (end < start and step > 0):
        raise ValueError(f"Step sign ({step}) does not move from {start} to {end}.")

    n_steps = int(math.floor(((end - start) / step) + 1e-9))
    base_pts = [round(start + step * i, 8) for i in range(n_steps)]

    if include_end:
        last_val = round(start + step * n_steps, 8)
        if abs(last_val - end) <= 1e-7 or not base_pts or abs(base_pts[-1] - end) > 1e-7:
            base_pts.append(round(end, 8))

    expanded: list[float] = []
    for pt in base_pts:
        expanded.extend([pt] * dupl)
    return expanded


class SaclaScanEditor:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SACLA BL3 Custom Scan Parameter Editor")
        self.mode = tk.StringVar(value="Eng")
        self.current_symbol = "Fe"
        self.edge_var = tk.StringVar(value="K")

        # Top control bar: mode selector
        top_bar = tk.Frame(root, pady=6)
        top_bar.pack(side=tk.TOP, fill=tk.X, padx=10)

        for label, val in (
            ("Energy", "Eng"),
            ("Energy with delay", "Eng_with_D"),
            ("Delay", "Dly"),
        ):
            tk.Radiobutton(
                top_bar, text=label, value=val, font=("Arial", 13),
                variable=self.mode, command=self._on_mode_changed
            ).pack(side=tk.LEFT, padx=(0, 10))

        # Second bar: Periodic Table button & Edge selector
        elem_bar = tk.Frame(root, pady=4)
        elem_bar.pack(side=tk.TOP, fill=tk.X, padx=10)

        tk.Label(elem_bar, text="Element:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.btn_ptable = ttk.Button(
            elem_bar, text="Fe (Z=26)...", command=self._open_periodic_table
        )
        self.btn_ptable.pack(side=tk.LEFT, padx=(4, 10))

        tk.Label(elem_bar, text="Edge:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.cb_edge = ttk.Combobox(
            elem_bar, textvariable=self.edge_var,
            values=["K"], width=6, state="readonly", font=("Arial", 12)
        )
        self.cb_edge.pack(side=tk.LEFT, padx=(4, 10))
        self.cb_edge.bind("<<ComboboxSelected>>", self._on_edge_selected)

        self.e0_label_var = tk.StringVar(value="E0 = 7111.2 eV")
        tk.Label(elem_bar, textvariable=self.e0_label_var, font=("Arial", 12, "bold"), fg="#1565c0").pack(
            side=tk.LEFT, padx=(4, 0)
        )

        # Input text editor
        self.input_text = tk.Text(root, font=("Monaco", 14), width=64, height=16)
        self.input_text.pack(padx=10, pady=(4, 6), fill=tk.BOTH, expand=True)

        # Action button directly above Output Preview
        style = ttk.Style(root)
        style.configure("Action.TButton", font=("Arial", 13, "bold"), padding=(16, 6))
        self.btn_make = ttk.Button(
            root, text="Make the parameters", style="Action.TButton", command=self.make_params
        )
        self.btn_make.pack(pady=(2, 6))

        # Output preview
        tk.Label(root, text=">>>>>> Output Preview <<<<<<", font=("Arial", 13, "bold")).pack()
        self.output_text = tk.Text(root, font=("Monaco", 14), width=64, height=18)
        self.output_text.pack(padx=10, pady=(2, 6), fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value=f"Working directory: {os.getcwd()}")
        tk.Label(root, textvariable=self.status_var, font=("Arial", 11), anchor="w", fg="#333333").pack(
            side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 6)
        )

        self._select_element("Fe")

    def _on_mode_changed(self):
        is_energy = self.mode.get() in ("Eng", "Eng_with_D")
        self.btn_ptable.configure(state="normal" if is_energy else "disabled")
        self.cb_edge.configure(state="readonly" if is_energy else "disabled")
        self.insert_template()

    def _open_periodic_table(self):
        dlg = PeriodicTableDialog(self.root, current_symbol=self.current_symbol)
        if dlg.selected_symbol:
            self._select_element(dlg.selected_symbol)

    def _select_element(self, symbol: str):
        edges = XRAY_EDGES.get(symbol, {})
        if not edges:
            return
        self.current_symbol = symbol
        z = SYMBOL_TO_Z.get(symbol, 0)
        self.btn_ptable.configure(text=f"{symbol} (Z={z})...")

        edge_list = list(edges.keys())
        self.cb_edge.configure(values=edge_list)
        default_edge = "K" if "K" in edges else ("LIII" if "LIII" in edges else edge_list[0])
        self.edge_var.set(default_edge)
        self._on_edge_selected()

    def _on_edge_selected(self, *_):
        edge = self.edge_var.get()
        e0 = XRAY_EDGES.get(self.current_symbol, {}).get(edge)
        if e0 is not None:
            self.e0_label_var.set(f"E0 = {e0:.1f} eV")
            if self.mode.get() == "Dly":
                self.mode.set("Eng")
                self.btn_ptable.configure(state="normal")
                self.cb_edge.configure(state="readonly")
            self.insert_template()

    def _format_header(self, title: str, lines: list[str]) -> str:
        border = "#" * (BOX_WIDTH + 2)
        out = [
            border,
            f"#{'how to write: start, end, step, duplication':^{BOX_WIDTH}}#",
            f"#{title:^{BOX_WIDTH}}#",
        ]
        for ln in lines:
            out.append(f"#{' ' * 6}{ln:<{BOX_WIDTH - 6}}#")
        out.append(border)
        return "\n".join(out) + "\n"

    def insert_template(self):
        self.input_text.delete("1.0", tk.END)
        mode = self.mode.get()

        sym = self.current_symbol
        z = SYMBOL_TO_Z.get(sym, 0)
        edge = self.edge_var.get()
        e0 = XRAY_EDGES.get(sym, {}).get(edge, 7111.2)
        sym_lower = sym.lower()
        edge_lower = edge.lower()

        e_pre_start = round(e0 - 20.0, 1)
        e_edge_start = round(e0 - 7.0, 1)
        e_edge_end = round(e0 + 8.0, 1)
        e_post_end = round(e0 + 45.0, 1)

        if mode == "Eng":
            header = self._format_header(
                f"<Energy scan in eV ({sym} (Z={z}) {edge}-edge)>",
                [
                    "7110, 7160, 1, 1  <= start, end, step, dupl.",
                    "out=fe_k_xanes    <= output file name",
                ],
            )
            body = (
                f"{e_pre_start}, {e_edge_start}, 1, 1\n"
                f"{e_edge_start}, {e_edge_end}, 0.5, 1\n"
                f"{e_edge_end}, {e_post_end}, 1, 1\n"
                f"out={sym_lower}_{edge_lower}_xanes\n"
            )
        elif mode == "Dly":
            header = self._format_header(
                "<Example (for delay in ps)>",
                [
                    "t0 = 100          <= reference offset (in pls)",
                    "-5, -1, 1, 1      <= start, end, step, dupl.",
                    "-1, 1, 0.1, 1",
                    "1, 5, 1, 1",
                    "out=fe_delay      <= output file name",
                ],
            )
            body = (
                "t0 = 0\n"
                "-5, -1, 1, 1\n"
                "-1, 1, 0.1, 1\n"
                "1, 5, 1, 1\n"
                "out=test_delay\n"
            )
        else:
            header = self._format_header(
                f"<Energy with delay ({sym} (Z={z}) {edge}-edge)>",
                [
                    f"E0 = {e0:.1f}       <= reference energy (in eV)",
                    "t0 = 0            <= reference offset (in pls)",
                    "7110, 7160, 1, 1  <= start, end, step, dupl.",
                    "out=fe_k_xanes_wth_delay",
                ],
            )
            body = (
                f"E0 = {e0:.1f}\n"
                "t0 = 0\n"
                f"{e_pre_start}, {e_edge_start}, 1, 1\n"
                f"{e_edge_start}, {e_edge_end}, 0.5, 1\n"
                f"{e_edge_end}, {e_post_end}, 1, 1\n"
                f"out={sym_lower}_{edge_lower}_xanes_wth_delay\n"
            )
        self.input_text.insert(tk.END, header + body)

    def make_params(self):
        self.output_text.delete("1.0", tk.END)
        mode = self.mode.get()
        raw_lines = self.input_text.get("1.0", tk.END).splitlines()

        filename = "params.csv"
        t0 = 0
        e0: float | None = None
        segments: list[tuple[float, float, float, int]] = []

        try:
            for line_no, raw in enumerate(raw_lines, start=1):
                line = raw.split("#", 1)[0].strip()
                if not line:
                    continue

                e0_match = re.match(r"^E0\s*=\s*([+-]?\d+(?:\.\d+)?)$", line)
                if e0_match:
                    if mode != "Eng_with_D":
                        raise ValueError(f"Line {line_no}: 'E0' is only used in 'Energy with delay' mode.")
                    e0 = float(e0_match.group(1))
                    continue

                t0_match = re.match(r"^t0\s*=\s*([+-]?\d+(?:\.\d+)?)$", line)
                if t0_match:
                    if mode == "Eng":
                        raise ValueError(f"Line {line_no}: 't0' is not used in Energy-only mode.")
                    t0 = round(float(t0_match.group(1)))
                    continue

                out_match = re.match(r"^out\s*=\s*(.+)$", line)
                if out_match:
                    filename = out_match.group(1).strip()
                    if not filename:
                        raise ValueError(f"Line {line_no}: Output filename cannot be empty.")
                    continue

                parts = [p.strip() for p in line.split(",")]
                if len(parts) == 4:
                    try:
                        start, end, step = map(float, parts[:3])
                        dupl_f = float(parts[3])
                        if not dupl_f.is_integer():
                            raise ValueError(f"Line {line_no}: Duplication '{parts[3]}' must be an integer.")
                        segments.append((start, end, step, int(dupl_f)))
                    except ValueError as exc:
                        raise ValueError(f"Line {line_no}: Invalid segment '{line}' ({exc}).") from exc
                else:
                    raise ValueError(
                        f"Line {line_no}: Unrecognized syntax '{line}'. "
                        "Expected 'start, end, step, dupl', 'E0 = <val>', 't0 = <val>', or 'out=<name>'."
                    )

            if not segments:
                raise ValueError("No scan segments found.")
            if mode == "Eng_with_D" and (e0 is None or e0 <= 0):
                raise ValueError("Please specify a valid 'E0 = <energy_eV>' line for 'Energy with delay' mode.")

            params: list[float] = []
            for idx, (start, end, step, dupl) in enumerate(segments):
                is_last = idx == len(segments) - 1
                seg_pts = generate_segment(start, end, step, dupl, include_end=is_last)
                if params and seg_pts and abs(params[-1] - seg_pts[0]) <= 1e-7:
                    seg_pts = seg_pts[dupl:]
                params.extend(seg_pts)

            if not filename.endswith(".csv"):
                filename += ".csv"
            out_path = os.path.abspath(filename)

            csv_lines: list[str] = []
            preview_lines: list[str] = []

            if mode == "Eng":
                csv_header = "bl3_st1_pm003,\tbl3_st1_pm005"
                preview_lines.append("#Eng(eV), CCpos, CCneg")
                for e in params:
                    cc = calc_cc_pulses(e)
                    csv_lines.append(f"{cc:d}, {-cc:d}")
                    preview_lines.append(f"{e:.2f}, {cc:d}, {-cc:d}")

            elif mode == "Dly":
                csv_header = "bl3_st2_pm001"
                preview_lines.append("DELAY(ps), MOTOR(pls)")
                for d_ps in params:
                    motor_pls = int(round(d_ps * DELAY_PULSES_PER_PS)) + t0
                    csv_lines.append(f"{motor_pls:d}")
                    preview_lines.append(f"{d_ps:.2f}, {motor_pls:d}")

            else:
                csv_header = "bl3_st1_pm003,\tbl3_st1_pm005,\tbl3_st2_pm001"
                preview_lines.append("#Eng(eV), CCpos, CCneg, delay(pls)")
                for e in params:
                    cc = calc_cc_pulses(e)
                    delay_pls = calc_delay_compensation_pulses(e, e0, t0)
                    csv_lines.append(f"{cc:d}, {-cc:d}, {delay_pls:d}")
                    preview_lines.append(f"{e:.2f}, {cc:d}, {-cc:d}, {delay_pls:d}")

            with open(out_path, "w", encoding="utf-8") as fout:
                fout.write(csv_header + "\n")
                fout.write("\n".join(csv_lines) + "\n")

            self.output_text.insert(tk.END, "\n".join(preview_lines) + "\n")
            self.status_var.set(f"Saved {len(csv_lines)} points -> {out_path}")

        except Exception as err:
            messagebox.showerror("Parameter Error", str(err))
            self.status_var.set(f"Error: {err}")


if __name__ == "__main__":
    mw = tk.Tk()
    app = SaclaScanEditor(mw)
    mw.mainloop()
