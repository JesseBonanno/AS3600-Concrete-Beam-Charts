# Goal - create a function / class that calculates bending moment and shear capacity
# use function or class to generate a table for a change in d, Ast, f'c etc.

from math import floor, pi
import plotly.express as px
import plotly.graph_objects as go

class Concrete:
    """Class to define a concrete beam and methods for bending and shear capacity calculations.
    """

    def __init__(self,D=200, b = 1000, cover = 20, fc = 32, diameter = 7.6, spacing = 100, ductility = 'L', fsy = 500, d = None):
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

        self.D = D
        self.b = b
        self.cover = cover
        self.fc = fc
        self.diameter = diameter
        self.spacing = spacing
        self.ductility = ductility
        self.fsy = fsy
        
        if d:
            self.d = d
        else:
            self.d = D - cover - diameter/2

        self.fctf = 0.6*(fc**0.5)

        A_bar = floor(diameter**2 * pi /4)
        self.Ast = A_bar * (b / spacing)

        self.a2 = max(0.85-0.0015*fc,0.67)
        self.gamma = max(0.97-0.0025*fc,0.67)


    def bending(self):
        """Bending capacity calculation based on beam attributes.

        Returns
        -------
        Bending Capacity, int
            Bending capacity in kN.m, considers phi.
        """
        a2, gamma = self.a2, self.gamma
        fc, Ast, fsy = self.fc, self.Ast, self.fsy
        b,d = self.b, self.d
        dn = (Ast * fsy) / (a2*fc*b*gamma)
        ku = dn / d
        Muo = (Ast * fsy) * (d - 0.5*gamma*ku*d) /(10**6)

        if self.ductility in ['l','L']:
            phi = 0.65
        elif self.ductility in ['n','N']:
            phi = min(max(1.24 - 13 * ku /12,0.65),0.85)      
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
        phi = 0.75
        dv = max(0.72 * self.D, 0.9 * self.d)
        bv = self.b
        thetav = 36
        kv = min(0.1, 200/(1000+1.3*dv))
        Vuc = kv * bv * dv * min(8, self.fc**0.5) / 1000

        # return design shear capacity in kN
        return Vuc * phi

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
        # f is the factor for different members
        # 0.19 for 2 way slab
        # 0.2 for 1 way slab
        # 0.24 for flat slab (supported by columns)
        A_min = self.b * self.d * f * (self.D/self.d)**2 * self.fctf/self.fsy
        return A_min



if __name__ == "__main__":
    # loop through depths at 10 mm increments
    fig = px.line()

    x, y = {}, {}
    for cover in range(20,80,5):
        x[cover] = []
        y[cover] = []
        for D in range(60,750,10):
            conc = Concrete(D = D, fc = 32, ductility='N', cover = cover, diameter = 10)
            y[cover].append(conc.deemed())
            x[cover].append(conc.D)

        fig.add_trace(go.Scatter(x=x[cover],y=y[cover], name = str("d = D - "+ str(cover+5))))

    fig.update_layout(
            title={'text': "Deemed to comply (where fc = 32 MPa)", 'x': 0.5},
            title_font_size=24,
            showlegend=True,
            hovermode='x')
    fig.update_xaxes(title_text='Depth, D (mm)')
    fig.update_yaxes(title_text='Min Ast (mm2/m))')

    fig.show()
    fig.write_image("./deemed_f32.png")
    fig.write_html("./deemed_f32.html")
