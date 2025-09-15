from manim import *
import numpy as np

config.pixel_width  = 2560   # or 2560
config.pixel_height = 1440   # or 1440
config.frame_rate   = 60     # optional

#activate env .\manim-env\Scripts\Activate.ps1
#render clean manim -pqh Enemy_Health_Scaling.py EnemyHealthPlotSimple --format=mov --transparent

class EnemyHealthPlotFull(Scene):
    def construct(self):
        # ---------------------------
        # Tunables
        # ---------------------------
        BASE_LEVEL   = 4          # "Base Level" from the screenshots
        BASE_HEALTH  = 300       # Health at BASE_LEVEL (set this to your unit's base HP)
        X_MAX_OFFSET = 200        # how far above BASE_LEVEL to show
        SHOW_COMPONENTS = True    # set False to hide f1/f2 overlays
        # ---------------------------

        # --- Formulas from the screenshots ---
        # T(x) = (x - BaseLevel - 70)/10
        def T(x):
            return (x - BASE_LEVEL - 70.0)/10.0

        # Smoothstep S1(x) over offset in [70, 80]
        # S1(x) = 0, offset<70 ; = 3t^2 - 2t^3, 70<=offset<=80 ; = 1, offset>80
        def S1(x):
            offset = x - BASE_LEVEL
            if offset < 70:
                return 0.0
            if offset > 80:
                return 1.0
            t = T(x)
            return 3*t**2 - 2*t**3

        # f1(x) = 1 + 0.015 (x - BaseLevel)^{2.12}, for offset < 70
        def f1(x):
            offset = max(x - BASE_LEVEL, 0.0)
            return 1.0 + 0.015 * (offset**2.12)

        # f2(x) = 1 + (24*sqrt(5)/5) (x - BaseLevel)^{0.72}, for offset > 80
        def f2(x):
            offset = max(x - BASE_LEVEL, 0.0)
            return 1.0 + (24.0*np.sqrt(5.0)/5.0) * (offset**0.72)

        # Smoothly blended scale factor
        # scale(x) = (1 - S1) f1 + S1 f2
        def scale(x):
            s = S1(x)
            return (1.0 - s)*f1(x) + s*f2(x)

        # Enemy Health = BaseHealth * scale(x)
        def health(x):
            return BASE_HEALTH * scale(x)

        # ---------------------------
        # Axes
        # ---------------------------
        x_min = BASE_LEVEL - BASE_LEVEL
        x_max = BASE_LEVEL + X_MAX_OFFSET
        # pick round-ish y max by sampling a few points
        samples = [health(BASE_LEVEL + k) for k in (0, 70, 80, 120, X_MAX_OFFSET)]
        y_max_guess = max(samples)*1.08
        y_step = 0.0
        # choose a reasonable y tick step
        magnitude = 10**int(np.floor(np.log10(y_max_guess)))
        for m in [1, 2, 5, 10]:
            if y_max_guess/magnitude <= 7:
                y_step = m*magnitude/2 if m in (1,2) else m*magnitude
                break
        if y_step == 0:
            y_step = magnitude

        ax = Axes(
            x_range=[x_min, x_max, max(10, (x_max-x_min)//8)],
            y_range=[0, y_max_guess, y_step],
            x_length=10.5, y_length=5.8,
            tips=False,
            axis_config={"include_numbers": True, "font_size": 28, "color": GREY_B},
        ).to_edge(DOWN).scale(0.9)

        x_label = ax.get_x_axis_label(Tex("Level", font_size=32))
        y_label = ax.get_y_axis_label(Tex("Enemy Health", font_size=32).rotate(90*DEGREES), edge=LEFT, direction=LEFT, buff=0.5)

        title = Tex(r"\textbf{Enemy Health vs. Level}", font_size=36).to_edge(UP)

        self.play(FadeIn(title))
        self.play(Create(ax), FadeIn(x_label), FadeIn(y_label))

        # labels for f1, f2
        lbl_f1 = MathTex(r"f_1(x)=1+0.015(x-\mathrm{BL})^{2.12}", font_size=28).next_to(title, DOWN)
        lbl_f2 = MathTex(r"f_2(x)=1+\frac{24\sqrt{5}}{5}(x-\mathrm{BL})^{0.72}", font_size=28).next_to(lbl_f1, DOWN, buff=0.2)
        
        box_f1 = SurroundingRectangle(lbl_f1, buff=0.2, corner_radius=0.2, color=RED)
        box_f2 = SurroundingRectangle(lbl_f2, buff=0.2, corner_radius=0.2, color=RED)

        self.play(FadeIn(lbl_f1))
        self.play(FadeIn(lbl_f2, shift=DOWN*0.4))
        self.wait(1)
        self.play(Create(box_f1))
        self.wait(1)
        self.play(Uncreate(box_f1))
        self.play(Create(box_f2))
        self.wait(1)
        self.play(Uncreate(box_f2))
        self.wait(1)
        
        # Smoothstep formula badge
        smooth_lbl = MathTex(
            r"S_1(x)=\begin{cases}"
            r"0,& x-\mathrm{BL }<70\\"
            r"3T(x)^2-2T(x)^3,& 70\le x-\mathrm{BL}\le 80\\"
            r"1,& x-\mathrm{BL}>80"
            r"\end{cases}\!,\quad T(x)=\dfrac{x-\mathrm{BL}-70}{10}",
            font_size=28
        ).next_to(lbl_f2, DOWN)
        self.play(FadeIn(smooth_lbl, shift=DOWN*0.4))
        self.wait(4)

        self.play(AnimationGroup(
            FadeOut(smooth_lbl, shift=UP*0.2),
            FadeOut(lbl_f2, shift=UP*0.2),
            FadeOut(lbl_f1),
            lag_ratio=0.20,
            run_time=1
        ))

        # ---------------------------
        # Curves
        # ---------------------------
        # Final (blended) health curve
        health_graph = ax.plot(health, x_range=[x_min, x_max, 0.25], use_smoothing=True)
        health_graph.set_stroke(width=5)
        self.play(Create(health_graph), run_time=2)

        # ---------------------------
        # Transition markers at BL+70 and BL+80
        # ---------------------------
        x70 = BASE_LEVEL + 70
        x80 = BASE_LEVEL + 80

        v70 = ax.get_vertical_line(ax.c2p(x70, health(x70)), color=GREY_B, stroke_width=2)
        v80 = ax.get_vertical_line(ax.c2p(x80, health(x80)), color=GREY_B, stroke_width=2)
        t70 = MathTex(r"\mathrm{BL}+70", font_size=28).next_to(v70, UP, buff=0.15).shift(LEFT*0.7)
        t80 = MathTex(r"\mathrm{BL}+80", font_size=28).next_to(v80, UP, buff=0.15).shift(LEFT*0.5)
 
        self.play(Create(v70), FadeIn(t70))
        self.play(Create(v80), FadeIn(t80))

        self.wait(1.5)

        self.play(FadeOut(v70, v80, t70, t80))

        highlight = ax.plot(health, x_range=[BASE_LEVEL+80, x_max], color=RED, stroke_width=6)
        self.play(FadeIn(highlight))
        self.wait(1)
        self.play(FadeOut(highlight))

        # 1) Build long-range axes aligned & styled like the first
        def nice_step(max_val, nticks=6):
            if max_val <= 0: return 1
            raw = max_val/nticks
            m = 10**int(np.floor(np.log10(raw)))
            for k in (1, 2, 2.5, 5, 10):
                if raw <= k*m:
                    return k*m
            return 10*m
        
        y_final = health(9999)*1.08
        y_step_final = nice_step(y_final)

        ax_long = Axes(
            x_range=[x_min, 9999, 1000],                 # final x-range + tick step
            y_range=[0, y_final, y_step_final],            # keep your y range (or recompute)
            x_length=10.5, y_length=5.8,
            tips=False,
            axis_config={"include_numbers": True, "font_size": 28, "color": GREY_B},
        ).to_edge(DOWN).scale(0.9).move_to(ax)           # align with the existing axes

        # 2) Build the long-range curve on the long axes
        long_curve = ax_long.plot(
            health, x_range=[x_min, 10000, 0.25], use_smoothing=True
        ).set_stroke(width=5)

        xmax_tr = ValueTracker(x_max)  # start where your first plot ends

        long_curve = always_redraw(
            lambda: ax_long.plot(
                health, x_range=[x_min, xmax_tr.get_value(), 0.25], use_smoothing=True
            ).set_stroke(width=5)
        )

        self.play(FadeTransform(health_graph,long_curve), run_time=1)

        self.play(
            Transform(ax, ax_long),          
            xmax_tr.animate.set_value(10000),
            run_time=2
        )

        self.wait(2)

############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################

class EnemyHealthPlotSimple(Scene):
    def construct(self):
        # ---------------------------
        # Tunables
        # ---------------------------
        BASE_LEVEL   = 4          # "Base Level" from the screenshots
        BASE_HEALTH  = 300       # Health at BASE_LEVEL (set this to your unit's base HP)
        X_MAX_OFFSET = 200        # how far above BASE_LEVEL to show
        SHOW_COMPONENTS = True    # set False to hide f1/f2 overlays
        # ---------------------------

        # --- Formulas from the screenshots ---
        # T(x) = (x - BaseLevel - 70)/10
        def T(x):
            return (x - BASE_LEVEL - 70.0)/10.0

        # Smoothstep S1(x) over offset in [70, 80]
        # S1(x) = 0, offset<70 ; = 3t^2 - 2t^3, 70<=offset<=80 ; = 1, offset>80
        def S1(x):
            offset = x - BASE_LEVEL
            if offset < 70:
                return 0.0
            if offset > 80:
                return 1.0
            t = T(x)
            return 3*t**2 - 2*t**3

        # f1(x) = 1 + 0.015 (x - BaseLevel)^{2.12}, for offset < 70
        def f1(x):
            offset = max(x - BASE_LEVEL, 0.0)
            return 1.0 + 0.015 * (offset**2.12)

        # f2(x) = 1 + (24*sqrt(5)/5) (x - BaseLevel)^{0.72}, for offset > 80
        def f2(x):
            offset = max(x - BASE_LEVEL, 0.0)
            return 1.0 + (24.0*np.sqrt(5.0)/5.0) * (offset**0.72)

        # Smoothly blended scale factor
        # scale(x) = (1 - S1) f1 + S1 f2
        def scale(x):
            s = S1(x)
            return (1.0 - s)*f1(x) + s*f2(x)

        # Enemy Health = BaseHealth * scale(x)
        def health(x):
            return BASE_HEALTH * scale(x)

        # ---------------------------
        # Axes
        # ---------------------------
        x_min = BASE_LEVEL - BASE_LEVEL
        x_max = BASE_LEVEL + X_MAX_OFFSET
        # pick round-ish y max by sampling a few points
        samples = [health(BASE_LEVEL + k) for k in (0, 70, 80, 120, X_MAX_OFFSET)]
        y_max_guess = max(samples)*1.08
        y_step = 0.0
        # choose a reasonable y tick step
        magnitude = 10**int(np.floor(np.log10(y_max_guess)))
        for m in [1, 2, 5, 10]:
            if y_max_guess/magnitude <= 7:
                y_step = m*magnitude/2 if m in (1,2) else m*magnitude
                break
        if y_step == 0:
            y_step = magnitude

        ax = Axes(
            x_range=[x_min, x_max, max(10, (x_max-x_min)//8)],
            y_range=[0, y_max_guess, y_step],
            x_length=10.5, y_length=5.8,
            tips=False,
            axis_config={"include_numbers": True, "font_size": 28, "color": GREY_B},
        ).to_edge(DOWN).scale(0.9)

        x_label = ax.get_x_axis_label(Tex("Level", font_size=32))
        y_label = ax.get_y_axis_label(Tex("Enemy Health", font_size=32).rotate(90*DEGREES), edge=LEFT, direction=LEFT, buff=0.5)

        title = Tex(r"\textbf{Enemy Health vs. Level}", font_size=36).to_edge(UP)

        self.play(FadeIn(title))
        self.play(Create(ax), FadeIn(x_label), FadeIn(y_label))


        # ---------------------------
        # Curves
        # ---------------------------
        # Final (blended) health curve
        health_graph = ax.plot(health, x_range=[x_min, x_max, 0.25], use_smoothing=True)
        health_graph.set_stroke(width=5)
        self.play(Create(health_graph), run_time=2)

        self.wait(2)

        self.play(
            Uncreate(health_graph), 
            FadeOut(x_label), 
            FadeOut(y_label), 
            Uncreate(ax), 
            FadeOut(title), 
            run_time=2
            )