from manim import *
import csv
from pathlib import Path
from manim import config

# Setting output resolution of the manim animation
config.pixel_width  = 2560
config.pixel_height = 1440
config.frame_rate   = 60

#activate env .\manim-env\Scripts\Activate.ps1
#render manim -pqh Warframe_Animations.py EnemyHealthAndDamage
#render clean manim -pqh Warframe_Tank_Table.py FramesTable --format=mov --transparent

## ---------- This is the animation for plotting the table of all my evaluated Health Tanks ----------#

CSV_PATH = Path("warframe_table.csv")
FONT_SIZE = 26
MAYBE_COLOR = ManimColor("#FFA500")

ICON = {
    "YES":   ("✓", GREEN),
    "NO":    ("✗", RED),
    "MAYBE": ("~", MAYBE_COLOR),
}

HEADERS = [
    "RANK", "FRAME", "EHP", "9999 Bombard One-Shot?",
    "Levelcap Viable?", "Eclipse Subsume", "Null Star Subsume", "TIER",
]

SAMPLE_ROWS = [
    ["1","Nidus","136,489,305","NO","YES","YES","NO","S"],
    ["2","Baruuk","108,918,187","NO","YES","YES","NO","S"],
    ["3","Trinity","27,269,862","NO","YES","YES","NO","S"],
    ["4","Mesa","21,081,600","NO","YES","YES","NO","A"],
    ["5","Gara","20,304,568","NO","YES","YES","NO","A"],
    ["6","Citrine","17,255,347","NO","YES","YES","NO","A"],
    ["7","Mirage","14,083,482","NO","YES","NO","YES","A"],
    ["8","Nova","13,697,080","NO","YES","YES","NO","A"],
    ["9","Ember","9,238,037","NO","MAYBE","YES","NO","B"],
    ["10","Nezha","8,680,272","NO","MAYBE","YES","NO","B+"],
    ["11","Oraxia","7,836,050","NO","YES (passive)","NO","YES","B+"],
    ["12","Titania","6,708,956","NO","MAYBE","YES","NO","B"],
    ["13","Chroma","5,994,231","NO","MAYBE","NO","YES","B"],
    ["14","Valkyr","5,474,560","NO","YES (passive)","YES","NO","A"],
    ["15","Grendel","5,271,091","NO","MAYBE","YES","NO","B"],
    ["16","Nekros","4,793,320","NO","MAYBE","YES","NO","B"],
    ["17","Atlas","4,466,280","NO","NO","YES","NO","C"],
    ["18","Qorvex","3,863,840","NO","NO","YES","NO","C"],
    ["19","Jade","3,724,588","NO","NO","YES","NO","C"],
    ["20","Hydroid","3,004,098","NO","NO","YES","NO","D"],
    ["21","Equinox","2,587,601","NO","NO","YES","NO","D"],
    ["22","Inaros","2,068,199","NO","NO","YES","NO","D"],
    ["23","Oberon","993,042","YES","NO","YES","NO","F"],
]

def load_rows():
    if CSV_PATH.exists():
        rows = []
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            rdr = csv.reader(f)
            first = next(rdr)
            is_header = len(first) == len(HEADERS) and any(s.upper()=="RANK" for s in first)
            if not is_header:
                rows.append(first)
            rows.extend(rdr)
        return rows
    return SAMPLE_ROWS

def convert_symbol(text: str):
    raw = text.strip()
    upper = raw.upper()
    for key, (glyph, color) in ICON.items():
        if upper == key or upper.startswith(key + " "):  # exact match or key + suffix
            suffix = raw[len(key):] if len(raw) > len(key) else ""
            return glyph, color, suffix
    return raw, WHITE, ""

class FramesTable(Scene):
    def construct(self):
        title = Text("Warframe Health Tank Rankings", weight=BOLD).to_edge(UP)
        self.play(FadeIn(title, shift=UP, run_time=0.6))

        rows = load_rows()

        # Preprocess rows into symbols
        processed = []
        for row in rows:
            new_row = []
            for cell in row:
                glyph, color, suffix = convert_symbol(cell)
                if glyph in ("✓","✗","~"):
                    icon = Text(glyph, font_size=FONT_SIZE, color=color)
                    if suffix.strip():
                        extra = Text(suffix, font_size=int(FONT_SIZE*0.85), color=GRAY_B)\
                            .next_to(icon, RIGHT, buff=0.15, aligned_edge=DOWN)
                        new_row.append(VGroup(icon, extra))
                    else:
                        new_row.append(icon)
                else:
                    new_row.append(str(cell))
            processed.append(new_row)

        table = Table(
            [HEADERS] + processed,
            include_outer_lines=True,
            element_to_mobject=lambda s: Text(str(s), font_size=FONT_SIZE) if isinstance(s,str) else s,
            h_buff=0.6,
            v_buff=0.28,
            arrange_in_grid_config={"col_alignments":"lccccccc"},
        )
        
        table.scale_to_fit_width(config.frame_width - 2)   
        table.scale_to_fit_height(config.frame_height - 2)  
        table.next_to(title, DOWN, buff=0.2)

        # Draw table
        self.play(Create(table.get_horizontal_lines()), Create(table.get_vertical_lines()), run_time=0.8)

        # Labels
        labels = list(table.get_labels().submobjects)
        if labels:
            self.play(LaggedStart(*[FadeIn(m, scale=0.95) for m in labels],
                                  lag_ratio=0.06, run_time=1))

        # Entries
        entries = list(table.get_entries_without_labels().submobjects)
        if entries:
            self.play(LaggedStart(*[FadeIn(m, scale=0.98) for m in entries],
                                  lag_ratio=0.008, run_time=1.5))

        legend = VGroup(
            Text("Legend:", font_size=24, weight=BOLD),
            Text("✓  = YES", font_size=22, color=GREEN),
            Text("✗  = NO", font_size=22, color=RED),
            Text("~  = MAYBE", font_size=22, color=ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).scale(0.9)
        legend.to_edge(DOWN+LEFT).shift(RIGHT*0.3+UP*0.2)

        self.play(FadeIn(legend, shift=UP, run_time=1))
        self.wait(1)
