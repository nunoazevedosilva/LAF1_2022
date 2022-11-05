import numpy as np
from scipy import sparse, stats
from scipy.stats import t
from scipy.sparse.linalg import spsolve
from scipy import special
from scipy import optimize 
from scipy.signal import savgol_filter
from fundamental_constants import *
from sklearn import linear_model 
import matplotlib.ticker as ticker
from matplotlib.pyplot import *

def voigt_profile_binder(x,x0, A, sigma, gamma):
    return A*special.voigt_profile(x-x0,sigma, gamma)
    
    
def voigt_fit(x,y,initial_guess_x0 = 1,initial_guess_A=1):
    
    return optimize.curve_fit(voigt_profile_binder, x, y,p0=[initial_guess_x0,initial_guess_A,1,1])


def voigt_fwhm(x,params):
    y = voigt_profile_binder(x,params[0],params[1],params[2],params[3])
    d = y - (np.max(y) / 2) 
    indexes = where(d > 0)[0] 
    return np.abs(x[indexes[-1]] - x[indexes[0]]),[x[indexes[0]],x[indexes[-1]]],[y[indexes[0]],y[indexes[-1]]]

def lorentzian_profile_binder(x,x0, A, sigma, gamma):
    """ Return Lorentzian line shape at x with HWHM gamma """
    return A* gamma / pi / ((x-x0)**2 + gamma**2)

def gaussian_profile_binder(x,x0, A, sigma, gamma):
    """ Return Gaussian line shape at x with HWHM sigma """
    return A*np.sqrt(log(2) / pi) / sigma* exp(-((x-x0) / sigma)**2 * log(2))


def binder_fit(x,y, binder, initial_guess_x0 = 1, initial_guess_A = 1):

    return optimize.curve_fit(binder, x, y,p0=[initial_guess_x0,initial_guess_A,1,1])

def fit_fwhm(x,params,binder):
    y = binder(x,params[0],params[1],params[2],params[3])
    d = y - (max(y) / 2) 
    indexes = np.where(d > 0)[0] 
    return abs(x[indexes[-1]] - x[indexes[0]]),[x[indexes[0]],x[indexes[-1]]],[y[indexes[0]],y[indexes[-1]]]

def baseline_als(y, lam, p, niter=10):
    L = len(y)
    D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
    w = np.ones(L)
    for i in range(niter):
        W = sparse.spdiags(w, 0, L, L)
        Z = W + lam * D.dot(D.transpose())
        z = spsolve(Z, w*y)
        w = p * (y > z) + (1-p) * (y < z)
    return z


def density_H_alpha(wl,sp,fit="Voigt",Plot=True, compare_methods = False,ratio_max=0.8,baseline_rem=True):


    line_ritz = 656.3
    new_wavelengths = wl
    new_spectrum = np.copy(sp)
    if baseline_rem:
        new_spectrum += -baseline_als(new_spectrum,100000,0.05)
    ##not correct##
    radius=0.3
    center_wavelength_peak_index = get_closest_peak_index(line_ritz, radius, new_wavelengths, new_spectrum)
    index_lr = get_closest_peak_width_index(center_wavelength_peak_index,ratio_max, new_wavelengths, new_spectrum)

    if compare_methods==False:
        if fit == "Voigt":
            current_profile_binder = voigt_profile_binder
        elif fit == "Gaussian":
            current_profile_binder = gaussian_profile_binder
        else:
            current_profile_binder = lorentzian_profile_binder

        params, pcov = binder_fit(new_wavelengths[index_lr[0]:index_lr[1]], new_spectrum[index_lr[0]:index_lr[1]],
                                 current_profile_binder,
                                 initial_guess_x0 = line_ritz, initial_guess_A = new_spectrum[center_wavelength_peak_index])

        xx = np.arange(new_wavelengths[index_lr[0]],new_wavelengths[index_lr[1]],0.001)
        fwhm, fwhm_x_v, fwhm_y_v = fit_fwhm(xx,params,current_profile_binder)

        #density = 10e17*pow(fwhm/1.31,1/0.64)
        #density = 9.77e16*pow(fwhm,1.39)
        density = (fwhm/(2.8*10**-17))**(1/0.72)*10**-6
        
        if Plot:
            subplots()
            title(r'$H_{\alpha}$ line fit',fontsize=12)
            plot(new_wavelengths[index_lr[0]:index_lr[1]],new_spectrum[index_lr[0]:index_lr[1]],'-',marker = 'o', lw=0.5,color='k',label='Signal')
            fill_between(xx,current_profile_binder(xx,params[0],params[1],params[2],params[3]),color='b',alpha=0.2,label=fit+' fit')
            plot(fwhm_x_v,fwhm_y_v,ls = ':', color = 'k', marker = '|',markersize = 10)
            ax = gca()
            ax.text(0.3, 0.2,  '$n_{plasma} =$' + "%1.2e" % density +' $cm^{-3}$',
            transform=ax.transAxes,fontsize=12, bbox={'boxstyle':'round', 'facecolor': 'wheat', 'alpha': 0.5, 'pad': 0.5})
            ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
            legend(fontsize=12)


        return density, new_wavelengths[index_lr[0]:index_lr[1]], new_spectrum[index_lr[0]:index_lr[1]], params

def get_plasma_density(wl,signal,Plot=True):
    try:
        density = density_H_alpha(wl,signal,fit='Voigt',Plot=Plot, compare_methods = False,
                     ratio_max=0.1,baseline_rem=True)
        return (1e-16)*density[0]
    except:
        print('H alpha line not found')
        return None
    
def plasma_reduction_energy_factor(n_e, T):
    return (e_c**2/(4*np.pi*eps_0))*np.sqrt(e_c**2*n_e/(eps_0*kb_si*T))*6.24150913*10**18


def saha_boltzmann_temperature_new(lines, ion_energies , wavelengths, spectrum, ratio_of_maximum = 0.5, radius = 1, guess_temperature = T_ref,
                          Plot = True, electron_density=n_e_ref, Title = "Saha-Boltzmann plot", Plotlines = False, use_max_intensity = False):
    
    #log(I/(gj*Aij))
    y_s = []
    
    #log(Ej)
    x_s = []
    
    ##################################
    #auxiliary variables to plot
    
    #plasma_reduction_energy_factor
    energy_correction = plasma_reduction_energy_factor(electron_density, T_ref)

    
    plot_y = len(lines)
    plot_x = max([len(lines_ion) for lines_ion in lines])
    
    if Plotlines:
        fig1,ax = subplots(plot_y,plot_x,figsize=(plot_x*3,plot_y*3))
    else:
        fig1 = None
    ##################################
    
    ion_plot_lines=0
    for lines_ion in lines:
        
        index_plot=ion_plot_lines*plot_x+1
        
        for line_i in lines_ion:
            ritz = line_i[0]
            g_j = line_i[1]
            A_ji = line_i[2]
            ion_state = line_i[3]
            llabel = line_i[4]
            e_upper = line_i[5]
                
                
            if use_max_intensity:
                
                index_max = get_closest_peak_index(ritz, radius, wavelengths, spectrum)
                if index_max != None:
                    intensity = spectrum[index_max]
                    y0 = np.log(intensity/(g_j*A_ji))-(ion_state
                                                                      -1)*np.log(2*(2*pi*m_e*kb_si*guess_temperature)**(3/2.)/h**3/electron_density)
                    y_s.append(y0)
            
                    energy = line_i.e_upper+ion_energies[0:int(line_i.ion_state)-1].sum()
                    x_s.append(energy-energy_correction)
                
                else:
                    print( " *** Warning - line " + str(line_i.ritz)+ " for " + line_i.label +" " + str(int(line_i.ion_state)) +  " not found within the given range")


            else:
                try:
                    intensity = get_peak_area(ritz, ratio_of_maximum, wavelengths, spectrum, radius, Plotlines, 
                                              str(llabel + ' ' + str(int(ion_state))+ ' - ' + str(ritz)),
                                              fig = fig1, subp =[plot_y,plot_x,index_plot] )
                except:
                    intensity = None

                
                if intensity != None:
                    #print(intensity)
                    intensity=abs(intensity)
                    
                    ####################
                    #y0 = np.log(intensity/(line_i.g_j*line_i.A_ji))-(line_i.ion_state
                     #                                                     -1)*np.log(2*(2*pi*m_e*kb_si*guess_temperature)**(3/2.)/h**3/electron_density)
                    
                    y0 = np.log(intensity*ritz/(g_j*A_ji))-(ion_state-1)*np.log(2*(2*np.pi*m_e*kb_si*guess_temperature)**(3/2.)/h**3/electron_density)
                    
                    ################
                    y_s.append(y0)
                
                    energy = e_upper+ion_energies[0:int(ion_state)-1].sum()
                    x_s.append(energy-energy_correction)
                else:
                    print( " *** Warning - line " + str(ritz)+ " for " + llabel +" " + str(int(ion_state)) +  " not found within the given range")
            
            index_plot += 1
            
        ion_plot_lines+=1
    
    y_s=np.array(y_s)
    x_s=np.array(x_s)
        
    
    regressor = linear_model.LinearRegression()
        
    x_train=x_s.reshape(len(x_s),1)
    y_train=y_s.reshape(len(y_s),1)
    regressor.fit(x_train, y_train)
        
    r2=regressor.score(x_train,y_train)
    slope = regressor.coef_[0][0]
    temperature=-1./(kb*slope)
    tev=temperature/T_ref
    
    result = stats.linregress(x_train[:,0],y_train[:,0])
        
    tinv = lambda p, df: abs(t.ppf(p/2, df))
    ts = tinv(0.05, len(x_s)-2)
    slope_95 = ts*result.stderr
    temp_95 = (slope_95/slope)*temperature
    temp_95_ev = (slope_95/slope)*tev
    
    if Plot:
        fig,ax = subplots(figsize=(5,3),constrained_layout=True)
        
        ax.set_title(Title)
        ax.plot(x_s,y_s,'o', fillstyle = 'none',ls='none',color = 'k')
        

        
        ax.plot(sorted(x_train),regressor.predict(sorted(x_train)),ls='--',color='k')
        
        #prediction bands
        N = x_s.size
        var_n = 2
        alpha = 1.0 - 0.95 #conf
        q = t.ppf(1.0 - alpha / 2.0, N - var_n)
        # Stdev of an individual measurement
        se = result.stderr
        sx = (x_s - x_s.mean()) ** 2
        sxd = np.sum((x_s - x_s.mean()) ** 2)
        dy = q * se * np.sqrt(1.0+ (1.0/N) + (sx/sxd))
        fill = np.array([np.array([xxc, yyc, yyc2]) for xxc,yyc, yyc2 in sorted(zip(x_train[:,0],regressor.predict(x_train)[:,0]-dy,
                                                         regressor.predict(x_train)[:,0]+dy))])
        xc, yc, yc2 = fill[:,0],fill[:,1],fill[:,2]
        
        ax.fill_between(xc,yc,yc2,ls='None',color='b',alpha=0.2)
        
        ax.set_xlabel(r"$E_i (ev)$")
        ax.set_ylabel(r"$log(I_{ij}^{*}/(g_i A_{ij}))$")
        
        stdev = np.sqrt(np.sum((regressor.predict(x_train)-y_train)**2) / (len(y_train) - 2))

        ax.text(0.6, 0.7,  '$r^2 =$' + "%0.4f" % r2 + '\n' + 
                r'$T_{plasma}=$'+ "%0.0f" % temperature + "$\pm$" + "%0.0f" % abs(temp_95) + " K"+
                "\n" + r'$T_{plasma}=$'+ "%0.2f" % tev + "$\pm$" + "%0.2f" % abs(temp_95_ev) + " ev",
                transform=ax.transAxes,fontsize=8, bbox={'boxstyle':'round', 'facecolor': 'wheat', 'alpha': 0.5, 'pad': 0.5})

        return temperature, temp_95, r2, y_s,x_s
        
    else:
        
        return temperature, temp_95, r2, y_s, x_s


def find_wavelength_index(center_wavelength,wavelengths):
    """
    Find the index corresponding to the wavelength in wavelenghts that is 
    the closest to a given center_wavelength
    """
    
    for i in range(0,len(wavelengths)-1):
        if center_wavelength >= wavelengths[i] and center_wavelength < wavelengths[i+1]:
            return i
    
    return None

def get_closest_peak_index(center_wavelength_peak, radius, wavelengths, spectrum):
    
    #find the index of the closest wavelength
    index_center = find_wavelength_index(center_wavelength_peak, wavelengths)
    
    #find the closest peak around a given radius
    index_right = find_wavelength_index(center_wavelength_peak+radius, wavelengths)
    index_left = find_wavelength_index(center_wavelength_peak-radius, wavelengths)
    
    if index_right != None and index_left != None:
    
        #get the max
        index_max = np.argmax(spectrum[index_left:index_right])+index_left
        
        return index_max
    
    #index right or left outside the wavelength range
    else:
        return None
    
    
    
def get_closest_peak_width_index(center_wavelength_peak_index,ratio_of_maximum, wavelengths, spectrum):
    
    peak_value = spectrum[center_wavelength_peak_index]
    
    threshold = ratio_of_maximum * peak_value
    
    left_found = False
    right_found = False
    
    #find the intersection at left
    i = center_wavelength_peak_index
    try:
        while spectrum[i]>threshold:
            i-=1
        index_left = i+1
    
        #find intersection at rigth
        i = center_wavelength_peak_index
        while spectrum[i]>threshold:
            i+=1
        index_right = i-1
        
        
        return [index_left,index_right]
    
    except:
        return None
    
def get_peak_area(center_wavelength, ratio_of_maximum, wavelengths, spectrum, radius = 1, Plot = False, Title = "", fig = None, subp =(1,1,1) ):
    
    #get closest peak index
    center_wavelength_peak_index = get_closest_peak_index(center_wavelength, radius, wavelengths, spectrum)
    
    if center_wavelength_peak_index == None:
        return None
    
    #get limits at which spectrum < ratio* peak value
    peak_limits = get_closest_peak_width_index(center_wavelength_peak_index,ratio_of_maximum, wavelengths, spectrum)
    
    if peak_limits == None:
        return None
    
    peak_value = spectrum[center_wavelength_peak_index]
    
    #correction at left
    x1=wavelengths[peak_limits[0]-1]
    y1=spectrum[peak_limits[0]-1]
    x3=wavelengths[peak_limits[0]]
    y3=spectrum[peak_limits[0]]
    
    b=(y1-x1/x3*y3)/(1-x1/x3)
    m=(y3-b)/x3
    
    y2_l=ratio_of_maximum*peak_value
    x2_l=(y2_l-b)/m
    dx2_l=x3-x2_l
    correction_area_left = 0.5*(y2_l+y3)*(dx2_l)
    
    #correction at right
    x1=wavelengths[peak_limits[1]]
    y1=spectrum[peak_limits[1]]
    x3=wavelengths[peak_limits[1]+1]
    y3=spectrum[peak_limits[1]+1]
    
    b=(y1-x1/x3*y3)/(1-x1/x3)
    m=(y3-b)/x3
    
    y2_r=ratio_of_maximum*peak_value
    x2_r=(y2_r-b)/m
    dx2_r=x3-x2_r
    correction_area_right = 0.5*(y2_r+y3)*(dx2_r)
    
    #wavelength interval for correctly weighted integration by trapezoidal rule
    dwavelengths = np.roll(wavelengths, -1) - wavelengths
    
    
    #plot if you desire to
    if Plot:
        
        
        cw = wavelengths[center_wavelength_peak_index]
        
        ax = subplot(subp[0],subp[1],subp[2])
        
        #plot signal
        fr = 80
        ax.set_title(Title)
        ax.plot(wavelengths[peak_limits[0]-fr:peak_limits[1]+fr],
                spectrum[peak_limits[0]-fr:peak_limits[1]+fr],
             ls='-',lw=0.5,color='k', label = 'Signal')
        
        #plot centerwavelenght, determined peak and radius
        ax.plot([center_wavelength,center_wavelength],[0,peak_value],ls='--',lw=0.5,alpha=0.5,color='r')
        ax.plot([center_wavelength-radius,center_wavelength-radius],[0,peak_value],ls='--',lw=0.5,alpha=1,color='r')
        ax.plot([center_wavelength+radius,center_wavelength+radius],[0,peak_value],ls='--',lw=0.5,alpha=1,color='r')
        ax.plot([cw,cw],[0,peak_value],ls=':',lw=1.0,alpha=0.5,color='k', label = 'Peak Found')
        
        ax.plot([center_wavelength-radius,center_wavelength+radius],[ratio_of_maximum*peak_value,ratio_of_maximum*peak_value],ls=':',lw=1.0,alpha=0.5,color='k', label = 'Peak Found')
        
        
        y=np.concatenate((np.array([y2_l]),spectrum[peak_limits[0]:peak_limits[1]+1],np.array([y2_r])))
        x=np.concatenate((np.array([x2_l]),wavelengths[peak_limits[0]:peak_limits[1]+1],np.array([x2_r])))
        
        ax.fill_between(x,y,
                        color='b',alpha=0.1,label='Peak Area')
        
        
        if subp[2]==subp[1]*subp[0]:
            ax.legend()
        

        
        return np.trapz(y,x)
    
    
    else:
        y=np.concatenate((np.array([y2_l]),spectrum[peak_limits[0]:peak_limits[1]+1],np.array([y2_r])))
        x=np.concatenate((np.array([x2_l]),wavelengths[peak_limits[0]:peak_limits[1]+1],np.array([x2_r])))
        
        return np.trapz(y,x)

    
#####################
#####################
#####################
#####################

#####################
#####################
#####################
#####################

#####################
#####################
#####################
#####################

#####################
#####################
#####################
#####################

def get_plasma_temperature(lines, ion_energies, wl, signal):
    
    wl1 = np.ndarray.flatten(wl)
    signal1 = np.ndarray.flatten(signal)
    new_spectrum = np.copy(signal1)
    new_spectrum += -baseline_als(new_spectrum,100000,0.05)
    
    temperature, temp_95, r2, y_s, x_s = saha_boltzmann_temperature_new(lines, ion_energies , wl1, new_spectrum, ratio_of_maximum = 0.9, radius = 0.15, guess_temperature = T_ref,
                Plot = True, electron_density=n_e_ref, Title = "Saha-Boltzmann plot", Plotlines = True, use_max_intensity = False)

    return temperature, y_s, x_s 


def get_peak_area_intensity(wl,signal, l0, Plot=True):
    radius = 0.2
    ratio_of_maximum = 0.5
    wavelengths = wl
    spectrum = signal
    center_wavelength = l0
    
    center_wavelength_peak_index = get_closest_peak_index(l0, radius,  wavelengths, spectrum)
    
    if center_wavelength_peak_index == None:
        print('Peak Not Found')
        return None
    
    peak_limits = get_closest_peak_width_index(center_wavelength_peak_index,ratio_of_maximum, wavelengths, spectrum)
    
    if peak_limits == None:
        print('Peak limits Not Found')
        return None
    
    peak_value = spectrum[center_wavelength_peak_index]
    
    #correction at left
    x1=wavelengths[peak_limits[0]-1]
    y1=spectrum[peak_limits[0]-1]
    x3=wavelengths[peak_limits[0]]
    y3=spectrum[peak_limits[0]]
    
    b=(y1-x1/x3*y3)/(1-x1/x3)
    m=(y3-b)/x3
    
    y2_l=ratio_of_maximum*peak_value
    x2_l=(y2_l-b)/m
    dx2_l=x3-x2_l
    correction_area_left = 0.5*(y2_l+y3)*(dx2_l)
    
    #correction at right
    x1=wavelengths[peak_limits[1]]
    y1=spectrum[peak_limits[1]]
    x3=wavelengths[peak_limits[1]+1]
    y3=spectrum[peak_limits[1]+1]
    
    b=(y1-x1/x3*y3)/(1-x1/x3)
    m=(y3-b)/x3
    
    y2_r=ratio_of_maximum*peak_value
    x2_r=(y2_r-b)/m
    dx2_r=x3-x2_r
    correction_area_right = 0.5*(y2_r+y3)*(dx2_r)
    
    #wavelength interval for correctly weighted integration by trapezoidal rule
    dwavelengths = np.roll(wavelengths, -1) - wavelengths
    
    
    #plot if you desire to
    if Plot:
        
        subplots()
        cw = wavelengths[center_wavelength_peak_index]
        ax=gca()
        fr = 40
        ax.set_title('Peak Found at ' + str(cw))
        ax.plot(wavelengths[peak_limits[0]-fr:peak_limits[1]+fr],
                spectrum[peak_limits[0]-fr:peak_limits[1]+fr],
             ls='-',lw=0.5,color='k', label = 'Signal')
        
        #plot centerwavelenght, determined peak and radius
        ax.plot([center_wavelength,center_wavelength],[0,peak_value],ls='--',lw=0.5,alpha=0.5,color='r')
        ax.plot([center_wavelength-radius,center_wavelength-radius],[0,peak_value],ls='--',lw=0.5,alpha=1,color='r')
        ax.plot([center_wavelength+radius,center_wavelength+radius],[0,peak_value],ls='--',lw=0.5,alpha=1,color='r')
        ax.plot([cw,cw],[0,peak_value],ls=':',lw=1.0,alpha=0.5,color='k', label = 'Peak Found')
        
        ax.plot([center_wavelength-radius,center_wavelength+radius],[ratio_of_maximum*peak_value,ratio_of_maximum*peak_value],ls=':',lw=1.0,alpha=0.5,color='k', label = 'Peak Found')
        
        
        y=np.concatenate((np.array([y2_l]),spectrum[peak_limits[0]:peak_limits[1]+1],np.array([y2_r])))
        x=np.concatenate((np.array([x2_l]),wavelengths[peak_limits[0]:peak_limits[1]+1],np.array([x2_r])))
        
        ax.fill_between(x,y,
                        color='b',alpha=0.1,label='Peak Area')
        ax.legend()
        

        
        return np.trapz(y,x)
    
    
    else:
        y=np.concatenate((np.array([y2_l]),spectrum[peak_limits[0]:peak_limits[1]+1],np.array([y2_r])))
        x=np.concatenate((np.array([x2_l]),wavelengths[peak_limits[0]:peak_limits[1]+1],np.array([x2_r])))
        
        return np.trapz(y,x)

    
    return peak_intensity

def get_peak_intensity(wl,signal, l0, Plot=True):
    radius = 0.2
    ratio_of_maximum = 0.5
    wavelengths = wl
    spectrum = signal
    center_wavelength = l0
    
    center_wavelength_peak_index = get_closest_peak_index(l0, radius,  wavelengths, spectrum)
    
    if center_wavelength_peak_index == None:
        print('Peak Not Found')
        return None
    
    peak_limits = get_closest_peak_width_index(center_wavelength_peak_index,ratio_of_maximum, wavelengths, spectrum)
    
    if peak_limits == None:
        print('Peak limits Not Found')
        return None
    
    peak_value = spectrum[center_wavelength_peak_index]
    
    
    #plot if you desire to
    if Plot:
        
        subplots()
        cw = wavelengths[center_wavelength_peak_index]
        ax=gca()
        fr = 40
        ax.set_title('Peak Found at ' + str(cw))
        ax.plot(wavelengths[peak_limits[0]-fr:peak_limits[1]+fr],
                spectrum[peak_limits[0]-fr:peak_limits[1]+fr],
             ls='-',lw=0.5,color='k', label = 'Signal')
        
        #plot centerwavelenght, determined peak and radius
        ax.plot([center_wavelength,center_wavelength],[0,peak_value],ls='--',lw=0.5,alpha=0.5,color='r')
        ax.plot([center_wavelength-radius,center_wavelength-radius],[0,peak_value],ls='--',lw=0.5,alpha=1,color='r')
        ax.plot([center_wavelength+radius,center_wavelength+radius],[0,peak_value],ls='--',lw=0.5,alpha=1,color='r')
        ax.plot([cw,cw],[0,peak_value],ls=':',lw=1.0,alpha=0.5,color='k', label = 'Peak Found')
        ax.legend()
    

    
    return peak_value
