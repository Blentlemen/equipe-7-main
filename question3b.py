import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import math

# ------------- CHANGER LES PARAMÈTRES AVANT DE LANCER LE CODE -------------------- # 
#initialiser la géométrie
a, b, c, d, e, f = 2, 2, 4, 2, 0.2, 6
N = 4
dx = 0.1 # step

# -----------------------------Question 1------------------------------#

largeur = (2*a + (N+1)*(c/2) + (N-1)*(d/2)) # trouvé en analysant l'image 
Lx = largeur
Ly = f # grandeur de la grille en x et en y sans espacement autour du pm
nx = int(Lx/dx)
ny = int(Ly/dx) # nombre de points en x et en y

x = np.linspace(0, Lx, nx)
y = np.linspace(-Ly/2, Ly/2, ny)
X, Y = np.meshgrid(x, y)

#initialiser le potentiel à 0 partout
V = np.zeros((ny,nx)) # potentiel initial
bloqué = np.zeros((ny,nx), dtype=bool)


# rentrer les dynodes pour laisser un potentiel qui ne varie pas
# Cette fonction est en [y,x]
#f, b et e sont en x
# a,c,d sont en y
def placer_dynodes_bas(V, bloqué):
    for i in range(N//2 + N%2):
        pot_dyn = (2*i+1) * 100
        vert_start = b #coordonnée verticale du début de la dynode
        vert_end = b + e # la fin
        horiz_start = a + i*(c+d)   #coordonnée horizontale du début de la dynode
        horiz_end = horiz_start + c # fin

        ix_start = int(horiz_start/dx) #donne l'indice de colonne correspondant sur la grille
        ix_end = int(horiz_end/dx) # même chose mais pour la fin
        iy_start = int(vert_start/dx) # début y
        iy_end = int(vert_end/dx) # fin y

        V[iy_start:iy_end, ix_start:ix_end] = pot_dyn
        bloqué[iy_start:iy_end, ix_start:ix_end] = True
    return V, bloqué

def placer_dynodes_haut(V, bloqué):
    for i in range(N//2):
        pot_dyn = (2*(i+1)) * 100
        vert_start = f-b #coordonnée verticale du début de la dynode
        vert_end = vert_start + e # la fin
        horiz_start = a + (i+1)*c +d/2 + i*d - c/2 #coordonnée horizontale du début de la dynode
        horiz_end = horiz_start + c # fin

        ix_start = int(horiz_start/dx) #donne l'indice de colonne correspondant sur la grille
        ix_end = int(horiz_end/dx) # même chose mais pour la fin
        iy_start = int(vert_start/dx) # début y
        iy_end = int(vert_end/dx) # fin y

        V[iy_start:iy_end, ix_start:ix_end] = pot_dyn
        bloqué[iy_start:iy_end, ix_start:ix_end] = True
    return V, bloqué

V, bloqué = placer_dynodes_haut(V, bloqué)
V, bloqué = placer_dynodes_bas(V, bloqué)

# La variation minimale est établie à 10^-5 parce que 
def relaxation(V, bloqué, variation=1e-5, max_iter=1000000):
    for iteration in range(max_iter):
        V_old = V.copy() # pour la comparaison pour la tolérance
        for i in range(1, ny-1): #tous les points sauf les bords
            for j in range(1, nx-1): # meme chose en x
                if not bloqué[i, j]:
                    V[i, j] = 0.25 * (V_old[i+1, j] + V_old[i-1, j] +
                                     V_old[i, j+1] + V_old[i, j-1])
        chang_pot_max = np.max(np.abs(V - V_old))
        if chang_pot_max < variation:
            print(f"Convergence atteinte après {iteration} itérations avec une tolérance de variation de {variation})")
            print("Nous avons atteint un potentiel qui ne varie presque plus et le problème est considéré résolu")
            break
    else:
        print("Attention !!!!!!!!!! ")
        print("Le maximum d'itérations a été atteint sans stabilisation, donc le programme a été arrêté")
    return V
res = relaxation(V, bloqué, variation=1e-5, max_iter=3000)
# --------------------------------------- Question 2 ---------------------------------#

# calculer le gradient en x et y grâce à numpy
Ey, Ex = np.gradient(-res, dx, dx)

E_norm = np.sqrt(Ex**2 + Ey**2) #norme

# ---------------------------------------- Question 3a--------------------------------#

#implémenter une fonction de déterminer x(t) d'un électron
#Conditions initiales applicables: x(t=0) et v(t=0)

#constantes physiques:
q = -1.602*e-19 # charge de l'électron
m = 9.109*e-31 # masse
# F(x,y,z) = qE(x,y,z)
# a = qE/m

# Il faut approximer le champ entre les cases existantes avec euler pour des valeurs
def Eulerer_lechamp(x, y, Ex, Ey, dx):
    # transformer la position en indice de row/colonne
    i = int(y / dx)
    j = int(x / dx)
    # il faut créer une référence de grandeur pour savoir si on est dans la grille
    ny, nx = Ex.shape
    if 0 <= i < ny and 0 <= j < nx: # vérifier que c'est dans la grille que j'ai créée sinon ça marche pas
        return Ex[i, j], Ey[i, j]
    else:
        return 0, 0 # si on n'est pas dans la grille, il n'y a pas de champ

def position_el(x0, y0, vx0, vy0, Ex, Ey, dx, dt, it_max):
    #placer l'électron à t=0
    x = [x0] # position à t=0
    y = [y0]
    vx = vx0 # vitesse à t=0
    vy = vy0

    for i in range(it_max):
        # méthode d'Euler du champ au point courant
        Ex_val, Ey_val = Eulerer_lechamp(x[-1], y[-1], Ex, Ey, dx)
        #littéralement Euler:
        ax = (q*Ex_val / m) # accélération en x
        ay = (q*Ey_val / m)  # même chose en y

        vx += ax * dt # changement infinitésimal de la vitesse
        vy += ay * dt # même chose en y

        x_new = x[-1] + vx * dt # changement infinitésimal de la position
        y_new = y[-1] + vy * dt

        x.append(x_new)
        y.append(y_new)

        if not (0 <= x_new < Lx and -Ly/2 <= y_new <= Ly/2):
            print("L'électron n'est plus dans le tube PM")
            break #enfin ça va être moins chiant
    return np.array(x), np.array(y)


# ---------------------------------------Question 3b --------------------------------------------#

x0 = 0.1
y0 = 0.1
vx0 = 0
vy0 = 0
dt = 1e-5
it_max = 1000000
traj_x, traj_y = position_el(x0, y0, vx0, vy0, Ex, Ey, dx, dt, it_max)

#----------------------------------------affichage de la trajectoire x(t)------------------------#
cp = plt.contourf(X, Y, res, levels=100, cmap='plasma')
contour_dynodes = plt.contour(X, Y, bloqué, levels=[0.5], colors='black', linewidths=0.5)
plt.colorbar(cp, label="Potentiel (V)")
plt.plot(traj_x, traj_y, 'y-', label="Trajectoire")
plt.plot(x0, y0, 'go', label="Départ (0,0)", markersize=2.5)
plt.xlabel("x (mm)")
plt.ylabel("y (mm)")
plt.title("Q3 b)")
plt.legend()
plt.axis("equal")
plt.savefig("Q3b_trajectoire.png", dpi=300)
plt.show()

print("Position finale :", traj_x[-1], traj_y[-1])
print("Déplacement total :", traj_x[-1] - traj_x[0], traj_y[-1] - traj_y[0])