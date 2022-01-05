# Goal - create a function / class that calculates bending moment and shear capacity
# use function or class to generate a table for a change in d, Ast, f'c etc.

from math import floor, pi, radians, tan
import plotly.express as px
import plotly.graph_objects as go


class Concrete:
    """Class to define a concrete beam and methods for bending and shear capacity calculations."""

    def __init__(
        self,
        D=200,
        b=1000,
        cover=20,
        fc=32,
        diameter=7.6,
        spacing=100,
        ductility="L",
        fsy=500,
        d=None,
    ):
        """Initialization method.

        Parameters
        ----------
        D : int, optional
            Depth of the concrete beam (mm), by default 200
        b : int, optional
            width of the concrete beam (mm), by default 1000
        cover : int, optional
            steel cover (mm), by default 20
        fc : int, optional
            concrete strength (MPa), by default 32
        diameter : float, optional
            diameter of steel reinforcement, by default 7.6
        spacing : int, optional
            spacing of steel reinforcement, by default 100
        ductility : str, optional
            ductility class of steel, by default 'L'
        fsy : int, optional
            yield strength of steel, by default 500
        d : int or None, optional
            depth to center or reinforcement is typically calculated
            by using the beam Depth, cover and reinforcment bar diameter,
            but the value can be overrided by specifying an int here,
            by default None
        """

        # initialise parameters
        self.D = D
        self.b = b
        self.cover = cover
        self.fc = fc
        self.diameter = diameter
        self.spacing = spacing
        self.ductility = ductility
        self.fsy = fsy

        # if d is set than use d, else calculate
        if d:
            self.d = d
        else:
            self.d = D - cover - diameter / 2

        # calculate concrete fctf
        self.fctf = 0.6 * (fc ** 0.5)

        # calculate area of steel in mm2 for the full width
        A_bar = floor(diameter ** 2 * pi / 4)
        self.Ast = A_bar * (b / spacing)

        # calculate concrete stress block parameters
        self.a2 = max(0.85 - 0.0015 * fc, 0.67)
        self.gamma = max(0.97 - 0.0025 * fc, 0.67)


    def plain_concrete_bending(self):
        """Bending capacity calculation based on beam attributes for plain concrete in accordance with AS3600 section 20, section 21.

        Returns
        -------
        Bending Capacity, int
            Bending capacity in kN.m, considers phi.
        """
        # initialise some parameters to be easier to refer to
        D = self.D - 50 #reduce by 50 mm in accordance with AS3600 20.4.1
        fctf = self.fctf
        b = self.b

        # define phi
        phi = 0.6

        # total tensile / compressive force
        F = fctf * b * D/2  

        # calculate moment capacity (without reduction factor)
        # change into kN.m
        Muo = (F * D*2/3) / (10 ** 6)

        # return design bending capacity in kN.m
        return Muo * phi
    
    def plain_concrete_shear(self):
        """Shear capacity calculation based on beam attributes for plain concrete in accordance with AS3600 section 20, section 21.

        Returns
        -------
        Shear Capacity, int
            Shear capacity in kN, considers phi.
        """

        # calcualte parameters needed for shear capacity calculation
        b = self.b
        D = self.D - 50 #reduce by 50 mm in accordance with AS3600 20.4.1
        fc = self.fc

        # define phi
        phi = 0.6

        # calculate shear capacity (without reduction factor)
        # change into kN
        Vu = 0.15* b * D * fc**(1/3) /1000

        # return design shear capacity in kN
        return Vu * phi

    def bending(self):
        """Bending capacity calculation based on beam attributes.

        Returns
        -------
        Bending Capacity, int
            Bending capacity in kN.m, considers phi.
        """
        # initialise some parameters to be easier to refer to
        a2, gamma = self.a2, self.gamma
        fc, Ast, fsy = self.fc, self.Ast, self.fsy
        b, d = self.b, self.d

        # calculate dn
        dn = (Ast * fsy) / (a2 * fc * b * gamma)

        # calculate ku
        ku = dn / d

        # calculate moment capacity (without reduction factor)
        # change into kN.m
        Muo = (Ast * fsy) * (d - 0.5 * gamma * ku * d) / (10 ** 6)

        # use ductility class to determine phi (AS3600)
        if self.ductility in ["l", "L"]:
            phi = 0.65
        elif self.ductility in ["n", "N"]:
            phi = min(max(1.24 - 13 * ku / 12, 0.65), 0.85)
        else:
            phi = 0.65

        # return design bending capacity in kN.m
        return Muo * phi


    def shear(self):
        """Shear capacity calculation based on beam attributes.

        Returns
        -------
        Shear Capacity, int
            Shear capacity in kN, considers phi.
        """
        # initialise some parameters to be shorter to refer to
        d, D, b, fc = self.d, self.D, self.b, self.fc

        # define phi
        phi = 0.7

        # calcualte parameters needed for shear capacity calculation
        # Note thetav and kv simplified
        dv = max(0.72 * D, 0.9 * d)
        bv = b
        thetav = 36
        kv = min(0.1, 200 / (1000 + 1.3 * dv))

        # calculate shear capacity (without reduction factor)
        # change into kN
        Vuc = kv * bv * dv * min(8, fc ** 0.5) / 1000

        # is less than 0.55 * (cot...) ~= 0.25 and sqrt(f'c) < f'c

        # return design shear capacity in kN
        return Vuc * phi * ks

    def deemed(self, f=0.2):
        """Deemed to comply check for crack control and minimum bending capacity.

        Parameters
        ----------
        f : float, optional
            factor for deemed to comply consideration
            is 0.19 for 2 way slab
            is 0.2 for 1 way slab or beam
            is 0.24 for flat slab (slab supported by columns)
            , by default 0.2

        Returns
        -------
        Minimum Steel, int
            Minimum steel for deemed to comply crack control
            and minimum bending capacity requirements (mm2/m)
        """
        # calculate minimum steel for deemed to comply crack control and minimum
        # bending strength in accordance with AS3600 8.1.6.1, 9.1.1, 8.6.1, 9.5.1
        A_min = self.b * self.d * f * (self.D / self.d) ** 2 * self.fctf / self.fsy
        return A_min


if __name__ == "__main__":
    # intialise and empty plotly plot
    fig = px.line()

    # outer loop will represent each line on graph
    for fc in [50, 40, 32, 20]:
        # intilize empty and x and y array to represent data for lines
        x = []
        y = []
        # inner loop will represent all the points on a line
        for D in range(30, 500, 20):
            # create conc class with parameters based on loops and other requirements
            conc = Concrete(D=D, fc=fc)

            # initialise y to be a value created off of the conc class
            # can be conc.deemed(), conc.shear() or conc.bending()
            y.append(conc.bending())

            # intilise x value to be a representation of the inner loop value, either
            # setting it to be the loop value or a related proportional value
            x.append(conc.d)

        # add line with the following code, name will be the name displayed in the legend
        # for the line and should be appropriate defined in relation to the outer loop
        fig.add_trace(go.Scatter(x=x, y=y, name=str(fc) + " MPa"))

    # update title and axes titles for the graph
    fig.update_layout(
        title={"text": "SL81 at varying depth", "x": 0.5},
        title_font_size=24,
        showlegend=True,
        hovermode="x",
    )
    fig.update_xaxes(title_text="d (mm)")
    fig.update_yaxes(title_text="Moment Capacity (kN.m)")

    # show graph
    fig.show()

    # save graph (optional)
    # fig.write_image("./SL81_Bending.png")
    # fig.write_html("./SL81_Bending.html")
