# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 16:05:12 2016

@author: clay_budin

Step 1: 1D linear convection
	du/dt + c*du/dx = 0
linear because c is constant

Schemes:
Upwind - Forward diff in time, Backward diff in space
Leapfrog - Centered diff in time, u(n+1,i) = u(n-1,i) - c*dt/dx * (u(n,i+1)-u(n,i-1)) - centered diff using point from 2 time steps back
Lax-Friedrichs - FD in time, u(n+1,i) = 1/2*(u(n,i+1)+u(n,i-1)) - c*dt/(2*dx) * (u(n,i+1)-u(n,i-1)) - centered diff using avg for u(n,i)
Lax-Wendroff - FD in time, u(n+1,i) = u(n,i) - sigma/2*(u(n,i+1)-u(n,i-1)) + sigma^2/2*(u(n,i+1)-2*u(n,i)+u(n,i-1)) - adds second derivive term for more accuracy

Domain: [0,2]
Range: [0,1]
Initial Conditions: u(0) = 1, 0 everywhere else
Boundary Conditions: u(0) = 1

c*dt/dx (= sigma) seems to be important to stability - CFL number
	if > 1, sim blows up, eg if 2: u(t+1,i) = 2*u(t,i-1) - u(t,i)
	if == 1, sim is perfect: u(t+1,i) = u(t,i-1)
	if < 1, sim works but seems to damp high freqs, eg if .5 get averaging bwtn u(t,i-1) and u(t,i) - numerical diffusion



"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# graphing vars
fig, ax = plt.subplots()
ax.grid()
ax.set_xlim(-.1, 2.1)
ax.set_ylim(-.1, 1.4)

line_uw, = ax.plot([], [], "b", lw=1)
line_lf, = ax.plot([], [], "r", lw=1)
line_lxfr, = ax.plot([], [], "g", lw=1)
line_lw, = ax.plot([], [], "c", lw=1)



# simulation constants
nx = 201
nt = 300
c = 0.5 #1.0
dt = 0.01
dx = 2.0 / (nx-1.0)

# simlation grids - 1D
xdata = []
yduw = []				# upwind scheme - backwards difference
ydlf, yplf = [], []		# leapfrog scheme - save previous data since we need u(t-2)
ydlxfr = []
ydlw = []


# global var - current time step
ct = 0

def init ():
	global ct
	if ct == 0: print "init() dx = " + str(dx) + " dt = " + str(dt) + " c*dt/dx = " + str(c*dt/dx)
	ct = 0

	del xdata[:]
	del yduw[:]
	del ydlf[:]
	del yplf[:]
	del ydlxfr[:]
	del ydlw[:]

	for i in range(nx):
		x = i*dx
		xdata.append(x)
		y = 0.0

		# IC u(0) = 1
		if i == 0: y = 1.0

		yduw.append(y)
		ydlf.append(y)
		yplf.append(y)
		ydlxfr.append(y)
		ydlw.append(y)

	line_uw.set_data(xdata, yduw)
	line_lf.set_data(xdata, ydlf)
	line_lxfr.set_data(xdata, ydlxfr)
	line_lw.set_data(xdata, ydlw)




def data_gen ():
	global ct
	while ct <= nt:
		#print "data_gen() ct =", ct
		ct += 1

		# for useful visual comparissons among these schemes, see:
		#	http://www.thevisualroom.com/heavy_side_and_sinusoidal_input.html

		# Upwind scheme (backwards diff)
		# copy contents of yduw to ypuw
		ypuw = []
		ypuw[:] = yduw[:]

		for i in range(1,nx-1):
			yduw[i] = ypuw[i] - (c*dt/dx)*(ypuw[i]-ypuw[i-1])
			#yduw[i] = ypuw[i] - (c*dt/(2.0*dx))*(ypuw[i+1]-ypuw[i-1])		# central diff - not stable for any c


		# leapfrog scheme
		# stable for sigma <= 1.0
		# better than upwind on leading edge, but trailing edge has oscillations
		ypplf = []
		ypplf[:] = yplf[:]
		yplf[:] = ydlf[:]
		if ct == 1:
			# need a startup scheme - upwind
			#print "Startup"
			for i in range(1,nx-1):
				ydlf[i] = yplf[i] - (c*dt/dx)*(yplf[i]-yplf[i-1])
		else:
			# all other times use leapfrog update step
			for i in range(1,nx-1):
				ydlf[i] = ypplf[i] - (c*dt/dx)*(yplf[i+1]-yplf[i-1])


		# Lax-Friedrichs
		# seems like worse numerical diffusion than with Upwind
		yplxfr = []
		yplxfr[:] = ydlxfr[:]
		for i in range(1,nx-1):
			ydlxfr[i] = .5*(yplxfr[i+1]+yplxfr[i-1]) - (c*dt/(2*dx))*(yplxfr[i+1]-yplxfr[i-1])

		# Lax-Wendroff
		# improved on leading edge like leapfrog, oscillations on trailing edge but better than leapfrog
		yplw = []
		yplw[:] = ydlw[:]
		for i in range(1,nx-1):
			ydlw[i] = yplw[i] - (c*dt/(2*dx))*(yplw[i+1]-yplw[i-1]) + (c*dt/dx)*(c*dt/dx)*.5*(yplw[i+1]-2*yplw[i]+yplw[i-1])


		# don't need to enfore BC since leftmost element of ydata arrays not touched by iterations

		yield


def run (data):
	#print "run()"
	line_uw.set_ydata(yduw)
	line_lf.set_ydata(ydlf)
	line_lxfr.set_ydata(ydlxfr)
	line_lw.set_ydata(ydlw)



ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=10, repeat=True, init_func=init)

plt.show()



