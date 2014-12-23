import string
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import polynomial as P

class dossier:
	"gere l arborescence des data qui doivent quand meme etre placees dans le bon dossier de mois"
	def __init__(self, annee, mois):
        	self.annee = str(annee)
        	self.mois = str(mois).zfill(2)
		self.mypath = self.path()
		self.extr = self.extrait()
		self.mydate = self.date()
		self.rangement = self.classement()
		self.cre = self.create()

	def path(self):
		mypath = '/home/cyril/Documents/data_pompe_sonde/'+str(self.annee)+'/'+str(self.mois)

		return mypath

	def extrait(self):
		mypath = self.mypath
		f = next(os.walk(mypath))
		return f[2:][0]
	
	def date(self):
		numero_jour = set()
		fichier=self.extr
		for f in fichier:
			numero_jour.add(f[0:4])
		return numero_jour
		
	
	def classement(self):
		mypath = self.mypath
		date = self.mydate
		mois = mypath[-2:]
		mois_file = set()
		date_range = set()

		for chaine in date:
			if chaine[2:4]==mois:
				date_range.add(chaine[0:2])
				mois_file.add(chaine[2:4])
			else:
				print 'Les fichiers XX'+chaine[2:4]+' ne sont pas ranges dans le dossier du mois correspondant !'
		return {'mois':mois_file,'jour':date_range}

	def create(self):
		mypath = self.mypath
		dictionnaire_mois_jour= self.rangement

		for jour in dictionnaire_mois_jour['jour']:
			mypath_jour = mypath+'/'+jour
			mypath_jour_dat = mypath_jour+'/'+'dat'
			mypath_jour_dat2 = mypath_jour+'/'+'dat2'
			mypath_jour_dat_A = mypath_jour_dat+'/'+'A'
			mypath_jour_dat_R = mypath_jour_dat+'/'+'R'

			if not os.path.exists(mypath_jour):
	  				os.mkdir(mypath_jour)
					os.mkdir(mypath_jour_dat)
					os.mkdir(mypath_jour_dat2)
					os.mkdir(mypath_jour_dat_A)
					os.mkdir(mypath_jour_dat_R)

	def deplacement(self):
		mypath = self.mypath
		liste_fichiers=self.extr
		
		for fichier in liste_fichiers:
    			if fichier[2:4] in mypath[-2:]:
        			if fichier[6:12]!='ARMTRS':
            				if fichier[-4:]=='dat2':
                				src=mypath+'/'+fichier
						dst=mypath+'/'+str(fichier[0:2])+'/dat2/'+fichier
						shutil.move(src,dst)
            				elif fichier[6]=='A':
                				src=mypath+'/'+fichier
						dst=mypath+'/'+str(fichier[0:2])+'/dat/A/'+fichier
						shutil.move(src, dst)
            				elif fichier[6]=='R':
                				src=mypath+'/'+fichier
						dst=mypath+'/'+str(fichier[0:2])+'/dat/R/'+fichier
						shutil.move(src, dst)
            				else:
                				print 'fichier:'+fichier+' non pris en compte'
        			else:
            				print 'On ne prend pas en compte les fichiers ARMTRS'
			else:
        			print 'Le fichier ne sera pas traite car ne correspond pas au mois courant'

class traitement:
	"gere le traitement des data mise en arborescence par la classe dossier"
	def __init__(self, annee, mois, jour,temps=[],signal=[],nomfigure='',abscisse='',ordre=3,Puissance=False):
		self.annee = str(annee)
		self.mois = str(mois).zfill(2)
		self.jour = str(jour).zfill(2)
		self.mypath = self.path()
		self.atraiter = self.fichieratraiter()
		self.temp = self.temporel(ordre)

	def path(self):
		mypath = '/home/cyril/Documents/data_pompe_sonde/'+str(self.annee)+'/'+str(self.mois)+'/'+str(self.jour)

		return mypath
	
	def plotter(self,temps,signal,fit,nomfigure,xlim,abscisse,ordonnee='Amplitude (Units)',fitter=False):

		fig=plt.figure()

		ax1 = fig.add_subplot(111)
		plt.plot(temps,signal,lw=2,color=[1,0.5,0])
		ax1.set_title(str(nomfigure),position=(0.5,1.05))
		ax1.set_xlabel(str(abscisse))
		ax1.set_ylabel(str(ordonnee))
		ax1.set_xlim(xlim)
		
		if fitter==True:
			plt.plot(temps,fit,lw=2,color=[1,0.5,0])
			
		plt.savefig(str(nomfigure),bbox_inches='tight', dpi=150, transparent=False)

	def fichieratraiter(self):
		a_traiter=[]
		f = os.walk(self.mypath)
		for (dirpath, dirnames, filenames) in f:
    			filenames_nopdf=[]
    			if filenames!=[]:
        			for item in filenames:
            				if ('pdf' in item)==False:
                				if 'dat2' in item:
                    					fichier_image=dirpath+'/'+item[:-5]+'.pdf'
                    					fichier_image_FFT=dirpath+'/'+item[:-5]+'_FFT.pdf'
                				else:
                    					fichier_image=dirpath+'/'+item[:-4]+'.pdf'
                    					fichier_image_FFT=dirpath+'/'+item[:-4]+'_FFT.pdf'
                				noms_fichiers=(item, fichier_image, fichier_image_FFT)
                				filenames_nopdf.append(noms_fichiers)
            					a_traiter.append((dirpath, noms_fichiers))
		return a_traiter
		
	def temporel(self,ordre=3):
		xlim=[]
		tracetemp={}
		for item in self.atraiter:
			fichier_path=item[0]+'/'+item[1][0]
			fichier=open(fichier_path,'r')
			fichier_forme=fichier.readlines()
			time=[]
			signal=[]
			for ligne in fichier_forme:
    				coupe_debut=ligne.find('\t')
    				coupe_fin=ligne.rfind('\t')
    				ti=float(ligne[:coupe_debut])
    				si=float(ligne[coupe_debut+1:coupe_debut+11])
    				time.append(ti)
    				signal.append(si)
			xlim=[0,time[-1:][0]]
			fichier_image=item[1][1]
			fichier_image_FFT=item[1][2]	
			polynome = P.polyfit(time,signal,ordre)
			fit=P.polyval(time, polynome)
			tracetemp[fichier_path]=(time,signal,fit,fichier_image,xlim,'Temps (ps)',fichier_image_FFT)
		return tracetemp	

	def frequentiel(self,Puissance):
		xlim=[0,50]
		tracefreq={}
		for key in self.temp:
			vecteur=self.temp[key]
			t=vecteur[0]
			s=vecteur[1]-vecteur[2]
			nom=self.temp[key][6]
			Y_FFT = np.fft.fft(s)
			N = len(Y_FFT)/2+1
			dt = t[1] - t[0]
			fa = 1.0/dt
			X = np.linspace(0, fa/2, N, endpoint=True)
			hann = np.hanning(len(s))
			Yhann = np.fft.fft(hann*s)
			S_FFT = 2.0*abs(Yhann[:N])/N
			P_FFT = S_FFT**2
			if Puissance==True:
				tracefreq[key]=(1000*X,P_FFT,nom,xlim,'Frequence (GHz)','Puissance (Units^2)')
			else:
				tracefreq[key]=(1000*X,S_FFT,nom,xlim,'Frequence (GHz)','Amplitude (Units)')
		return tracefreq
		

