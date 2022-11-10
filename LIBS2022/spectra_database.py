import h5py
import numpy as np
import requests
import re


# def get_spectra_online(element, density = 1e17, temperature=1):
#     density_str = '{:.2e}'.format(density).replace('e+','e')
#     temperature_str = '{:.2f}'.format(temperature)
#     URL = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl?composition="+element+"%3A100&mytext%5B%5D="+element+"&myperc%5B%5D=100&spectra="+element+"0-2&low_w=250&limits_type=0&upp_w=900&show_av=2&unit=1&resolution=5000&temp="+temperature_str+"&eden="+density_str+"&maxcharge=2&min_rel_int=0.01&libs=1"
#     page = requests.get(URL)
#     lista = page.text.split('var dataDopplerArray=')[1].split(';')[0].replace('],',']').replace('null','0').split('\n')[1:]
#     arr = np.array([np.fromstring(lista[i][1:-1],sep=',') for i in range(0,len(lista)-1)])
#     return arr

# def get_spectra_online(element, density = 1e17, temperature=1):
#     density_str = '{:.2e}'.format(density).replace('e+','e')
#     temperature_str = '{:.2f}'.format(temperature)
#     URL = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl?composition="+element+"%3A100&mytext%5B%5D="+element+"&myperc%5B%5D=100&spectra="+element+"0-2&low_w=250&limits_type=0&upp_w=900&show_av=2&unit=1&resolution=100000&temp="+temperature_str+"&eden="+density_str+"&maxcharge=2&min_rel_int=0.01&libs=1"
#     page = requests.get(URL)
#     lista = page.text.split('var dataSticksArray=')[1].split(';')[0].replace('],',']').replace('null','0').split('\n')[1:]
#     arr = np.array([np.fromstring(lista[i][1:-1],sep=',') for i in range(0,len(lista)-1)])
#     return arr

def get_spectra_online(element, density = 1e17, temperature=1):
    density_str = '{:.2e}'.format(density).replace('e+','e')
    temperature_str = '{:.2f}'.format(temperature)
    URL = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl?composition="+element+"%3A100&mytext%5B%5D="+element+"&myperc%5B%5D=100&spectra="+element+"0-2&low_w=250&limits_type=0&upp_w=900&show_av=2&unit=1&resolution=100000&temp="+temperature_str+"&eden="+density_str+"&maxcharge=2&min_rel_int=0.01&libs=1"
    page = requests.get(URL)
    lista = page.text.split('var dataSticksArray=')[1].split(';')[0].replace('],',']').replace('null','0').split('\n')[1:]
    arr = np.array([np.fromstring(lista[i][1:-1],sep=',') for i in range(0,len(lista)-1)])
    
    x=np.linspace(250, 900,10000)
    y1=np.zeros(len(x))
    R=100
    for i in range(0,len(spectrum1[:,1])):
        y1+=spectrum1[i,1]*np.exp(-(x-np.ones(len(x))*spectrum1[i,0])**2*R)

    y2=np.zeros(len(x))
    for i in range(0,len(spectrum1[:,1])):
        y2+=spectrum1[i,2]*np.exp(-(x-np.ones(len(x))*spectrum1[i,0])**2*R)

    y3=np.zeros(len(x))
    for i in range(0,len(spectrum1[:,1])):
        y3+=spectrum1[i,3]*np.exp(-(x-np.ones(len(x))*spectrum1[i,0])**2*R)

    return np.transpose(np.vstack([x,y1,y2,y3]))


def save_spectra(element):
    f = h5py.File('database/' + element +'.h5', 'w' )
    f['data'] = get_spectra_online(element)
    f.close()

def get_spectra(element):
    f = h5py.File('database/' + element +'.h5', 'r' )
    arr = np.array(f['data'])
    f.close()
    return arr

if __name__ == "main":
    
    ptable = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg',
           'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr',
           'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br',
           'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
           'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La',
           'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er',
           'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au',
           'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
           'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md',
           'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn',
           'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']

    for element in ptable:
        print(element,end='\r')
        #get_spectra_online('Li', density = 1e17, temperature=1)
        try:
            save_spectra(element)
        except:
            pass
        #get_spectra('Li')