from manim import *
import numpy as np

config.pixel_width  = 2560
config.pixel_height = 1440
config.frame_rate   = 60

#activate env .\manim-env\Scripts\Activate.ps1
#render manim -pqh Warframe_Animations.py EnemyHealthAndDamage
#render clean manim -pqh Armor_Changes.py TennoDRComparison --format=mov --transparent

class TennoDRComparison(Scene):
    def construct(self):
        # ---------- Model ----------
        C_ARMOR = 300.0
        A1, A2 = 500.0, 750.0
        C1, C2, C3 = 0.50, 0.75, 0.90
        HL_ARMOR = 300
        LAMBDA = np.log(2) / HL_ARMOR

        def smoothstep(t):
            t = np.clip(t, 0.0, 1.0)
            return 3*t**2 - 2*t**3

        def dr_vanilla(a):
            a = np.asarray(a, dtype=float)
            return a / (a + C_ARMOR)

        def dr_proposed_array(A):
            A = np.asarray(A, dtype=float)

            s1 = np.zeros_like(A)
            m1 = (A >= 0) & (A < A1)
            s1[m1] = smoothstep((A[m1] - 0.0) / (A1 - 0.0))
            s1[A >= A1] = 1.0

            s2 = np.zeros_like(A)
            m2 = (A >= A1) & (A < A2)
            s2[m2] = smoothstep((A[m2] - A1) / (A2 - A1))
            s2[A >= A2] = 1.0

            s3 = np.zeros_like(A)
            m3 = (A >= A2)
            s3[m3] = 1.0 - np.exp(-LAMBDA * (A[m3] - A2))

            remaining = (1 - C1*s1) * (1 - C2*s2) * (1 - C3*s3)
            return 1.0 - remaining

        # ---------- Axes ----------
        x_min, x_max = 0, 5000
        y_min, y_max = 0.0, 1.0
        ax = Axes(
            x_range=[x_min, x_max, 500],
            y_range=[y_min, y_max, 0.1],
            x_length=10.5, y_length=5.8,
            tips=False,
            axis_config={"include_numbers": True, "font_size": 36}
        ).to_edge(DOWN).scale(0.8)

        x_label = Text("Armor", font_size=28).next_to(ax.x_axis, DOWN, buff=0.3)
        y_label = Text("Damage Reduction", font_size=28).next_to(ax.y_axis, LEFT, buff=-1).rotate(PI/2)
        title = Text(
            "Vanilla vs New",
            font_size=36,
            t2c={"Vanilla": BLUE, "New": RED}
        ).to_edge(UP)

        # ---------- Curves ----------
        vg = ax.plot(lambda a: dr_vanilla(a), x_range=[x_min, x_max, 5], use_smoothing=True)
        vg.set_stroke(width=5, color=BLUE)

        xs = np.linspace(x_min, x_max, 800)
        ys = dr_proposed_array(xs)
        def proposed_func(a):
            return float(np.interp(a, xs, ys))
        pg = ax.plot(proposed_func, x_range=[x_min, x_max, 5], use_smoothing=True)
        pg.set_stroke(width=5, color=RED)

        # ---------- Build & Animate ----------
        self.play(Write(title), run_time=1.0)
        self.play(Create(ax), FadeIn(x_label), FadeIn(y_label), run_time=1.5)
        self.play(Create(vg), run_time=1.5)
        self.play(Create(pg), run_time=3.0)
        self.wait(2)
