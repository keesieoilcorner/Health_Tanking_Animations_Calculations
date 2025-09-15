from manim import *
import numpy as np
import math
import random, numpy as np

config.pixel_width  = 2560   # or 2560
config.pixel_height = 1440   # or 1440
config.frame_rate   = 60     # optional

#activate env .\manim-env\Scripts\Activate.ps1
#render manim -pqh Warframe_Animations.py EnemyHealthAndDamage
#render clean manim -pqh EHP_Formula_Animations.py EHPComputeExample --format=mov --transparent

class EHPFormula(Scene):
    def construct(self):
        # --- Harden determinism
        random.seed(0)
        np.random.seed(0)
        config.threads = 1  # avoid nondeterministic submobject ordering

        # --- Formulas (unchanged layout)
        formula_long = MathTex(
            r"\mathbf{EHP}", r"\boldsymbol{=}",
            r"\frac{(\textbf{Modded Health} + \textbf{Total Energy} \cdot \textbf{Energy Efficiency})}"
            r"{(\textbf{1} \cdot (\textbf{1} - \textbf{DR}_1) \cdot (1 - \textbf{DR}_2) \cdot "
            r"\dfrac{\textbf{Net Armor}}{\textbf{Net Armor}+300} \cdot (1 - \textbf{DR}_4)\ldots)}"
        ).scale_to_fit_width(config.frame_width - 1).move_to(ORIGIN)
        formula_long[0].set_color(RED)

        formula_dense = MathTex(
            r"\mathbf{EHP}", r"\boldsymbol{=}",
            r"\frac{(\textbf{H} + \textbf{E} \cdot \textbf{Eff})}"
            r"{\prod\limits_{\substack{i \\ \text{all DR}}} (1 - \mathbf{DR}_i)}"
        ).scale_to_fit_width(config.frame_width - 1).move_to(ORIGIN)
        formula_dense[0].set_color(RED)

        # --- Recommended explicit mapping
        key_map = {
            r"\mathbf{EHP}": r"\mathbf{EHP}",
            r"\boldsymbol{=}": r"\boldsymbol{=}",
            r"(\textbf{Modded Health} + \textbf{Total Energy} \cdot \textbf{Energy Efficiency})":
                r"(\textbf{H} + \textbf{E} \cdot \textbf{Eff})",
            r"\dfrac{\textbf{Net Armor}}{\textbf{Net Armor}+300}":
                r"(1 - \mathbf{DR}_i)",  # armor term becomes one of the DR_i factors
        }

        # --- Animation
        self.play(Write(formula_long, run_time=1.8, rate_func=rate_functions.ease_out_cubic))
        self.wait(0.3)

        # Keep positions aligned
        formula_dense.move_to(formula_long)

        # Only morph explicitly mapped parts; fade/appear the rest for stability
        self.play(
            TransformMatchingTex(
                formula_long, formula_dense,
                key_map=key_map,
                transform_mismatches=True,   # <- prevents "best-guess" pairing
                path_arc=PI/12,
                lag_ratio=0.05,
                rate_func=rate_functions.ease_in_out_cubic
            ),
            run_time=2.0
        )
        self.wait(0.5)

class EHPComputeExample(Scene):
    def construct(self):
        # Repeatability
        random.seed(0); np.random.seed(0); config.threads = 1

        # --- Params (edit these) ---
        H   = 750
        E   = 0
        Eff = 0    # e.g. 2.4 for 240%
        A   = 300     # armor term A/(A+300)
        DR1 = 0.90
        DR2 = 0.90
        DR_armor = A/(A+300)
        dr_factors = [DR1, DR2, DR_armor]  # add/remove as needed
  
        # --- Precompute ---
        numerator_value = H + E*Eff
        one_minus = [1 - d for d in dr_factors]
        denom_value = float(np.prod(one_minus))
        ehp_value = numerator_value / denom_value

        # --- Layout helpers ---
        SAFE_W = config.frame_width - 2.0  # left/right margin
        def center_fit(mobj):
            mobj.scale_to_fit_width(min(SAFE_W, mobj.width)).move_to(ORIGIN)
            return mobj

        def f(x):  # concise numbers
            s = f"{x:.6g}"
            return s

        # --- Step 1: Dense formula
        step1 = MathTex(
            r"\mathbf{EHP}", r"\boldsymbol{=}",
            r"\frac{(\textbf{H} + \textbf{E}\cdot\textbf{Eff})}"
            r"{\prod\limits_{\substack{i \\ \text{all DR}}} (1 - \mathbf{DR}_i)}"
        )
        
        center_fit(step1)
        step1.scale_to_fit_width(config.frame_width - 1)
        step1[0].set_color(RED)

        self.add((step1))
        self.wait(0.5)
        self.play(ScaleInPlace(step1, scale_factor=0.5), run_time=1 ,rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.2)

        # --- Step 2: Expand product to explicit factors (matches dr_factors length)
        labels = [rf"\mathbf{{DR}}_{i+1}" for i in range(len(dr_factors))]
        denom_expanded_tex = "".join([rf"\left(1-{lab}\right)" for lab in labels])

        step2 = MathTex(
            r"\mathbf{EHP}", r"\boldsymbol{=}",
            r"\frac{(\textbf{H} + \textbf{E}\cdot\textbf{Eff})}{" + denom_expanded_tex + r"}"
        )
        center_fit(step2)
        step2[0].set_color(RED)

        self.play(TransformMatchingTex(
            step1, step2,
            key_map={r"\prod\limits_{\substack{i \\ \text{all DR}}} (1 - \mathbf{DR}_i)": denom_expanded_tex},
            transform_mismatches=False, path_arc=PI/16, lag_ratio=0.05
        ), run_time=1.2)
        self.wait(0.15)

        # --- Step 3: Substitute numbers
        numerator_numbers = rf"\left({f(H)} + {f(E)}\cdot{f(Eff)}\right)"
        denom_numbers = "".join([rf"\left(1-{f(d)}\right)" for d in dr_factors])

        step3 = MathTex(
            r"\mathbf{EHP}", r"\boldsymbol{=}",
            r"\frac{" + numerator_numbers + r"}{" + denom_numbers + r"}"
        )
        center_fit(step3)
        step3[0].set_color(RED)

        key_map_subs = {r"(\textbf{H} + \textbf{E}\cdot\textbf{Eff})": numerator_numbers}
        for lab, val in zip(labels, dr_factors):
            key_map_subs[lab] = f"{f(val)}"

        self.play(TransformMatchingTex(
            step2, step3, key_map=key_map_subs, transform_mismatches=True,
            path_arc=PI/20, lag_ratio=0.04
        ), run_time=1.3)
        self.wait(0.15)

        # --- Step 4: Evaluate numerator only
        step4 = MathTex(
            r"\mathbf{EHP}", r"\boldsymbol{=}",
            r"\frac{" + f(numerator_value) + r"}{" + denom_numbers + r"}"
        )
        center_fit(step4)
        step4[0].set_color(RED)

        self.play(TransformMatchingTex(
            step3, step4, key_map={numerator_numbers: f(numerator_value)},
            transform_mismatches=False
        ), run_time=0.9)
        self.wait(0.1)

       # --- Step 5: Evaluate (1 - DR) factors, but instead of showing each,
        # jump straight to the multiplied value

        # First create the direct fraction with multiplied denominator
        step5 = MathTex(
            r"\mathbf{EHP}", r"\boldsymbol{=}",
            r"\frac{" + f(numerator_value) + r"}{" + f(denom_value) + r"}"
        )
        center_fit(step5)
        step5[0].set_color(RED)

        # Transform from the full factor form directly to the single decimal denominator
        self.play(TransformMatchingTex(
            step4, step5,
            key_map={denom_numbers: f(denom_value)},
            transform_mismatches=False
        ), run_time=1.0)
        self.wait(0.2)

        # --- Step 6: Final numeric EHP
        value_str  = f"{ehp_value:,.2f}".replace(",", r"\,")  # e.g. 2\,864\,000\,000.00
        value_bold = rf"\mathbf{{{value_str}}}"

        step6 = MathTex(r"\mathbf{EHP}", r"\boldsymbol{=}", value_bold
        )
        center_fit(step6)
        step6[0].set_color(RED)


        self.play(TransformMatchingTex(
            step5, step6,
            transform_mismatches=True
        ), run_time=0.8)

        self.play(step6.animate.scale(2), run_time=0.6, rate_func=rate_functions.ease_in_out_back)

        self.wait(2)

class ArmorDamageReduction(Scene):
    def construct(self):
        # --- Title & formula ---
        title = Text("Armor Damage Reduction", weight=BOLD).to_edge(UP)
        formula = MathTex(r"\text{DR} = \frac{Net Armor}{Net Armor + 300}",
        )

        formula.next_to(title, DOWN)
        self.play(FadeIn(title, shift=UP*0.2))
        self.play(Write(formula))
        self.wait(2)
        self.play(
            LaggedStart(
            FadeOut(formula, run_time=0.5),
            FadeOut(title, run_time=0.5),
            lag_ratio=0.15
            )
        )

        # --- Axes setup ---
        axes = Axes(
            x_range=[0, 4000, 500],
            y_range=[0, 1, 0.1],
            x_length=10,
            y_length=6,
            tips=False,
        )
        x_label = axes.get_x_axis_label(Tex("Armor $A$"))
        y_label = axes.get_y_axis_label(Tex("Damage Reduction (DR)"))
        y_label.next_to(axes.y_axis, UP, buff=0.15).shift(RIGHT*3)
        graph_group =  VGroup(axes, x_label, y_label).to_edge(DOWN).scale(0.9)
        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label))

        # --- Plot DR(A) ---
        dr = lambda a: a / (a + 300)
        curve = axes.plot(dr, x_range=[0, 4000], stroke_width=6)
        self.play(Create(curve))
        self.wait(0.5)

        # --- Target 90% and A=2700 marker ---
        target_dr = 0.9
        target_A = 2700
        target_point = axes.coords_to_point(target_A, target_dr)
        h_line = DashedLine(
            axes.coords_to_point(0, target_dr),
            axes.coords_to_point(target_A, target_dr),
            dash_length=0.1
        )
        v_line = DashedLine(
            axes.coords_to_point(target_A, 0),
            axes.coords_to_point(target_A, target_dr),
            dash_length=0.1
        )
        dot = Dot(target_point)
        tag_dr = MathTex(r"0.9").next_to(h_line, LEFT, buff=0.2)
        tag_A = MathTex(r"A\approx2700").next_to(v_line, DOWN, buff=0.2)
        self.play(Create(h_line), Create(v_line))
        self.play(FadeIn(dot, scale=0.8), FadeIn(tag_dr), FadeIn(tag_A))
        self.wait(3)

        # Clean finish
        self.play(*[FadeOut(mobj) for mobj in self.mobjects])