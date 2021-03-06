from manimlib import *
from helpers import *

class Tensor(Scene):
    """
    Displays tensor multiplication (Kronecker product) of two arbitrary 2x2 matrices
    """
    def construct(self):
        self.camera.frame.shift(2 * OUT)

        # Initial matrices
        A = Matrix(
            [["a_{11}", "a_{12}"],
             ["a_{21}", "a_{22}"]]
        )

        B = Matrix(
            [["b_{11}", "b_{12}"],
             ["b_{21}", "b_{22}"]]
        )

        tens = Tex("\\otimes")

        A.get_entries().set_color(GREEN)
        B.get_entries().set_color(BLUE)

        lhs = VGroup(A, tens, B)
        lhs.arrange(RIGHT)

        eq = Tex("=")

        # Create primitive of rhs Matrix
        rhsMatrixP = [ [], [] ]

        # Create copies of elements in first two matrices
        #  and use them to populate rhsMatrixP
        for (i, j) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            a = A.get_entries()[2*i+j].copy()
            b = B.copy()
            vg = VGroup(a, b)
            vg.arrange(RIGHT)
            rhsMatrixP[i].insert(j, vg)

        rhsMatrix = Matrix(rhsMatrixP, element_to_mobject=(lambda m: m), v_buff=2, h_buff=3.8)

        equation = VGroup(lhs, eq, rhsMatrix)
        equation.arrange(RIGHT)

        # Initial write animation
        writeLHS = AnimationGroup(
                WriteMatrix(A),
                Write(tens),
                WriteMatrix(B),
                Write(eq),
                Write(rhsMatrix.get_brackets()[0]),
                Write(rhsMatrix.get_brackets()[1]),
                lag_ratio=0.1
            ) 

        self.play(
            writeLHS
        )

        # Animation of the 4 copies of B
        Btrans = [
            TransformFromCopy(B, en[1], replace_mobject_with_target_in_scene=True)
            for en in rhsMatrix.get_entries()
        ]
        # Animation of the entries of A
        Atrans = [
            TransformFromCopy(A.get_entries()[i], an, path_arc=(math.pow(-1, math.floor((i + 2)/4)) * 0.5), replace_mobject_with_target_in_scene=True)
            for i, an in enumerate(map(lambda en: en[0], rhsMatrix.get_entries()))
        ]

        # Animate rhsMatrix's creation
        self.play(
            AnimationGroup(
                AnimationGroup(
                    *Btrans,
                    lag_ratio=0.1,
                ),
                AnimationGroup(
                    *Atrans,
                    lag_ratio=0.4
                ),
                lag_ratio=0.5
            )
        )
        
        self.add(rhsMatrix.get_entries())

        # Distribute the as
        Atrans2 = [ ]

        # We must keep a copy of the final entries as a workaround
        #  for the Matrix class, which does not do deep copies properly
        #  so, we must keep our own copies of necessary entries
        als = [ ]
        final_ = [ ]

        # Setup animation for distributing the a_i
        for en in rhsMatrix.get_entries():
            a = en[0]
            for brow in en[1][:1]:
                for ben in brow:
                    ac = a.copy()
                    # Keep copy of new a for later
                    als.append(ac)
                    # Put copy of a next to entry of b in nested matrix
                    ac.next_to(ben, LEFT, 0.05)
                    ben.add(ac)
                    # Keep copy of entry of b for later
                    final_.append(ben)
                    # Hide copy of a so it may be added back later
                    self.remove(ac)
                    Atrans2.append(TransformFromCopy(a, ac, replace_mobject_with_target_in_scene=True))

        # Distribute the a's and reposition entries
        self.play(
            *Atrans2,
            *( FadeOut(x) for x in map(lambda el: el[0], rhsMatrix.get_entries()) ),
            *( x.animate.shift((A[0][0].get_width() + 0.02) * LEFT) for x in map(lambda el: el[1][1], rhsMatrix.get_entries()) )
        )

        self.add(*als)

        ent = rhsMatrix.get_entries()

        # Map from nested matrices to outer matrix
        final_matrix = [
            [ ent[0][1][0][0], ent[0][1][0][1], ent[1][1][0][0], ent[1][1][0][1] ],
            [ ent[0][1][0][2], ent[0][1][0][3], ent[1][1][0][2], ent[1][1][0][3] ],
            [ ent[2][1][0][0], ent[2][1][0][1], ent[3][1][0][0], ent[3][1][0][1] ],
            [ ent[2][1][0][2], ent[2][1][0][3], ent[3][1][0][2], ent[3][1][0][3] ],
        ]

        # Positioning guides
        ul = ent[0][1][0][0].get_corner(UL)
        dhor  = ent[1][1][0][1].get_corner(UL) - ul
        dvert = ent[2][1][0][2].get_corner(UL) - ul

        dhor *= 1.0/3
        dvert *= 1.0/3

        final_anim = [ ]

        # Create evenly spaced grid out of entries
        for j, row in enumerate(final_matrix):
            for i, en in enumerate(row):
                final_anim.append(en.animate.move_to( ul + dhor * i + dvert * j, UL ))

        block = VGroup(*final_)

        self.play(
            # Fade out the inner brackets
            *(FadeOut(c) for c in [ent[0][1][2], ent[0][1][1], 
                                   ent[1][1][2], ent[1][1][1],
                                   ent[2][1][2], ent[2][1][1], 
                                   ent[3][1][2], ent[3][1][1]]),
            *final_anim,
        )

        lshift = 0.6

        # Reposition brackets
        self.play(
            block.animate.shift(LEFT * (lshift-0.1)),
            rhsMatrix.get_brackets()[1].animate.shift(LEFT * lshift)
        )

        self.wait(1)

class Cardiod(Scene):
    """ 
    Animation of a cardiod as a rolling curve (epicycloid) and its equation
    """
    def construct(self):
        ANIM_TIME = 8
        DOT_RADIUS = 0.04
        CURVE_COLOR = BLUE
        INNER_COLOR = RED
        OUTER_COLOR = GREEN
        STROKE_WIDTH = 2
        SAMPLES = 0.05

        # Curve axes, used as reference coordinates
        axes = Axes(x_range = (-2, 2), y_range = (-2, 2), width=4, height=4)

        # Cardoid function
        def func(t):
            return (2*math.cos(t)-math.cos(2*t), 2*math.sin(t)-math.sin(2*t), 0)
        
        # Cardiod function fitted to axes
        def cfunc(t): return axes.c2p(*func(t))

        t = ValueTracker(0)

        # Determine what range of values to draw of the cardiod for a given time t

        def t_min(t):
            if t >= 2*PI:
                return min(t - (2 * PI), 2*PI)
            else:
                return 0

        def t_max(t):
            if t <= 2*PI:
                return t
            else:
                return 2*PI


        cardiod = always_redraw(lambda: 
            ParametricCurve(lambda t: axes.c2p(*func(t)),
            t_range=[t_min(t.get_value()), t_max(t.get_value()), SAMPLES],
            color=CURVE_COLOR,
            stroke_width=STROKE_WIDTH )
        )
        
        t.add_updater(lambda m, dt: m.increment_value(dt * 4 * PI / ANIM_TIME))

        self.add(t)
        axes.center()
        
        ### Circles ###
        trace = Dot(radius=DOT_RADIUS, color=CURVE_COLOR)
        trace.add_updater(lambda m: m.shift(cfunc(t.get_value()) - m.get_center()))

        outer_circ = Circle( stroke_width=STROKE_WIDTH, radius=1 )
        outer_circ.add_updater(lambda m: m.shift(axes.c2p(2*math.cos(t.get_value()), 2*math.sin(t.get_value()), 0) - m.get_center()))
        outer_circ.add_updater(lambda m: m.set_width( 2*(axes.c2p(1, 0, 0) - axes.c2p(0, 0, 0))[0] ))
        outer_circ.set_color(WHITE)

        outer_circ_origin = Dot(radius=DOT_RADIUS)
        outer_circ_origin.add_updater(lambda m: m.shift(outer_circ.get_center() - m.get_center()))

        inner_circ = Circle( stroke_width=STROKE_WIDTH, radius=1 )
        inner_circ.add_updater(lambda m: m.shift(axes.get_origin() - m.get_center()))
        inner_circ.add_updater(lambda m: m.set_width( 2*(axes.c2p(1, 0, 0) - axes.c2p(0, 0, 0))[0] ))
        inner_circ.set_color(WHITE)

        inner_circ_origin = Dot(radius=DOT_RADIUS)
        inner_circ_origin.add_updater(lambda m: m.shift(inner_circ.get_center() - m.get_center()))

        dashed_circ = DashedVMobject(ParametricCurve(lambda t2: axes.c2p(2*math.cos(t2), 2*math.sin(t2), 0), [0, 2*PI, SAMPLES], stroke_width=STROKE_WIDTH),
            num_dashes=40)

        ### Lines ###
        inner_line = always_redraw(lambda: Line(start=axes.get_origin(), end=outer_circ.get_center(), stroke_width=STROKE_WIDTH, color=INNER_COLOR))
        outer_line = always_redraw(lambda: Line(start=outer_circ.get_center(), end=cfunc(t.get_value()), stroke_width=STROKE_WIDTH, color=OUTER_COLOR))

        ### Colors ###
        outer_circ_origin.set_color(OUTER_COLOR)
        inner_circ_origin.set_color(INNER_COLOR)

        # Add to scene
        curve_content = VGroup(cardiod,  outer_circ, inner_circ, inner_line, outer_line, outer_circ_origin, inner_circ_origin, trace)
        self.add(curve_content)

        kw = {
            "tex_to_color_map": {
                "{t}": GREY_B,
            }
        }

        eq = VGroup(
            Tex("x(t) = (2 \\cos{{t}} - \\cos{{2 t}})", isolate=["2 \\cos{{t}}", "\\cos{{2 t}}"]),
            Tex("y(t) = (2 \\sin{{t}} - \\sin{{2 t}})", isolate=["2 \\sin{{t}}", "\\sin{{2 t}}"]),
            
        )

        eq_x1 = eq[0][1]
        eq_x2 = eq[0][3]
        eq_y1 = eq[1][1]
        eq_y2 = eq[1][3]

        # set equation colors
        eq_x1.set_color(INNER_COLOR)
        eq_y1.set_color(INNER_COLOR)
        eq_x2.set_color(OUTER_COLOR)
        eq_y2.set_color(OUTER_COLOR)

        eq.arrange(DOWN * 1.5)
        eq.set_width(0.9*eq.get_width())

        self.add(eq)

        content = VGroup(VGroup(axes, curve_content), eq)
        content.arrange(RIGHT*2)
        content.center()
        content.shift(RIGHT*0.2)

        ### ANIMATION ###

        # total run-time
        rt = ANIM_TIME
        arc = 1

        art = rt/4 + 1/30
        self.wait(art)

        self.play(
            TransformFromCopy(inner_line, eq_x1.copy(), run_time=art, path_arc=arc),
            TransformFromCopy(inner_line, eq_y1.copy(), run_time=art, path_arc=-arc)
        )

        self.play(
            TransformFromCopy(outer_line, eq_x2.copy(), run_time=art, path_arc=arc),
            TransformFromCopy(outer_line, eq_y2.copy(), run_time=art, path_arc=-arc)
        )
        self.wait(rt/4)

from math import pow, sin, cos, log, sqrt
from numpy.linalg import norm

class Partial(Scene):
    """ 
    Demonstration of partial derivatives on two surfaces (a function R^2 -> R^2)
    """
    def construct(self):
        F1_COLOR = GREEN
        F2_COLOR = BLUE
        X_COLOR = GREY_B
        Y_COLOR = GREY_B
        POINT_RADIUS = 0.05
        ARR_THICKNESS = 0.04
        ARR_TIP_RATIO = 4
        ARR_LENGTH_FAC = 0.5
        SURFACE_ROT_TIME = 20
        CURVE_TRACE_TIME = 10
        ANG_FORWARDS = PI/2 - PI/6
        ANIM_TIME = SURFACE_ROT_TIME

        # demonstrated function
        def f(x, y):
            return (sin(sqrt(pow(2*x, 2)+pow(2*y, 2))), pow(x/2, 2) - pow(y/2, 2))

        # total derivative (jacobian) of f
        def jacf(x, y):
            return [
                [ (2*x*cos(2*sqrt(pow(x, 2)+pow(y, 2))))/sqrt(pow(x, 2)+pow(y, 2)), (2*y*cos(2*sqrt(pow(x, 2)+pow(y, 2))))/sqrt(pow(x, 2)+pow(y, 2)) ],
                [  x/2, -y/2 ]
            ]

        # gives an array of tangent vectors of f at point (x, y)
        def tanVecsf(x, y):
            d = jacf(x, y)
            vecs = [ ( 1, 0, d[0][0] ), ( 0, 1, d[0][1] ), ( 1, 0, d[1][0] ), ( 0, 1, d[1][1] ) ]
            return list(map(lambda v: np.array(v) * (1/norm(v)) * ARR_LENGTH_FAC, vecs))

        # parametrization of surface f
        def func(u, v):
            return (( u, v, f(u, v)[0] ), (u, v, f(u, v)[1]))
        
        def func1(u, v): return func(u, v)[0]
        def func2(u, v): return func(u, v)[1]
        
        # path to trace out (clover)
        path = lambda t: ((1.4 + cos(3*t))*cos(t), (1.4 + cos(3*t))*sin(t))

        t_val = ValueTracker(0)
        t = lambda: t_val.get_value() 
        self.add(t_val)

        ### Surfaces ###
        ran = [-3, 3, 1]

        axeskw = { "x_range":ran, "y_range":ran, "z_range":ran }
        surfacekw = { "u_range":ran[:2], "v_range":ran[:2] }
        pointkw = { "radius":POINT_RADIUS }
        veckw = { "thickness":ARR_THICKNESS," tip_width_ratio":ARR_TIP_RATIO }
        vecxkw = { }
        vecykw = { }

        ### f_1 ###
        axes1 = ThreeDAxes(**axeskw)
        surface1 = ParametricSurface(lambda u, v: axes1.c2p(*func1(u, v)), **surfacekw, color=F1_COLOR)
        
        point1 = Sphere(color=F1_COLOR, **pointkw)
        point1.add_updater(lambda m: m.shift(axes1.c2p(*func1(*path(t()))) - m.get_center()))

        vec1x = Vector(**veckw, **vecxkw)
        vec1x.add_updater(lambda m: m.set_points_by_ends(axes1.c2p(*func1(*path(t()))), axes1.c2p(*(np.array(func1(*path(t()))) + tanVecsf(*path(t()))[0]))))
        vec1y = Vector(**veckw, **vecykw)
        vec1y.add_updater(lambda m: m.set_points_by_ends(axes1.c2p(*func1(*path(t()))), axes1.c2p(*(np.array(func1(*path(t()))) + tanVecsf(*path(t()))[1]))))
        
        graph1 = Group(surface1,axes1,  vec1x, vec1y, point1,)

        ### f_2 ###
        axes2 = ThreeDAxes(**axeskw)
        surface2 = ParametricSurface(lambda u, v: axes2.c2p(*func2(u, v)), **surfacekw, color=F2_COLOR)
        
        point2 = Sphere(color=F2_COLOR, **pointkw)
        point2.add_updater(lambda m: m.shift(axes2.c2p(*func2(*path(t()))) - m.get_center()))

        vec2x = Vector(**veckw, **vecxkw)
        vec2x.add_updater(lambda m: m.set_points_by_ends(axes2.c2p(*func2(*path(t()))), axes2.c2p(*(np.array(func2(*path(t()))) + tanVecsf(*path(t()))[2]))))
        vec2y = Vector(**veckw, **vecykw)
        vec2y.add_updater(lambda m: m.set_points_by_ends(axes2.c2p(*func2(*path(t()))), axes2.c2p(*(np.array(func2(*path(t()))) + tanVecsf(*path(t()))[3]))))
        
        graph2 = Group(surface2,axes2,  vec2x, vec2y, point2,)

        ### Top Equation ###
        f1tex = "\\sin{{\\sqrt{{x^2 + y^2}}}}"
        f2tex = "x^2 - y^2"
        feq = Tex("f({{x}}, {{y}}) = ({}, {})".format(f1tex, f2tex), tex_to_color_map={ "{{x}}":X_COLOR, "{{y}}":Y_COLOR, f1tex:F1_COLOR, f2tex:F2_COLOR })

        feq.to_corner(UL, 1)
        feq.shift(RIGHT * 0.7)
        self.add(feq)

        # Graph Labels
        f1label = Tex("f_1", color=F1_COLOR)
        f2label = Tex("f_2", color=F2_COLOR)
        self.add(f1label, f2label)

        ### Matrix ###
        jaclhs = Tex("\Delta_{f} = ")
        jacmatrix = Matrix([
            ["""{\\partial f_1} \\over {\\partial x}""", """{\\partial f_1} \\over {\\partial y}"""],
            ["""{\\partial f_2} \\over {\\partial x}""", """{\\partial f_2} \\over {\\partial y}"""]
        ], element_to_mobject_config={ "isolate":["f_1", "f_2"] } , v_buff=1.2)
        jacfracs = [ ]
        for i, ent in enumerate(jacmatrix.get_entries()):
            ent[1].set_color({0:F1_COLOR, 1:F1_COLOR, 2:F2_COLOR, 3:F2_COLOR}[i])
            jacfracs.append( (ent[1], ent[2][2]) )
        jaceq = VGroup(jaclhs, jacmatrix)
        jaceq.arrange(RIGHT)
        jaceq.to_edge(RIGHT)
        self.add(jaceq)

        ### Animation ###

        RotateAxes(graph1, axes2, ANG_FORWARDS, LEFT)
        RotateAxes(graph2, axes1, ANG_FORWARDS, LEFT)

        # Spins 3d graphs at constant rate
        rot_updater = lambda ax: (lambda m, dt: RotateAxes(m, ax, dt * 2*PI/SURFACE_ROT_TIME, OUT) )

        graph1.add_updater(rot_updater(axes1))
        graph2.add_updater(rot_updater(axes2))

        graphs = Group(graph1, graph2)
        for graph in graphs: graph.scale(0.5)
        graphs.arrange(RIGHT * 6)

        graphs.to_corner(DL, 1.5)
        graphs.shift(UP * 0.5 + LEFT * 0.5)
        f1label.next_to(graph1, DOWN*1.5)
        f2label.next_to(graph2, DOWN*1.5)

        self.add(graphs)

        t_val.add_updater(lambda m, dt: m.increment_value(dt*2*PI*(1/CURVE_TRACE_TIME)))

        for i in range(0, 4):
            time = ANIM_TIME/4
            trans_time = 2
            wait_time = time - trans_time
            
            wait_time += 1/30
            if i < 3: trans_time += 1/30 

            self.wait(wait_time)
            animargs = { "replace_mobject_with_target_in_scene":True, "run_time":trans_time }
            self.play(
                FadeTransform(([f1label, f1label, f2label, f2label])[i].copy(), jacfracs[i][0], **animargs),
                FadeTransform(([vec1x, vec1y, vec2x, vec2y])[i].copy(), jacfracs[i][1], **animargs),
                run_time=trans_time
            )