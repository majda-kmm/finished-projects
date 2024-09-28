
# importation des bibliotheques 
import tkinter
import random
import numpy as np
from math import sqrt
import time
import sys

# creation de la fenetre et du canvas support a la simulation
fenetre= tkinter.Tk()
fenetre_longueur = fenetre.winfo_screenheight()
fenetre_largeur = fenetre.winfo_screenwidth()
fenetre.title("TIPE-simulation")
fenetre.geometry(f'{fenetre_largeur}x{fenetre_longueur}')

canvas = tkinter.Canvas(fenetre)
canvas.configure(bg='#A69F9F')
canvas.pack(fill="both", expand=True)

lotVoitures = []
NbStat = 0
NbStatTab = []
NbVoitures = 4
nbTotalVoitures = 0
TempsStat = 10 #argument1
NbPointsStat = 5 #argument2
rafraichissement = 0.01#s
# creation des classes Point, Voiture et Route
class Point :
  def __init__(self,x,y) :
    self.x = x 
    self.y = y

class Route :
  connexions = []
  file_attente = [[],[],[],[],[],[],[],[],[]] 
  matrice_adjacence = np.zeros((len(connexions), len(connexions)))
  intersections = [[20,70],[1250,70],[20,350],[1250,350],[20,650],[1250,650],[650,70],[650,650],[650,350]]
  proba_cumulee = np.zeros((len(connexions), len(connexions)))
  route_largeur = 20
  
  def __init__(self,i,j):
    self.i = i
    self.j = j
    self.construction_route()

  def construction_graphe() :
    for i in range (len(Route.intersections)) :
      Route.connexions.append(Point(Route.intersections[i][0], Route.intersections[i][1]))

  def construction_matrice() :
    #|Intersection0|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||I1|
    #|20|||||||||||||||||||||||||||||||||||||650||||||||||||||||||||||||||||||||||1250|
    #|70|000000000000000000000000000000000000000000000000000000000000000000000000000000||
    #||000000000000000000000000000000000000000000000000000000000000000000000000000000||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #|350|000000000000000000000000000000000000000000000000000000000000000000000000000000||
    #||000000000000000000000000000000000000000000000000000000000000000000000000000000||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||00||||||||||||||||||||||||||||||||||||00||||||||||||||||||||||||||||||||||||00||
    #||000000000000000000000000000000000000000000000000000000000000000000000000000000||
    #||000000000000000000000000000000000000000000000000000000000000000000000000000000||
    #|650|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    
    Route.matrice_adjacence = np.zeros((len(Route.connexions), len(Route.connexions))) 
    Route.matrice_adjacence[0][2] = 0.5 # probabilité pour une voiture d'aller de la route 0 à la route 2 
    Route.matrice_adjacence[0][6] = 0.5
    Route.matrice_adjacence[1][3] = 0.5
    Route.matrice_adjacence[1][6] = 0.5
    Route.matrice_adjacence[2][0] = 0.5
    Route.matrice_adjacence[2][4] = 0.3
    Route.matrice_adjacence[2][8] = 0.2
    Route.matrice_adjacence[3][1] = 0.3
    Route.matrice_adjacence[3][5] = 0.4
    Route.matrice_adjacence[3][8] = 0.3
    Route.matrice_adjacence[4][2] = 0.5
    Route.matrice_adjacence[4][7] = 0.5
    Route.matrice_adjacence[5][3] = 0.5
    Route.matrice_adjacence[5][7] = 0.5
    Route.matrice_adjacence[6][0] = 0.4
    Route.matrice_adjacence[6][1] = 0.4
    Route.matrice_adjacence[6][8] = 0.2
    Route.matrice_adjacence[7][4] = 0.3
    Route.matrice_adjacence[7][5] = 0.3
    Route.matrice_adjacence[7][8] = 0.4
    Route.matrice_adjacence[8][2] = 0.2
    Route.matrice_adjacence[8][3] = 0.4
    Route.matrice_adjacence[8][6] = 0.2
    Route.matrice_adjacence[8][7] = 0.2

  def proba_intersections ():
    Route.proba_cumulee = np.zeros((len(Route.connexions), len(Route.connexions)))
    for i in range (len(Route.matrice_adjacence)) :
      Route.proba_cumulee[i] = np.cumsum(Route.matrice_adjacence[i])
      
    # Ainsi, on passe de la matrice d'adjacence suivante : 
    # [[0.  0.  0.5 0.  0.  0.  0.5 0.  0. ] 
    #  [0.  0.  0.  0.5 0.  0.  0.5 0.  0. ] 
    #  [0.5 0.  0.  0.  0.3 0.  0.  0.  0.2] 
    #  [0.  0.3 0.  0.  0.  0.4 0.  0.  0.3]   
    #  [0.  0.  0.5 0.  0.  0.  0.  0.5 0. ] 
    #  [0.  0.  0.  0.5 0.  0.  0.  0.5 0. ] 
    #  [0.4 0.4 0.  0.  0.  0.  0.  0.  0.2] 
    #  [0.  0.  0.  0.  0.3 0.3 0.  0.  0.4] 
    #  [0.  0.  0.2 0.4 0.  0.  0.2 0.2 0. ]]

    # à la matrice de proba cumulée :
    # [[0.  0.  0.5 0.5 0.5 0.5 1.  1.  1. ]
    # [0.  0.  0.  0.5 0.5 0.5 1.  1.  1. ]
    # [0.5 0.5 0.5 0.5 0.8 0.8 0.8 0.8 1. ]
    # [0.  0.3 0.3 0.3 0.3 0.7 0.7 0.7 1. ]
    # [0.  0.  0.5 0.5 0.5 0.5 0.5 1.  1. ]
    # [0.  0.  0.  0.5 0.5 0.5 0.5 1.  1. ]
    # [0.4 0.8 0.8 0.8 0.8 0.8 0.8 0.8 1. ]
    # [0.  0.  0.  0.  0.3 0.6 0.6 0.6 1. ]
    # [0.  0.  0.2 0.6 0.6 0.6 0.8 1.  1. ]]

  def construction_route(self):
    # la fonction permet simplement de tracer les routes sur le canvas
    if Route.matrice_adjacence[self.i][self.j] != 0 :      
      if Route.connexions[self.i].x == Route.connexions[self.j].x :
        self.longueur_route = abs(Route.connexions[self.i].y-Route.connexions[self.j].y)
        canvas.create_rectangle(Route.connexions[self.i].x-Route.route_largeur,Route.connexions[self.i].y,Route.connexions[self.j].x+Route.route_largeur,Route.connexions[self.j].y, fill='#E3E0E0',width=0)
      else : 
        self.longueur_route = abs(Route.connexions[self.i].x-Route.connexions[self.j].x)
        canvas.create_rectangle(Route.connexions[self.i].x,Route.connexions[self.i].y-Route.route_largeur,Route.connexions[self.j].x,Route.connexions[self.j].y+Route.route_largeur, fill='#E3E0E0', width = 0)

  def derniere_voiture (self) : 
    # --en cours : la fonction permet de trouver la derniere voiture de la route
    # dans l'optique du modele de l'IDM et de trouver le leader de chaque 
    # voiture (ici, si une voiture se trouve premiere dans une route,
    # son leader est la derniere voiture de la route suivante 
    maxi = 0
    for v in Voiture.voitures :
      if v.route_debut == self.i and v.route_fin == self.j and v.longueur_r-v.pas >maxi :
        maxi = v.longueur_r-v.pas
        self.derniere = v

class Voiture :
  vitesse_max = 2
  a = 1 # m/s^2 acceleration maximale
  b = 1.5 #m/s^2 decceleration confortable
  b_max = 10 #m/s^2 decceleration maximale
  T = 1 #s : delai de securite 
  delta = 4 #: exposant d'acceleration
  distance_securite = 20
  pos0=0
  def __init__(self, route_debut, route_fin, pas,dp) :
    self.route_debut = route_debut
    self.route_fin = route_fin
    self.dp = dp # vitesse de la voiture 
    self.pas = pas # permet de connaitre l'avancement d'une voiture sur sa route actuelle
    self.lead = self
    self.delta_v = self.lead.dp-self.dp
    self.calcul_position()
    self.creation_voiture()
    self.acc = 0
    self.secu = 0
    
  def couleur():
    hexadecimal = "#"+''.join(random.choice('ABCDEF0123456789')for i in range(6))
    return hexadecimal

  def usine_a_voitures () :
    #global NbVoitures
    global nbTotalVoitures
    # on crée les voitures qui circuleront en circuit fermé
    for i in range(NbVoitures) :
      if i >= 9 :
        break
      for k in range (len(Route.matrice_adjacence[0])) :
        if Route.matrice_adjacence[i][k] != 0 :
          lotVoitures.append(Voiture(i,k,random.randint(0,250),1))
          lotVoitures.append(Voiture(k,i,random.randint(0,250),1))
          lotVoitures.append(Voiture(i,k,random.randint(0,250),1))
          lotVoitures.append(Voiture(k,i,random.randint(0,250),1))
          lotVoitures.append(Voiture(i,k,random.randint(0,250),1))
          nbTotalVoitures = nbTotalVoitures + 5

  def calcul_position(self) :
    global NbStat
    # on calcule les coordonnées du debut et de la fin de la route sur laquelle se trouve la voiture,
    # sa longueur, ainsi que le vecteur unitaire qui indique le sens et la direction de deplacement 
    # d'une voiture (du type [horizontale, verticale] )
    # exemple : [-1,0] -> la voiture se déplace selon les x décroissants 
    self.pd = np.array([Route.connexions[self.route_debut].x, Route.connexions[self.route_debut].y])
    self.pa = np.array([Route.connexions[self.route_fin].x, Route.connexions[self.route_fin].y])
    self.u = (self.pa-self.pd)/np.linalg.norm(self.pa-self.pd)
    
    pasConstante = 10
    if self.u[0] == 0 and self.u[1] == -1 :
      self.pd = np.array([Route.connexions[self.route_debut].x+pasConstante, Route.connexions[self.route_debut].y])
      self.pa = np.array([Route.connexions[self.route_fin].x+pasConstante, Route.connexions[self.route_fin].y])
      self.longueur_r = abs(self.pd-self.pa)[1]
    elif self.u[0] == 0 and self.u[1] == 1 :
      self.pd = np.array([Route.connexions[self.route_debut].x-pasConstante, Route.connexions[self.route_debut].y])
      self.pa = np.array([Route.connexions[self.route_fin].x-pasConstante, Route.connexions[self.route_fin].y])
      self.longueur_r = abs(self.pd-self.pa)[1]
    elif self.u[0] == 1 and self.u[1] == 0 :
      self.pd = np.array([Route.connexions[self.route_debut].x, Route.connexions[self.route_debut].y+pasConstante])
      self.pa = np.array([Route.connexions[self.route_fin].x, Route.connexions[self.route_fin].y+pasConstante])
      self.longueur_r = abs(self.pd-self.pa)[0]
    elif self.u[0] == -1 and self.u[1] == 0 :
      self.pd = np.array([Route.connexions[self.route_debut].x, Route.connexions[self.route_debut].y-pasConstante])
      self.pa = np.array([Route.connexions[self.route_fin].x, Route.connexions[self.route_fin].y-pasConstante])
      self.longueur_r = abs(self.pd-self.pa)[0]

    # tout ça dans le but de calculer les coordonnées x y de la position actuelle de la voiture 
    self.pos = self.pd + self.pas * self.u
    if self.route_debut == 0 and self.pos[0] != self.pos0 and round(self.pos[0],0) == 300 :
      self.pos0 = self.pos[0]
      NbStat = NbStat + 1
  
  def creation_voiture(self) :
    self.apparence_voiture()
    self.rect = canvas.create_rectangle(self.pos[0]-self.largeur,
                      self.pos[1]-self.longueur,
                      self.pos[0]+self.largeur,
                      self.pos[1]+self.longueur,
                      fill = Voiture.couleur(), outline="Black", width=1)

  def apparence_voiture(self):
    if self.u[0] == 0 :
          self.largeur = 4
          self.longueur = 7
    else :
      self.largeur = 7
      self.longueur = 4

  def leader(self) :
    maxi = self
    for voit in lotVoitures :
      if self.route_debut == voit.route_debut and self.route_fin == voit.route_fin and maxi.pas <= voit.pas and self != voit : 
        maxi = voit

    for voit in lotVoitures :
      if self.route_debut == voit.route_debut and self.route_fin == voit.route_fin and voit.pas >= self.pas and self != voit : 
       if(voit.pas <= maxi.pas ) :
        maxi = voit
    self.lead = maxi
  def distance_secu (self) :
    s = Voiture.distance_securite + max(0,self.dp*Voiture.T +(self.dp*self.delta_v)/(2*sqrt(Voiture.a*Voiture.b)))
    self.secu = s
    #print ('self.secu=',s)
    self.delta_v = self.dp-self.lead.dp

  def acceleration(self) :
    if self.lead == self and self.dp < Voiture.vitesse_max and self not in file_croisement(lotVoitures)[self.route_fin]:
      ac = Voiture.a*(1-(self.dp/Voiture.vitesse_max)**Voiture.delta-((self.secu)/(100000))**2)
      self.acc = ac
    elif self not in file_croisement(lotVoitures)[self.route_fin]: 
      delta = self.lead.pas- self.pas-self.longueur*2
      if delta == 0 :
        delta = 0.0001
      ac = Voiture.a*(1-(self.dp/Voiture.vitesse_max)**Voiture.delta-((self.secu)/delta)**2)
      self.acc = ac
    if self in file_croisement(lotVoitures)[self.route_fin]:
      self.acc = 0
      
  def changement_croisement(self) :
    ### si la voiture arrive a la fin de la route, on change de direction selon la matrice de proba cumulee
    if abs(self.pos[0]-self.pa[0])<= 30 and abs(self.pos[1]-self.pa[1]) <=30 :
      distribution = Route.proba_cumulee[self.route_fin]
      choix = self.route_debut
      while self.route_debut == choix :
        random_nombre = np.random.uniform()
        for i in range (len(distribution)) :
          if random_nombre <= distribution[i] :
            choix = i
            break
        if random_nombre > distribution[-1] :
          choix = np.argmax(distribution > random_nombre)
      self.route_debut = self.route_fin
      self.route_fin = choix
      self.pas = 0

  def mise_a_jour(self) :
    self.delta_v = self.dp-self.lead.dp
    if self.dp + self.acc < 0 :
      self.dp = 0
      self.pas += (1/2*self.dp**2)/self.acc      
    else :
      self.dp += self.acc*rafraichissement
      self.pas += self.dp + 1/2*self.acc*rafraichissement**2
  def freinage(self) :
    rando = random.randint(1,100)
    if rando<2 : 
      self.dp -=self.dp/2

def file_croisement(voitures) :
  pas_croisement=60
  for v in voitures :
    if v.longueur_r-v.pas < pas_croisement and v not in Route.file_attente[v.route_fin] :
      Route.file_attente[v.route_fin].append(v)
  return Route.file_attente

def gestion_croisement(v) :
  for i in Route.file_attente :
    if len(i)>=1 :
      i[0].dp = 0.75 
  for i in Route.file_attente :
    if v in i :
      if v == i[0] : 
        if v.pas >= 10 and v.pas <30:
          v.dp = 1
          i.remove(v)
      else:
        v.dp = 0

def animate () :
  file_croisement(lotVoitures)
  for v in lotVoitures :
    v.mise_a_jour()
    v.leader()
    v.distance_secu()
    v.acceleration()
    v.freinage()
    gestion_croisement(v)
    v.changement_croisement()
    v.apparence_voiture()
    v.calcul_position()    

def affichage() :
  for v in lotVoitures :
    canvas.coords(v.rect, v.pos[0]-v.largeur, v.pos[1]-v.longueur,v.pos[0]+v.largeur,v.pos[1]+v.longueur)
    fenetre.update()

def init():
  #global NbVoitures
  global TempsStat
  global NbPointsStat
  Route.construction_graphe()
  Route.construction_matrice()
  Route.proba_intersections()
  n = len(Route.matrice_adjacence)
  for i in range (n) :
    for j in range(i+1,n):
      Route(i,j)  
  if len(sys.argv) > 1 :
    NbVoitures = int(sys.argv[1])
  if len(sys.argv) > 2 :
    TempsStat = int(sys.argv[2])
  if len(sys.argv) > 3 :
    NbPointsStat = int(sys.argv[3])
  Voiture.usine_a_voitures()

#debut main
init()
print ('NbVoitures=',NbVoitures)
print ('TempsStat=',TempsStat)
print ('NbPointsStat=',NbPointsStat)
strPrint = str(nbTotalVoitures)
strPrint = strPrint + ";"
f = open('C:\doc\perso\\statVoitures10.csv', 'a')
f.write(str(nbTotalVoitures))
f.write(";")
t = time.time()
t1 = time.time()
while True :
  delai = time.time()- t 
  delaiTotal=time.time()- t1
  if delai > 0.02:
    animate()
    affichage()
    t = time.time() 
  #time.sleep(0.000001)
  if delaiTotal > TempsStat :
    t1 = time.time()
    NbStatTab.append(NbStat)
    f.write(str(NbStat))
    f.write(";")
    strPrint = strPrint +str(NbStat)+";"
    NbStat=0
  if len(NbStatTab) == NbPointsStat :
    print ('fermeture fichier')
    moy1 = sum(NbStatTab)/len(NbStatTab)
    print("moy1=",moy1)
    strPrint = strPrint +str(moy1).replace(".",",")
    strPrint = strPrint +"\n"
    print(strPrint)
    f.write(strPrint)
    f.write("\n")
    f.close
    break