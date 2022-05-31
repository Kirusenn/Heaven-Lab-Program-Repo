# Nema17
# 200 steps per rotation
# 1.8 degrees per steps
# 1.2A/phase
# 3.4Ohm/phase
# Needed power: (1.2*2) * (3.4*2+0.5) + 0.5 = 18.02V, 2.4A minimum.
# Max current = 1.2A

from Phidget22.Phidget import *
from Phidget22.Devices.Stepper import *
import time

steps_per_rotation = 200 # Number of rotations per step for the Nema17

rots_per_second = 1/16/steps_per_rotation # The 1/16 facter is because the default Phidget scale factor is in 1/16 step per second
rots_per_minute = rots_per_second * 60
steps_per_shot = 1/(16*20)

timeout = 0
target_rpm_scale = 850
target_sps_scale = target_rpm_scale / rots_per_minute * steps_per_shot

target = target_sps_scale
current = 0.8
velocity = 1/13

pos_threshold = 0.05

RUN = True

# Pause motor motion
def pause(ch):
	if not ch.getIsMoving(): # Return if motor is already paused
		return
	ch.setVelocityLimit(0)
	print('Motor paused!\n')
	
# Resume motor motion
def run(ch):
	# if ch.getIsMoving(): # Return if motor is already moving
		# return
	RUN = True
	ch.setEngaged(True)
	print('Motor running!\n')

# PositionChangedHandler; controls reversal of motor once it has reached the set limits
def onPositionChange(self, position):
	# print(position)
	if abs(position - target) <= pos_threshold and RUN:
		self.setTargetPosition(0)
	if position <= pos_threshold and RUN:
		self.setTargetPosition(target)

# Stops movement and moves motor to zero position, disengaging afterward
def go_home(ch):
	print('Moving to home position; please wait...\n')
	RUN = False
	ch.setVelocityLimit(0)
	tmp = ch.getRescaleFactor()
	ch.setRescaleFactor(rots_per_minute)
	ch.setControlMode(StepperControlMode.CONTROL_MODE_STEP)
	ch.setTargetPosition(0)
	ch.setVelocityLimit(300)
	while ch.getIsMoving():
		time.sleep(0.050)
	ch.setEngaged(False)
	ch.setRescaleFactor(tmp)
	print('Motor parked in home position!\n')

def main():
	# Create and attach to Stepper
	ch = Stepper()
	ch.openWaitForAttachment(timeout)
	
	# Set scale factor
	# ch.setRescaleFactor(rots_per_minute)
	ch.setRescaleFactor(steps_per_shot)
	
	# Set current limit
	ch.setCurrentLimit(current)
	
	# Set velocity limit
	ch.setVelocityLimit(velocity)
	
	# Set PositionChangedHandler
	ch.setOnPositionChangeHandler(onPositionChange)
	
	# CONTROL_MODE_RUN runs motor at constant velocity
	# ch.setControlMode(StepperControlMode.CONTROL_MODE_RUN)
	
	# Zero the current position; ideally this should never change, and should be near one extremum of the rod
	ch.addPositionOffset(-ch.getPosition())
	
	ch.setTargetPosition(target)
	
	# Listen for keystrokes
	while True:
		try:
			command = input('Command: ')
			if len(command) == 0:
				continue
				
			match command:
				case 'p' | 'pause':
					pause(ch)
				case 'r' | 'resume' | 'run':
					run(ch)
				case 'q' | 'quit':
					go_home(ch)
					print('Closing program...\n')
					break
				case _:
					print('That is not a command!\n')
					continue
			
			#elif (command == 'p') or (command == 'pause'):
			#	pause(ch)
			#elif (command == 'r') or (command == 'resume') or (command == 'run'):
			#	run(ch)
			#elif (command == 'q') or (command == 'quit'):
			#	go_home(ch)
			#	print('\nClosing program...')
			#	break
			#else:
			#	print('That is not a command!')
			#	continue
			
		# Interrupt will move the motor back to the zero position and close Phidget tools before exiting
		except KeyboardInterrupt:
			print('\nKeyboard interrupt detected!\n')
			go_home(ch)
			break
	
	input('\nExiting...\n')
	ch.close()
	Phidget.finalize(0)
	sys.exit()

# Run program	
main()
