from manim import *
import numpy as np
import math

# Setting output resolution of the manim animation
config.pixel_width  = 2560
config.pixel_height = 1440 
config.frame_rate   = 60  

#activate env .\manim-env\Scripts\Activate.ps1
#render manim -pqh Warframe_Animations.py EnemyHealthAndDamage
#render clean manim -pqh Warframe_Animations.py WarframeDamageScalingOraxia --format=mov --transparent

## ---------- This is the animation for plotting the intersection between enemy damage and Warframe EHP ----------#

class EnemyHealthAndDamage(Scene):
    def construct(self):
        # Config
        base_level = 100
        x_min = 100
        x_max = 2000
        step = 100

        # Modifiers (example values)
        leech = 0.25
        strength = 2.0
        viral = 3.25
        ability_damage = 0
        vulnerability = 0

        # f1 and f2 definitions
        def f1(x):
            return (1 + 0.015 * (x - base_level))**2

        def f2(x):
            return (1 + (24 * np.sqrt(5) / 5) * ((x - base_level) ** 0.5))

        def s1(x):
            if x <= 50:
                return 0
            elif x >= 100:
                return 1
            else:
                t = (x - 50) / 50
                return 3 * t**2 - 2 * t**3

        def health_multiplier(x):
            if x <= 15:
                return f1(x)
            elif x <= 25:
                return (1 + 0.025 * (x - 15)) * f1(x)
            elif x <= 35:
                return (1.25 + 0.125 * (x - 25)) * f1(x)
            elif x <= 50:
                return (2.5 + 2/15 * (x - 35)) * f1(x)
            elif x <= 100:
                blend = (1 - s1(x)) * f1(x) + s1(x) * f2(x)
                return (4.5 + 0.03 * (x - 50)) * blend
            else:
                return 6 * f2(x)

        def damage(x):
            hp = health_multiplier(x)
            return hp * (
                (leech * (1 + strength)) *
                (1 + viral) *
                (1 + ability_damage) *
                (1 + vulnerability * (1 + strength))
            )

        # Data
        levels = np.arange(x_min, x_max + 1, step)
        hp_vals = [health_multiplier(x) for x in levels]
        dmg_vals = [damage(x) for x in levels]

        # Axes with labels

        axes = Axes(
         x_range=[x_min, x_max, 500],                    # x_min = 100, x_max = 2000
          y_range=[0, max(dmg_vals) * 1.2],               # scale y to fit highest damage value
          x_length=10,
          y_length=6,
          axis_config={"include_ticks": False, "include_numbers": False},
          x_axis_config={"stroke_width": 6},
          y_axis_config={"stroke_width": 6},
        ).to_edge(DOWN)

        self.play(Create(axes), run_time=2)

        x_label = Text("Enemy Level", font_size=24)
        y_label = Text("Value", font_size=24)

        x_label.next_to(axes.x_axis, DOWN, buff=0.1)
        y_label.next_to(axes.y_axis, LEFT, buff=0.2)

        self.play((Write(x_label), Write(y_label)), run_time=1)

        # Plot lines
        hp_graph = axes.plot_line_graph(levels, hp_vals, add_vertex_dots=False, line_color=RED, stroke_width=6)
        dmg_graph = axes.plot_line_graph(levels, dmg_vals, add_vertex_dots=False, line_color=BLUE, stroke_width=6)

        # Label positions near the end of each line
        hp_label_point = axes.coords_to_point(levels[-1], hp_vals[-1])
        dmg_label_point = axes.coords_to_point(levels[-1], dmg_vals[-1])

        hp_label = Text("Enemy Health", color=RED).scale(0.4).next_to(hp_label_point, RIGHT, buff=0.1)
        dmg_label = Text("Damage Output", color=BLUE).scale(0.4).next_to(dmg_label_point, RIGHT, buff=0.1)

        # Animate
        self.play(Create(hp_graph), FadeIn(hp_label), run_time=2)
        self.wait(0.2)
        self.play(Create(dmg_graph), FadeIn(dmg_label), run_time=2)
        self.wait(2)

# ===================== CONFIG: =====================
# P and K are constants that you can find on the Warframe wiki, here K is the exponent
K_WIKI = 0.015
P_WIKI = 1.55

# Bombard parameters
BOMBARD_BASE_DAMAGE = 65    # In game testing at level 1 against overguard
BOMBARD_BASE_LEVEL  = 4     # Found on wiki or via ingame testing with Trinity's EV
BOMBARD_K = 0.015
BOMBARD_P = 1.55

# Heavy Gunner parameters
HEAVY_BASE_DAMAGE = 8       # See bombard above
HEAVY_BASE_LEVEL  = 8       # See bombard above
HEAVY_K = 0.015
HEAVY_P = 1.55

# Enter your frame's EHP in the line below
TARGET_DAMAGE = 7836050

# ================================================================================

def damage_multiplier(L, base_level, K, P):
    return 1 + K * (L - base_level) ** P

def damage(L, base_damage, base_level, K, P):
    return base_damage * damage_multiplier(L, base_level, K, P)

def solve_level_for_damage(target_damage, base_damage, base_level, K, P):
    """Closed-form inversion for target = BD * (1 + K * (L - L0)^P)."""
    rhs = (target_damage / base_damage - 1.0) / K
    if rhs <= 0:
        return base_level
    return base_level + rhs ** (1.0 / P)

def nice_number(x):
    if x >= 1_000_000:
        return f"{x/1_000_000:.3g}M"
    if x >= 1_000:
        return f"{x/1_000:.3g}k"
    return f"{x:g}"

class WarframeDamageScalingOraxia(Scene):
    def construct(self):
        cL, cBase, cMul, cDmg, cConst = YELLOW, BLUE, GREEN, RED, PURPLE

        # ---------- Titles ----------
        title_wiki    = Tex("Wiki Generic", font_size=52).to_edge(UP)
        title_bombard = Tex("Corrupted Bombard", font_size=52).to_edge(UP)
        title_heavy   = Tex("Corrupted Heavy Gunner", font_size=52).to_edge(UP)

        # ---------- Generic (wiki) formulas ----------
        generic_mul = MathTex(
            r"\text{Damage Multiplier} = 1 + ",
            rf"{K_WIKI}",
            r"\cdot \big(",
            r"\text{Current Level}",
            r"-",
            r"\text{Base Level}",
            rf"\big)^{{{P_WIKI}}}",
            substrings_to_isolate=[r"\text{Current Level}", r"\text{Base Level}", rf"{K_WIKI}", rf"{P_WIKI}"],
            font_size=44
        ).set_color_by_tex(r"\text{Current Level}", cL)\
         .set_color_by_tex(r"\text{Base Level}", cBase)\
         .set_color_by_tex(rf"{K_WIKI}", cConst)\
         .set_color_by_tex(rf"{P_WIKI}", cConst)

        generic_dmg = MathTex(
            r"\text{Damage}(L) = ",
            r"\text{Base Damage}",
            r"\times",
            r"\text{Damage Multiplier}",
            substrings_to_isolate=[r"\text{Base Damage}", r"\text{Damage Multiplier}"],
            font_size=44
        ).set_color_by_tex(r"\text{Base Damage}", cDmg)\
         .set_color_by_tex(r"\text{Damage Multiplier}", cMul)

        group_generic = VGroup(generic_mul, generic_dmg).arrange(DOWN, buff=0.6).next_to(title_wiki, DOWN, buff=0.5)

        # Intro: show wiki + title
        self.play(FadeIn(title_wiki, shift=0.2*UP), Write(generic_mul), run_time=1.6)
        self.play(FadeIn(generic_dmg, shift=DOWN*0.2), run_time=1.0)
        self.wait(0.5)

        # ---------- Bombard formulas (morph) ----------
        bombard_mul = MathTex(
            r"\text{Damage Multiplier} = 1 + ",
            rf"{BOMBARD_K}",
            r"\cdot \big(",
            r"L", r"-", rf"{BOMBARD_BASE_LEVEL}",
            rf"\big)^{{{BOMBARD_P}}}",
            font_size=46
        ).set_color_by_tex("L", cL).set_color_by_tex(rf"{BOMBARD_BASE_LEVEL}", cBase)\
         .set_color_by_tex(rf"{BOMBARD_K}", cConst)\
         .set_color_by_tex(rf"{BOMBARD_P}", cConst)

        bombard_dmg = MathTex(
            r"\text{Damage}(L) = ",
            rf"{BOMBARD_BASE_DAMAGE}",
            r"\times",
            r"\text{Damage Multiplier}",
            font_size=46
        ).set_color_by_tex(rf"{BOMBARD_BASE_DAMAGE}", cDmg)\
         .set_color_by_tex(r"\text{Damage Multiplier}", cMul)

        group_bombard = VGroup(bombard_mul, bombard_dmg).arrange(DOWN, buff=0.6).move_to(group_generic)

        self.play(TransformMatchingTex(title_wiki, title_bombard), run_time=0.8)
        self.play(TransformMatchingTex(group_generic, group_bombard, path_arc=30*DEGREES), run_time=1.8)
        self.wait(0.4)
        self.play(FadeOut(group_bombard, title_bombard), run_time=0.7)
        

        # ---------- Back to wiki, then Heavy (morph) ----------
        self.play(FadeIn(title_wiki, shift=0.2*UP), FadeIn(group_generic), run_time=0.6)

        heavy_mul = MathTex(
            r"\text{Damage Multiplier} = 1 + ",
            rf"{HEAVY_K}",
            r"\cdot \big(",
            r"L", r"-", rf"{HEAVY_BASE_LEVEL}",
            rf"\big)^{{{HEAVY_P}}}",
            font_size=46
        ).set_color_by_tex("L", cL).set_color_by_tex(rf"{HEAVY_BASE_LEVEL}", cBase)\
         .set_color_by_tex(rf"{HEAVY_K}", cConst)\
         .set_color_by_tex(rf"{HEAVY_P}", cConst)

        heavy_dmg = MathTex(
            r"\text{Damage}(L) = ",
            rf"{HEAVY_BASE_DAMAGE}",
            r"\times",
            r"\text{Damage Multiplier}",
            font_size=46
        ).set_color_by_tex(rf"{HEAVY_BASE_DAMAGE}", cDmg)\
         .set_color_by_tex(r"\text{Damage Multiplier}", cMul)

        group_heavy = VGroup(heavy_mul, heavy_dmg).arrange(DOWN, buff=0.6).move_to(group_generic)

        self.play(TransformMatchingTex(title_wiki, title_heavy), run_time=0.8)
        self.play(TransformMatchingTex(group_generic, group_heavy, path_arc=-30*DEGREES), run_time=1.8)
        self.wait(0.4)
        self.play(FadeOut(group_heavy, title_heavy), run_time=0.7)

        # ---------- Plot & intersection (Bombard) ----------
        self._plot_and_intersect(
            scene_title="Corrupted Bombard",
            base_damage=BOMBARD_BASE_DAMAGE,
            base_level=BOMBARD_BASE_LEVEL,
            K=BOMBARD_K,
            P=BOMBARD_P,
            target_damage=TARGET_DAMAGE,
            curve_color=cBase,
            dot_color=YELLOW
        )

        # ---------- Plot & intersection (Heavy) ----------
        self._plot_and_intersect(
            scene_title="Corrupted Heavy Gunner",
            base_damage=HEAVY_BASE_DAMAGE,
            base_level=HEAVY_BASE_LEVEL,
            K=HEAVY_K,
            P=HEAVY_P,
            target_damage=TARGET_DAMAGE,
            curve_color=cBase,
            dot_color=YELLOW
        )

    # ---------- Plot + horizontal line + drop to X-axis ----------
    def _plot_and_intersect(self, scene_title, base_damage, base_level, K, P, target_damage, curve_color, dot_color):
        title_tex = Tex(scene_title, font_size=48).to_edge(UP)
        self.play(FadeIn(title_tex, shift=0.2*UP), run_time=0.6)

        # Compute intersection
        def _nice_number(x, round_to=True):
            #Return 1, 2, 5, or 10 times a power of 10, close to x.
            if x <= 0:
                return 1
            exp = math.floor(math.log10(x))
            frac = x / (10 ** exp)
            if round_to:
                if frac < 1.5: nice = 1
                elif frac < 3: nice = 2
                elif frac < 7: nice = 5
                else:          nice = 10
            else:
                if frac <= 1:  nice = 1
                elif frac <= 2:nice = 2
                elif frac <= 5:nice = 5
                else:          nice = 10
            return nice * (10 ** exp)

        def nice_axis(vmin, vmax, n_ticks=6, integers=True):
            #Compute rounded axis [lo, hi, step] with about n_ticks.
            if vmin == vmax:
                vmax = vmin + 1
            span = vmax - vmin
            step = _nice_number(span / max(1, (n_ticks - 1)), round_to=True)
            lo   = math.floor(vmin / step) * step
            hi   = math.ceil (vmax / step) * step
            if integers:
                step = max(1, int(round(step)))
                lo   = int(math.floor(lo / step) * step)
                hi   = int(math.ceil (hi / step) * step)
            return lo, hi, step
        
        L_star = solve_level_for_damage(target_damage, base_damage, base_level, K, P)
        x_max  = max(base_level + 10, math.ceil(L_star * 1.08))
        y_max  = math.ceil(target_damage * 1.15)

        # --- Get clean axis ranges
        x_lo, x_hi, x_step = nice_axis(base_level, x_max, n_ticks=8, integers=True)
        y_lo, y_hi, y_step = nice_axis(0,          y_max,  n_ticks=6, integers=True)

        # (Optional) if you want to FORCE the x-axis to start exactly at base_level:
        # x_lo = base_level

        # Precompute label positions so only the rounded numbers appear
        x_nums = np.arange(x_lo, x_hi + x_step/2, x_step)
        y_nums = np.arange(y_lo, y_hi + y_step/2, y_step)

        ax = Axes(
            x_range=[x_lo, x_hi, x_step],
            y_range=[y_lo, y_hi, y_step],
            x_length=10.5, y_length=5.8,
            axis_config={
                "include_numbers": True,
                "font_size": 28,
                "color": GREY_B,
                "decimal_number_config": {"num_decimal_places": 0},  # integers only
            },
            x_axis_config={"numbers_to_include": x_nums},
            y_axis_config={"numbers_to_include": y_nums},
            tips=False,
        ).to_edge(DOWN)

        # Only X label (no Y label per request)
        x_label = ax.get_x_axis_label(Tex("Level $L$", font_size=32))
        y_label = ax.get_y_axis_label(Tex("Damage", font_size=32))

        self.play(Create(ax), FadeIn(x_label, y_label), run_time=1.0)

        curve = ax.plot(
            lambda L: damage(L, base_damage, base_level, K, P),
            x_range=[base_level, x_max],
            use_smoothing=False,
            color=curve_color,
            stroke_width=6
        )
        curve_label = MathTex(
            rf"\text{{Damage}}(L) = {base_damage}\cdot\Big(1+{K}\,(L-{base_level})^{{{P}}}\Big)",
            font_size=20
        ).move_to([-2, 0, 0]).set_color(curve_color)
   
        self.play(Create(curve), FadeIn(curve_label), run_time=1.4)

        # Horizontal line at target damage (no Y label text)
        y_line = ax.get_horizontal_line(
            ax.c2p(L_star, target_damage),  # point where it should end
            color=RED,
            stroke_width=5
        )
        self.play(Create(y_line), run_time=0.8)

        # Intersection dot
        p = ax.c2p(L_star, target_damage)
        dot = Dot(p, color=dot_color, radius=0.07)
        self.play(GrowFromCenter(dot), run_time=0.6)

        # Placing numeric readout of the level
        L_rounded = int(round(L_star))
        readout = MathTex(rf"L \approx {L_rounded}", font_size=44, color=dot_color)
        readout_bg = BackgroundRectangle(readout, fill_opacity=0.8, buff=0.15)
        readout_grp = VGroup(readout_bg, readout)
        readout_grp.next_to(p, DOWN, buff=0.3)

        self.play(FadeIn(readout_grp, scale=0.9), run_time=0.6)
        self.wait(0.6)

        # Clean up
        self.play(
            *[FadeOut(m) for m in [title_tex, ax, x_label, y_label, curve, curve_label, y_line, dot, readout_grp]],
            run_time=0.9
        )


































class EHPFormula2(Scene):

    def construct(self):
        title = Text("Effective Health (EHP)", weight=BOLD).to_edge(UP)
        self.play(FadeIn(title))

        # 1) Descriptive formula (built from stable parts)
        #    EHP = [ Modded Health · (Net Armor + 300) ] / [ 300 (1 − Net Damage Reduction) (1 + Damage Type Modifier) ]
        desc = MathTex(
            r"\boldsymbol{EHP}", r"\boldsymbol{=}",
            r"\frac{\textbf{Modded Health} \cdot (\textbf{Net Armor} + 300)}{300 \, (1 - \textbf{Net Damage Reduction}) \, (1 + \textbf{Damage Type Modifier})}",
        )
        desc.scale_to_fit_width(config.frame_width - 1).next_to(title, DOWN, buff=0.6)
        desc[0].set_color(RED)
        desc[2][0:12].set_color(RED)
        desc[2][14:22].set_color(YELLOW)
        desc[2][34:52].set_color(DARK_BLUE)
        desc[2][56:73].set_color(PURPLE)

        desc.move_to(ORIGIN)

        self.play(Write(desc))
        self.wait(1)

        # 2) Condensed (abbreviations) — keep denominator colors
        short = MathTex(
            r"\boldsymbol{EHP}", r"\boldsymbol{=}",
            r"\frac{\textbf{H} \cdot (\textbf{A} + 300) }{ 300 \, (1 - \textbf{DR}) \, (1 + \textbf{DTM}) }"
        )
        short.scale_to_fit_width(config.frame_width - 1).move_to(desc)

        short[0].set_color(RED)
        short[2][0:1].set_color(RED)
        short[2][3:4].set_color(YELLOW)
        short[2][16:18].set_color(DARK_BLUE)
        short[2][22:25].set_color(PURPLE)
        short.move_to(ORIGIN)

        self.play(TransformMatchingTex(desc, short, path_arc=PI/10))
        self.wait(1)

        # 3) Numeric substitution
        H, A, DR, DTM = NOMINAL_HEALTH, NET_ARMOR, NET_DAMAGE_REDUCTION, DAMAGE_TYPE_MOD
        dr_s, dtm_s = fmt(DR), fmt(DTM)

        nums = MathTex(
            f"\\boldsymbol{{EHP}}", f"\\boldsymbol{{=}}",
            f"\\frac{{{fmt(H)} \\cdot ({fmt(A)} + 300) }}"
            f"{{ 300 \\, (1 - {dr_s}) \\, (1 + {dtm_s}) }}",
        )
        nums.scale_to_fit_width(config.frame_width - 1).move_to(short)

        nums[0].set_color(RED)
        nums[2][0:5].set_color(RED)
        nums[2][5:8].set_color(YELLOW)
        nums[2][20:24].set_color(DARK_BLUE)
        nums[2][28:31].set_color(PURPLE)
        nums.move_to(ORIGIN)

        self.play(TransformMatchingTex(short, nums, path_arc=-PI/10))
        self.wait(1)

        # 4) Compute and display result
        ehp_value = (H * (A + 300)) / (300 * (1 - DR) * (1 + DTM))
        result = VGroup(
            MathTex("\\boldsymbol{EHP}", "\\thickapprox"),
            DecimalNumber(ehp_value, num_decimal_places=RESULT_DECIMALS),
        ).arrange(RIGHT, buff=0.25).next_to(nums, DOWN, buff=0.5).scale(2)

        result[0][0].set_color(RED)

        underline = always_redraw(
            lambda: Underline(result[1], buff=0.06).set_color(WHITE)
        )

        result_group = VGroup(result, underline)
        self.play(FadeIn(result_group, shift=DOWN*0.2))
        self.wait(1)

        # Clean end frame
        end_result = result.copy()
        end_underline = always_redraw(
            lambda: Underline(end_result[1], buff=0.06).set_color(WHITE)
        )
        end_group = VGroup(nums.copy(), VGroup(end_result, end_underline)).arrange(DOWN, buff=0.4)
        end_group.move_to(ORIGIN)

        self.play(
            LaggedStart(
                FadeOut(title, shift=UP*0.2),
                Transform(VGroup(nums, result_group), end_group),
                lag_ratio=0.15
            )
        )

        self.wait(1)