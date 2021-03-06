from scipy.sparse import linalg
import scipy.sparse as sps
import numpy as np
import scipy as sp
import model


class Static:

    """
    Class for linear static analysis.

    Parameters
    ----------
    model: Model
        The model to be analysed.

    Methods
    -------
    submit()
        Submit analysis.
    """

    def __init__(self, model):
        self.model = model

    def submit(self):

        self.stiffness = model.Stiffness(self.model)

        Kff = self.stiffness.getPartitionFF()
        Kfr = self.stiffness.getPartitionFR()
        Krf = self.stiffness.getPartitionRF()
        Krr = self.stiffness.getPartitionRR()

        ndof = list(self.model.ndof.values())
        fdof = list(self.model.fdof.values())
        rdof = list(self.model.rdof.values())

        loads = np.array([load[1] for load in self.model.loads])
        Ff = self.model.Sp.dot(loads)
        Ur = np.zeros(len(rdof))
        Uf = sps.linalg.inv(Kff).dot(Ff-Kfr.dot(Ur))

        self.displacement = np.zeros((len(ndof), 1))
        self.displacement[rdof, 0] = Ur
        self.displacement[fdof, 0] = Uf



class Modal:

    """
    Class for eigenvalue extraction, to calculte natural frequencies and the 
    corresponding mode shapes of an undamped system.

    Parameters
    ----------
    model: Model
        The model to be analysed.

    Attributes
    ----------
    tolerance
        The relative accuracy for eigenvalues.
    sigma
        The sigma value for shift-invert mode.
    numberOfEigenvalues
        The number of eigenvalues to be extracted.
    normalizationMethod
        The mode shapes normalization method.
    returnShapes
        Flag for returning the mode shapes.

    Methods
    -------
    setSigmaValue(sigma)
        Specify the sigma value, near which the eigenvalues are calculated.
    setTolerance(tolerance)
        Specify the relative accuracy for eigenvalues.
    setNumberOfEigenvalues(number)
        Specify the number of eigenvalues to be extracted.
    setNormalizationMethod(method)
        Specify the mode shape normalization method.
    setReturnModeShapes(value)
        Specify if mode shapes are returned in addition to eigenvalues.
    submit()
        Submit analysis.
    """

    def __init__(self, model):

        self.model = model
        self.tolerance = 0
        self.sigma = 0
        self.numberOfEigenvalues = 1
        self.normalizationMethod = 'Mass'
        self.returnModeShapes = True


    def setSigmaValue(self, sigma):

        """
        Specify the sigma value, near which the eigenvalues are calculated
        using shift-invert mode of the "scipy.sparse.linalg.eigsh" algorithm.

        Parameters
        ----------
        sigma: real
            The sigma value.
        """

        if sigma <= 0:
            error = 'Sigma must be positive and non-zero'
            raise TypeError(error)

        self.sigma = sigma


    def setTolerance(self, tolerance):

        """
        Specify the relative accuracy (stopping criterion) for eigenvalues.
        If not specified, a zero value is used by default, which implies
        machine precision.

        Parameters
        ----------
        tolerance: float
            The relative accuracy.
        """

        self.tolerance = tolerance


    def setNumberOfEigenvalues(self, number):

        """
        Specify the number of eigenvalues to be extracted. If not specified, 
        only the first eigenvalue is extracted.

        Parameters
        ----------
        number: int, positive
            The number of eigenvalues.

        Raises
        ------
        TypeError
            If a non-positive number of eigenvalues is specified.
        """

        if number <= 0:
            error = 'Number of Eigenvalues must be positive.'
            raise TypeError(error)

        self.numberOfEigenvalues = number


    def setNormalizationMethod(self, method):

        """
        Specify the mode normalization method.

        Parameters
        ----------
        method: {'displacement', 'mass'}
            The method for mode shapes normalization. 

        Raises
        ------
        TypeError
            If an invalid normalization method is specified.
        """

        if method.lower() not in ['displacement', 'mass']:
            error = 'Normalization method must be either "{}" or "{}".'
            raise TypeError(error.format('Displacement', 'Mass'))

        self.normalizationMethod = method


    def setReturnModeShapes(self, value):

        """
        Specify if mode shapes are returned in addition to eigenvalues.

        Parameters
        ----------
        value: bool
            The flag determining whether mode shapes are extracted or not.

        Raises
        ------
        TypeError
            If value is not a boolean.
        """

        if value not in [True, False]:
            error = 'value should be either "True" or "False".'
            raise TypeError(error)

        self.returnModeShapes = value


    def submit(self):

        stiffness = model.Stiffness(self.model).getPartitionFF()
        mass = model.Mass(self.model).getPartitionFF()

        values = linalg.eigsh(stiffness, k=self.numberOfEigenvalues,
                M=mass, sigma=self.sigma, tol=self.tolerance,
                return_eigenvectors=self.returnModeShapes)

        if self.returnModeShapes:
            values, vectors = values[0], values[1]

            if np.any(values<0):
                index = np.where(values>=0)
                values, vectors = values[index[0]], vectors[:, index[0]]

                warning = '{} negative values found.\n'
                syst.stdout.write(warning.format(str(len(index[0]))))

            if self.normalizationMethod == 'Mass':
                for vector in vectors.T:
                    scaling = np.sqrt(vector.dot(mass.toarray().dot(vector)))
                    vector /= scaling
            else:
                scaling = np.max(np.abs(vectors), 0)
                vectors /= scaling

            # check if vectors has more than one columns.
            # If not, vectors.shape[1] will raise an error
            self.modes = np.zeros((len(self.model.ndof), vectors.shape[1]))
            self.modes[list(self.model.fdof.values()), :] = vectors
            self.modes[list(self.model.rdof.values()), :] = 0
        else:
            self.modes = None
            if np.any(values<0):
                index = np.where(values>=0)
                values = values[index[0]]

                warning = '{} negative values found.\n'
                syst.stdout.write(warning.format(str(len(index[0]))))

        self.frequencies = np.sqrt(values)/(2*np.pi)



class Dynamics(object):

    """
    Class for dynamic analysis, to calculate the time response of a system
    subjected to dynamic loads, using Newmark scheme.

    Parameters
    ----------
    model: Model
        The model to be analysed.

    Methods
    -------
    setTimePeriod(period)
        Specify the simulation time period.
    setIncrementSize(size)
        Specify the solution time increment.
    submit()
        Submit analysis.
    """


    def __init__(self, model):
        self.model = model
        self.timePeriod = 1
        self.incrementSize = 0.1


    def setTimePeriod(self, period):

        """
        Specify the simulation time period.

        Parameters
        ----------
        period: float, positive
            The simulation time period.

        Raises
        ------
        TypeError
            If period is not positive.
        """

        if period <= 0:
            raise TypeError('Time period must be positive.')

        self.timePeriod = period


    def setIncrementSize(self, size):

        """
        Specify the solution increment size.

        Parameters
        ----------
        size: float, positive
            The increment size.

        Raises
        ------
        TypeError
            If the increment size is not positive.
        """

        if size <= 0:
            raise TypeError('Increment size must be positive.')

        self.incrementSize = size




    def submit(self):

        modal = Modal(self.model)
        modal.setNumberOfEigenvalues(10)
        modal.submit()

        frequencies = modal.frequencies
        modes = modal.modes

        beta, gamma = 1/6, 1/2
        period, step = self.timePeriod, self.incrementSize

        if step > 0.1*(1/frequencies[-1]):
            step = 0.1*(1/frequencies[-1])

        time = np.arange(0, period+step, step)


        a, b = self.model.alpha, self.model.beta
        damping = a*1/(4*np.pi*frequencies)+b*np.pi*frequencies

        dsp = np.zeros((len(frequencies), len(time)))
        vlc = np.zeros((len(frequencies), len(time)))
        acc = np.zeros((len(frequencies), len(time)))

        K = (np.diag(frequencies)*2*np.pi)**2
        C = np.diag(frequencies)*2*np.pi*2*damping
        M = np.eye(len(frequencies))

        #  Construct modal force vector

        loads = np.zeros((len(self.model.loads), len(time)))

        for i, load in enumerate(self.model.loads):
            loads[i] = np.interp(time, load[0], load[1])

        frc = modes.T.dot(self.model.Sp).dot(loads)

        efrc = -C.dot(vlc[:, 0])-K.dot(dsp[:, 0])
        acc[:, 0] = np.linalg.solve(M, frc[:, 0]+efrc)

        a1 = 1/(beta*step**2)*M+gamma/(beta*step)*C
        a2 = 1/(beta*step)*M+(gamma/beta-1)*C
        a3 = (1/(2*beta)-1)*M+step*(gamma/(2*beta)-1)*C
        Ki = np.linalg.inv(K+a1)

        c1 = gamma/(beta*step)
        c2 = 1-gamma/beta
        c3 = step*(1-gamma/(2*beta))
        c4 = 1/(beta*step**2)
        c5 = -1/(beta*step)
        c6 = -(1/(2*beta)-1)

        for j in range(len(time)-1):

            efrc = a1.dot(dsp[:, j])+a2.dot(vlc[:, j])+a3.dot(acc[:, j])
            dsp[:, j+1] = Ki.dot(frc[:, j+1]+efrc)

            vlc[:, j+1] = c1*(dsp[:, j+1]-dsp[:, j])+c2*vlc[:, j]+c3*acc[:, j]
            acc[:, j+1] = c4*(dsp[:, j+1]-dsp[:, j])+c5*vlc[:, j]+c6*acc[:, j]

        self.modes = modes
        self.frequencies = frequencies

        self.time = time
        self.displacement = dsp
        self.velocity = vlc
        self.acceleration = acc
