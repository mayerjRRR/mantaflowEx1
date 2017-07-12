#
# Simple example scene for a 2D simulation
# Simulation of a buoyant smoke density plume with open boundaries at top & bottom
#
from manta import *

#this has to be done so keras doesn't kill itself
import locale
locale.setlocale(locale.LC_NUMERIC, "en_US.UTF-8")
from keras.models import Sequential
from keras.layers import * 
import platform

#keras parameters
training = True

# solver params
res = 64
gs = vec3(res,res,1)
s = Solver(name='main', gridSize = gs, dim=2)
s.timestep = 2
timings = Timings()

# prepare grids
flags = s.create(FlagGrid)
vel = s.create(MACGrid)
density = s.create(RealGrid)
pressure = s.create(RealGrid)

bWidth=1
alpha=0.5
flags.initDomain(boundaryWidth=bWidth) 
flags.fillGrid()

setOpenBound(flags, bWidth,'yY',FlagOutflow|FlagEmpty) 

if (GUI):
	gui = Gui()
	gui.show( True ) 
	#gui.pause()

source = s.create(Cylinder, center=gs*vec3(0.5,0.1,0.5), radius=res*0.14, z=gs*vec3(0, 0.02, 0))

#keras

model = Sequential()
model.add(UpSampling2D(size=(2,2), input_shape=(64,64,4)))
model.add(Convolution2D(1,8,1,activation='relu'))
mantaMsg(str(model.output_shape))
model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])



	
#main loop
for t in range(500):
	#mantaMsg('\nFrame %i' % (s.frame))

	if t<300:
		source.applyToGrid(grid=density, value=1)
		
	advectSemiLagrange(flags=flags, vel=vel, grid=density, order=2) 
	advectSemiLagrange(flags=flags, vel=vel, grid=vel,     order=2, openBounds=True, boundaryWidth=bWidth)
	
	resetOutflow(flags=flags,real=density) 
	#diffuseTemperatureExplicit(flags, density, alpha)
	#diffuseTemperatureImplicit(flags, density, alpha)

	setWallBcs(flags=flags, vel=vel)    
	addBuoyancy(density=density, vel=vel, gravity=vec3(0,-4e-3,0), flags=flags)

	solvePressure(flags=flags, vel=vel, pressure=pressure)
	
	#timings.display()    
	#gui.screenshot('plumeInstable\plume_%04d.png' % t) 
	s.step()
