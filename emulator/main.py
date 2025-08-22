import os
import pygame
import pydirectinput
import vgamepad as vg

script_dir = os.path.dirname(os.path.abspath(__file__))
sound_path = os.path.join(script_dir, "click.mp3")

pygame.init()
pygame.joystick.init()
gamepad = vg.VX360Gamepad()
pygame.mixer.music.load(sound_path)

def pedal_to_trigger(value: float) -> int:
    return int(((1.0 - value) / 2.0) * 255)

def axis_to_stick(value):
    return int(value * 32767)

for joystickIndex in range(pygame.joystick.get_count()):
    print(f"[{joystickIndex}]", pygame.joystick.Joystick(joystickIndex).get_name())

chosenInput = int(input("Choose your steering wheel: "))
chosenInput2 = int(input("Choose your shifter: "))
joystick = pygame.joystick.Joystick(chosenInput)
joystick2 = pygame.joystick.Joystick(chosenInput2)

gearMap = {}
buttonMap = {}
switchButton = 0

gearCount = int(input("Enter how many gears you have NOT including reverse: "))+1

for gearIndex in range(gearCount):
    actualGear = gearIndex+1
    input(f"\nShift into {actualGear if actualGear < gearCount else 'Reverse'} gear and press ENTER: ")

    pygame.event.pump()
    pressed_buttons = [i for i in range(joystick2.get_numbuttons()) if joystick2.get_button(i)]
    
    if pressed_buttons:
        button_id = pressed_buttons[0]
        gearMap[gearIndex] = button_id
        print(f"Mapped gear {actualGear if actualGear < gearCount else 'Reverse'} to joystick button {button_id}")

input("\nHold button for switching into 2nd shift group and press ENTER: ")
pygame.event.pump()
pressed_buttons = [i for i in range(joystick.get_numbuttons()) if joystick.get_button(i)]
if pressed_buttons:
    button_id = pressed_buttons[0]
    switchButton = button_id
    print(f"Mapped switching shift group button to joystick button {button_id}")

YesOrNo2 = input("\nWhen switching shift groups would you like it to make a click sound (this is because sometimes it doesn't register the press)? Y/N ").lower()
switchSound = False
if YesOrNo2 == "y":
    switchSound = True

YesOrNo = input("\nPlanning to bind custom buttons to roblox keys? Write Y/N: ").lower()
if YesOrNo == "y":
    AmountOfButtons = int(input("How many buttons are you gonna bind: "))
    for buttonIndex in range(AmountOfButtons):
        input(f"\nHold joystick button for button {buttonIndex+1} and press ENTER: ")
        pygame.event.pump()
        pressed_buttons = [i for i in range(joystick.get_numbuttons()) if joystick.get_button(i)]
        
        if pressed_buttons:
            button_id = pressed_buttons[0]
            buttonMap[button_id] = input(f"Enter roblox key that joystick {button_id} will do: ")
            print(f"Mapped button {buttonIndex} to joystick button {button_id} to press {buttonMap[button_id]}")

input("\nHold down your clutch hold your throttle in half and turn steering wheel to center and press ENTER: ")
pygame.event.pump()
for axisIndex in range(joystick.get_numaxes()):
    print(f"[{axisIndex}]", joystick.get_axis(axisIndex))

print("\nIf you cant decide which is which, usually devices axis go in same order as you are entering.")
chosenAxis2 = int(input("\nChoose your steering axis: "))
chosenAxis4 = int(input("\nChoose your throttle axis: "))
chosenAxis3 = int(input("\nChoose your brake axis: "))
chosenAxis = int(input("\nChoose your clutch axis: "))

currentGear = 0
physicalGear = 0
switchedGroup = False
lastSwitched = False
delayMap = {}

print("\nManual script initialized, enjoy! Make sure you start from neutral inside roblox. Transmission Tye can be either Manual or Semi, both work.")
print("\nIf your gear is missaligned, switch it with keyboard. It's not recommended to skip gears if you have high cpu usage (lag can cause gear to not shift correctly).")
print("\nTheres no neutral shifting at the moment as its not possible with a chassis and work around is not efficent.")

while True:
    pygame.event.pump()

    clutchValue = joystick.get_axis(chosenAxis)
    clutchPressed = clutchValue < -0.5

    if clutchPressed:
        pydirectinput.keyDown("shiftleft")
    else:
        pydirectinput.keyUp("shiftleft")

    if joystick.get_button(switchButton):
        if lastSwitched == False:
            switchedGroup = not switchedGroup
            print(switchedGroup)
            if switchSound == True:
                pygame.mixer.music.play()
            lastSwitched = True
    else:
        if lastSwitched == True:
            lastSwitched = False
        
    steer = axis_to_stick(joystick.get_axis(chosenAxis2))
    gamepad.left_joystick(x_value=steer, y_value=0)

    throttle = pedal_to_trigger(joystick.get_axis(chosenAxis4))
    gamepad.right_trigger(value=throttle)

    brake = pedal_to_trigger(joystick.get_axis(chosenAxis3))
    gamepad.left_trigger(value=brake)
    
    for button_id, key in buttonMap.items():
        pressed = joystick.get_button(button_id)

        if pressed:
            if not delayMap.get(button_id, False):
                pydirectinput.keyDown(key)
                print(f"Key down: {key}")
                delayMap[button_id] = True
        else:
            if delayMap.get(button_id, False):
                pydirectinput.keyUp(key)
                print(f"Key up: {key}")
                delayMap[button_id] = False


    for gear, button_id in gearMap.items():
        if joystick2.get_button(button_id):
            if clutchPressed:
                actualGear = gear+1
                if actualGear == gearCount: # Reverse
                    if currentGear != -1:
                        print("R")
                    currentGear = -1
                    howMany = physicalGear-currentGear 
                    for index in range(howMany): 
                        pydirectinput.press("q") 
                elif actualGear != currentGear:
                        if switchedGroup:
                            if currentGear != actualGear+(gearCount-1):
                                print(actualGear+(gearCount-1))
                            currentGear = actualGear+(gearCount-1)
                        else:
                            print(actualGear)
                            currentGear = actualGear
                        if currentGear >= physicalGear: 
                            howMany = currentGear-physicalGear 
                            for index in range(howMany): 
                                pydirectinput.press("e")
                        else: 
                            howMany = physicalGear-currentGear 
                            for index in range(howMany): 
                                pydirectinput.press("q") 
                physicalGear = currentGear
    gamepad.update()

pygame.quit()