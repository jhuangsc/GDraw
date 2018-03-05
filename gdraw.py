# Jonathan Huang (ICS2O1-02)
# Created December 11 2009
# GDraw - ICS Summative

# A basic computer graphics program. Intended to be somewhat similar to programs like MS Paint.

import pygame, sys, os, time
from pygame.locals import * 
from random import randint

from WriteFile import WriteText # CREDITS TO GARY ZENG 
# WriteText(Text,Font,Color,Location,MaxPerLine,LineSpace=5,Justify=False,Indent=0)

import platform
if platform.system() == "Windows": os.environ['SDL_VIDEODRIVER'] = 'windib'

os.system('Color 0F')

def Attributes(File):
    # Function to retrieve certain settings from a .ini file
    for line in File:
        if "CANVAS_WIDTH" in line:
            CANVAS_WIDTH = int(line[line.find("=")+1:].replace("\n",""))
        elif "CANVAS_HEIGHT" in line:
            CANVAS_HEIGHT = int(line[line.find("=")+1:].replace("\n",""))
        elif "PENCIL_OFFSET" in line:
            PENCIL_OFFSET = int(line[line.find("=")+1:].replace("\n",""))
    return CANVAS_WIDTH, CANVAS_HEIGHT, PENCIL_OFFSET
Config = open("gdraw_config.ini","r").readlines()
Settings = Attributes(Config)

# Setting some minimum, uh, settings to try and prevent errors
if Settings[0] < 480: Settings[0] = 480
if Settings[1] < 360: Settings[1] = 410
if Settings[2] < 1: Settings[2] = 1

pygame.init() 

Img_Icon = pygame.image.load("ui/gdraw_icon.png")
pygame.display.set_icon(Img_Icon)
window = pygame.display.set_mode((Settings[0], Settings[1]+50)) # , pygame.RESIZABLE
pygame.display.set_caption('GDraw - Beta') 
TheFont = pygame.font.SysFont("Courier", 10)

"""
TOOLBAR IMAGES
"""
Toolbar_Base = pygame.image.load("ui/gdraw_Image_ToolbarButtons.png")
Toolbar_Tools = pygame.image.load("ui/gdraw_Image_ToolbarTools.png")
Toolbar_Button = pygame.image.load("ui/gdraw_Image_ButtonPressed.png")
Toolbar_ButtonNeutral = pygame.image.load("ui/gdraw_Image_ButtonNeutral.png")
Toolbar_ButtonNeutral2 = pygame.image.load("ui/gdraw_Image_ButtonNeutral2.png")
PencilTools = pygame.image.load("ui/gdraw_Image_PencilTools.png")
EraserTools = pygame.image.load("ui/gdraw_Image_EraserTools.png")
FillTools = pygame.image.load("ui/gdraw_Image_FillTools.png")

# Preview shows the position of a drawing tool before actually drawing it
# Canvas is the main drawing area. Default color is white
# Toolbar contains buttons for individual tools and functions
# SubToolbar contains buttons for functions specific to certain tools
# InfoBar displays information such as canvas size, position of cursor on canvas, and descriptions of tools on mouseover - not used yet
# Screen is what is displayed, and everything else is drawn on it 

Preview = pygame.Surface((Settings[0], Settings[1]+50),pygame.SRCALPHA) # displays pencil/eraser/shape/etc previews 
Toolbar = pygame.image.load("ui/gdraw_Image_Toolbar.png").convert_alpha() # toolbar image
SubToolbar = pygame.image.load("ui/gdraw_Image_SubToolbarBase.png").convert_alpha() # toolbar buttons specific to certain tools
InfoBar = pygame.display.get_surface() # bar beside toolbar storing various tool info
Canvas = pygame.Surface((Settings[0], Settings[1]+50)) # saves what has been drawn 
Screen = pygame.display.get_surface() # Used to display everything

#==============================================================================#

running = True
""" 
Possible modes:
  Pencil, Eraser, Eyedropper, Selector, Fill, Line
  Shape(_Rectangle, _Square, _Circle, _Ellipse)
  Attributes
"""
Ruler = False # allows for drawing in a straight line
RulerX = False # prevents the pencil from drawing vertically until shift is released
SavedX = 0 # stores the X position of the cursor at the moment shift is pressed
RulerY = False # same as RulerX but for vertical 
SavedY = 0 # same as SavedX
Color = (127,127,127) # RGB color that all tools except Eraser will draw with

Mode = "Pencil"

Preview.fill((255,255,255,0))
Preview.set_alpha(0)
Canvas.fill((255,255,255,255))
Screen.fill((255,255,255,255))
Toolbar.fill(Color, (192,6,14,14)) #Displays the current color in the Palette button

#==============================================================================#

"""
PENCIL MODE (hotkey B)
    PencilType is the shape of the pencil 'brush'. Supported are circle/square
    PencilSize is the radius of the pencil, in pixels. Hotkeys are 1-8 and 0 on 
  the number line. Otherwise this can be set via the Pencil Size button.
    PencilOffset is the space between each pencil offset in pixels. This can be
  set through the Pencil Offset button. 
    AlwaysDraw, if True, draws wherever the cursor moves, without needing the
  user to click. Tab hotkey toggles this mode, otherwise this can be toggled via
  the Always Draw button. 
    PencilColorSet - if Normal, the colors used are what the user chooses. If
  Random, the colors are completely random. 
    Pencils - The number of pencils that will be used. Compare numbers to the
  number pad to see the position of the pencils.
    PencilSizeDict is used to change the eraser size using hotkeys 1~0
"""
PencilType = "Circle"
PencilSize = 8
PencilOffset = Settings[2]
PencilBorder = 0
AlwaysDraw = 0
PencilColorSet = "Normal"
Pencils = ["5"]
PencilOffsetDict = {K_KP1:"1", K_KP2:"2", K_KP3:"3", K_KP4:"4", K_KP5:"5", K_KP6:"6", K_KP7:"7", K_KP8:"8", K_KP9:"9"}
PencilSizeDict = {K_1:2, K_2:4, K_3:6, K_4:8, K_5:10, K_6:12, K_7:16, K_8:20, K_9:30, K_0:50}
"""
ERASER MODE (hotkey E)
    EraserSize is the radius of the 'pencil', in pixels. Hotkeys are the same
  as for the Pencil. Otherwise this can be set via the Eraser Size button.
    EraserType is the shape of the eraser. "Circle" or "Square"
    AlwaysErase is similar to the AlwaysDraw mode of the Pencil tool. Toggled
  using Tab as well, or via the Always Erase button.
    EraserSizeDict is used to change the eraser size using hotkeys 1~0
"""
EraserSize = 5
EraserType = "Circle"
AlwaysErase = 0
EraserSizeDict = {K_1:2, K_2:4, K_3:6, K_4:8, K_5:10, K_6:12, K_7:16, K_8:20, K_9:30, K_0:50}
"""
EYEDROPPER MODE (hotkey I)
    EyedropperStarted prevents the eyedropper from running multiple times per click
"""
EyedropperStarted = False
"""
PALETTE MODE (hotkey P)
    Palette_Values is used to store input numbers until they are converted to RGB
    PaletteDict is used to input numbers into Palette_Values
"""
Palette_Values = ""
PaletteDict = {K_1:"1", K_2:"2", K_3:"3", K_4:"4", K_5:"5", K_6:"6", K_7:"7", K_8:"8", K_9:"9", K_0:"0"}
"""
MARQUEE ERASER MODE (hotkey W)
    SelectorStarted is essential for the tool's function and for its preview
"""
SelectorStarted = False
"""
FILL MODE (hotkey F)
    FillTolDict is used when inputting numbers to change fill tolerance
    FillTolerance is a % representing the maximum deviance in a pixel's color from
  the origin point where the pixel will still be filled
"""
FillTolDict = {K_1:0.10, K_2:0.20, K_3:0.30, K_4:0.40, K_5:0.50, K_6:0.60, K_7:0.70, K_8:0.80, K_9:0.90, K_0:0.00, K_EQUALS:1.00}
FillTolerance = 0.10
"""
LINE MODE (hotkey Alt+L)
    LineWidth is the width of the line. Hotkeys to change the width are 1-0.
    LineStarted is set to True when the first point is set, False when it is finished
    LineWidthDict is used to set the width of the line
"""
LineWidth = 1
LineStarted = False
LineWidthDict = {K_1:1, K_2:2, K_3:3, K_4:4, K_5:5, K_6:6, K_7:7, K_8:8, K_9:9, K_0:10}
"""
RECTANGLE MODE (hotkey R)
    RectStarted is set to True when the start point is set, False when it is finished
    RectType - 0 is filled, 1 is an outline with a width of 1 pixel
"""
RectStarted = False
RectType = 0 
"""\
SQUARE MODE (hotkey S)
    Variables are identical to the Rect equivalents
"""
SquareStarted = False
SquareType = 0
"""
ELLIPSE MODE (hotkey O)
    Variables are identical to the Rect equivalents
"""
EllipseStarted = False
EllipseType = 0
"""
Circle Mode (hotkey C)
    Variables are identical to the Rect equivalents
"""
CircleStarted = False
CircleType = 0
"""
"""
#Dictionary used when drawing sub-toolbar buttons
ButtonPosDict = {"1":(215,2), "2":(237,2), "3":(260,2), "4":(283,2), "5":(306,2),
                 "6":(215,25), "7":(237,25), "8":(260,25), "9":(283,25), "10":(306,25)}

#==============================================================================#

def SwitchMode(Tool):
    global Mode, ToolClicked
    UpdatePreview()
    Toolbar.blit(Toolbar_Base.convert(), (0,0)) # Clears the toolbar area before drawing the clicked button    
    if Tool == "Pencil":
        Mode = "Pencil"
        Toolbar.blit(Toolbar_Button.convert(), (2,2))        
        print "TOOL - Mode set to Pencil"
    elif Tool == "Eraser":
        Mode = "Eraser"
        Toolbar.blit(Toolbar_Button.convert(), (25,2))
        print "TOOL - Mode set to Eraser"
    elif Tool == "Eyedropper":
        Mode = "Eyedropper"
        Toolbar.blit(Toolbar_Button.convert(), (48,2))
        print "TOOL - Mode set to Eyedropper"
    elif Tool == "Palette":
        Mode = "Palette"
        Toolbar.blit(Toolbar_Button.convert(), (188,2))
        print "TOOL - Palette opened"
    elif Tool == "Marquee Eraser":
        Mode = "Marquee Eraser"
        Toolbar.blit(Toolbar_Button.convert(), (94,2))
        print "TOOL - Marquee Eraser selected"
    elif Tool == "Fill":
        Mode = "Fill"
        Toolbar.blit(Toolbar_Button.convert(), (71,2))
        print "TOOL - Mode set to Fill"
    elif Tool == "Line":
        Mode = "Line"
        Toolbar.blit(Toolbar_Button.convert(), (2,25))
        print "TOOL - Mode set to Line"
    elif Tool == "Circle":
        Mode = "Shape_Circle"
        Toolbar.blit(Toolbar_Button.convert(), (25,25))
        print "TOOL - Mode set to Shape, Circle"
    elif Tool == "Ellipse":
        Mode = "Shape_Ellipse"
        Toolbar.blit(Toolbar_Button.convert(), (48,25))
        print "TOOL - Mode set to Shape, Ellipse"
    elif Tool == "Square":
        Mode = "Shape_Square"
        Toolbar.blit(Toolbar_Button.convert(), (71,25))
        print "TOOL - Mode set to Shape, Square"
    elif Tool == "Rectangle":
        Mode = "Shape_Rectangle"
        Toolbar.blit(Toolbar_Button.convert(), (94,25))
        print "TOOL - Mode set to Shape, Rectangle"
    Toolbar.blit(Toolbar_Tools.convert_alpha(), (0,0))
    SubToolbar.fill((255,255,255), (212,0,119,50))
    ToolClicked = True
        
def Pencil_Draw(Surface,Shape,ColorType,Circ,Rect,Radius,Fill):
    # Function to draw using the pencil tool more efficiently than the previously used method
    if Shape == "Circle": pygame.draw.circle(Surface,ColorType,Circ,abs(Radius/2),Fill)
    elif Shape == "Square": pygame.draw.rect(Surface,ColorType,Rect,Fill)
    
def Eraser_Erase(Surface,Shape,Circ,Rect,Radius):
    # Function to erase a bit more efficiently
    if Surface == Preview: 
        if Shape == "Circle": pygame.draw.circle(Preview,(0,0,0),Circ,abs(EraserSize/2),1)
        elif Shape == "Square": pygame.draw.rect(Preview,(0,0,0),Rect,1)
    elif Surface == Canvas:
        if Shape == "Circle": pygame.draw.circle(Canvas,(255,255,255),Circ,abs(EraserSize/2),0)
        elif Shape == "Square": pygame.draw.rect(Canvas,(255,255,255),Rect,0)
        
def UpdatePencils(NumStr):
    # Function to add/remove pencil offsets using the number pad
    Dir = {"1":"Southwest", "2":"South", "3":"Southeast", "4":"West", "5":"Center", "6":"East", "7":"Northwest", "8":"North", "9":"Northeast"}
    if NumStr in Pencils:
        Pencils.pop(Pencils.index(NumStr))
        print "PENCIL - " + Dir[NumStr] + " pencil disabled"
    else:
        Pencils.append(NumStr)
        print "PENCIL - " + Dir[NumStr] + " pencil enabled"
        
def ChangePencilSize(Size):
    global PencilSize
    PencilSize = Size
    print "PENCIL - Pencil size changed to " + str(Size)
    
def ChangeEraserSize(Size):
    global EraserSize
    EraserSize = Size
    print "ERASER - Eraser size changed to " + str(Size)
    
def ChangeLineWidth(Width):
    global LineWidth
    LineWidth = Width
    print "LINE - Line width changed to " + str(Width)
    
def AddToPalette(NumStr):
    # Function used by the basic palette to add numbers to create an RGB value
    global Palette_Values
    Palette_Values += NumStr
    
def ChangeFillTolerance(FloatLessThanOne):
    global FillTolerance
    FillTolerance = FloatLessThanOne
    print "FILL - Tolerance changed to " + str(FloatLessThanOne*100) + "%"
    
def UpdatePreview():
    # Resets the Preview surface to blank, transparent
    Preview.fill((255,255,255,0))
    Preview.set_alpha(0)
    
def UpdateScreen(): 
    # Redraws all primary surfaces to the screen; surface.convert() greatly improves efficiency
    Canvas.fill((255,255,255), (0,0,Settings[0],49)) #Clears the canvas
    Screen.blit(Canvas.convert(), (0,0))
    Screen.blit(Preview.convert_alpha(), (0,0))
    Toolbar.fill(Color, (192,6,14,14)) #Displays the current color over the Palette button
    Screen.blit(Toolbar.convert_alpha(), (0,0))
    Screen.blit(SubToolbar.convert_alpha(), (0,0))
    Screen.blit(InfoBar.convert(), (0,0))
    pygame.display.update()
    
#==============================================================================#

# Crosshair-shaped custom cursor
Cursor_Strings = ("           +            ",
                  "         ++X++          ",
                  "       ++XXXXX++        ",
                  "     ++XX++X++XX++      ",
                  "    +XX++ +X+ ++XX+     ",
                  "   +X++   +X+   ++X+    ",
                  "   +X+    +X+    +X+    ",
                  "  +X+     +X+     +X+   ",
                  "  +X+     +X+     +X+   ",
                  " +X+     +XXX+     +X+  ",
                  " +X++++++X   X++++++X+  ",
                  "+XXXXXXXXX X XXXXXXXXX+ ",
                  " +X++++++X   X++++++X+  ",
                  " +X+     +XXX+     +X+  ",
                  "  +X+     +X+     +X+   ",
                  "  +X+     +X+     +X+   ",
                  "   +X+    +X+    +X+    ",
                  "   +X++   +X+   ++X+    ",
                  "    +XX++ +X+ ++XX+     ",
                  "     ++XX++X++XX++      ",
                  "       ++XXXXX++        ",
                  "         ++X++          ",
                  "           +            ",
                  "                        ")
Cursor_Data = pygame.cursors.compile(Cursor_Strings,"+","X","O") # + is white, X is black
pygame.mouse.set_cursor((24,24),(11,11),Cursor_Data[0],Cursor_Data[1])
SwitchMode("Pencil")

#==============================================================================#

while running:
    #Background.fill((128,128,128))
    Events = pygame.event.get()
    
    ButtonPosDict = {"1":(215,2), "2":(238,2), "3":(261,2), "4":(284,2), "5":(307,2),
                     "6":(215,25), "7":(238,25), "8":(261,25), "9":(284,25), "10":(307,25)}
        
    # Draws sub-toolbar buttons
    if Mode == "Pencil":
        SubToolbar.fill((200,200,200), (212,0,119,50))
        ButtonList = ["1", "2", "3", "4", "5", 
                      "6", "7", "8", "9"]
        for Number in ButtonList: SubToolbar.blit(Toolbar_ButtonNeutral2, ButtonPosDict[Number])
        if AlwaysDraw == True: SubToolbar.blit(Toolbar_Button, ButtonPosDict["9"])
        if PencilBorder == 0: SubToolbar.blit(Toolbar_Button, ButtonPosDict["2"]) 
        elif PencilBorder == 1: SubToolbar.blit(Toolbar_Button, ButtonPosDict["3"]) 
        if PencilType == "Circle": SubToolbar.blit(Toolbar_Button, ButtonPosDict["4"]) 
        elif PencilType == "Square": SubToolbar.blit(Toolbar_Button, ButtonPosDict["5"])
        if PencilColorSet == "Normal": SubToolbar.blit(Toolbar_Button, ButtonPosDict["7"]) 
        elif PencilColorSet == "Random": SubToolbar.blit(Toolbar_Button, ButtonPosDict["8"]) 
        SubToolbar.blit(PencilTools, (213,0))
    elif Mode == "Eraser":
        SubToolbar.fill((200,200,200), (212,0,70,50))
        ButtonList = ["1", "2", "3", 
                      "6", "7"]
        for Number in ButtonList: SubToolbar.blit(Toolbar_ButtonNeutral2, ButtonPosDict[Number])
        if AlwaysErase == True: SubToolbar.blit(Toolbar_Button, ButtonPosDict["7"])
        if EraserType == "Circle": SubToolbar.blit(Toolbar_Button, ButtonPosDict["2"])
        elif EraserType == "Square": SubToolbar.blit(Toolbar_Button, ButtonPosDict["3"])
        SubToolbar.blit(EraserTools, (213,0))        
    elif Mode == "Eyedropper":
        ButtonList = ["1"]
        for Number in ButtonList: SubToolbar.blit(Toolbar_ButtonNeutral2, ButtonPosDict[Number])
        SubToolbar.fill(Canvas.get_at((MouseX,MouseY)), (221,8,10,10))
    elif Mode == "Fill":
        ButtonList = ["1",
                      "6"]
        for Number in ButtonList: SubToolbar.blit(Toolbar_ButtonNeutral2, ButtonPosDict[Number])
        SubToolbar.blit(FillTools, (213,0))
    
    #==========================================================================#
    
    for event in Events: # The majority of code is within this loop due to the input-centric nature of the program
        MousePos = pygame.mouse.get_pos()
        Buttons = pygame.mouse.get_pressed()
        MouseX = MousePos[0]
        MouseY = MousePos[1]
        KeyMod = pygame.key.get_mods()
        
        # ESC to exit
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE): running = False                 
            
        # Shortcuts for various tools and functions
            # notes for KeyMods
            # 4097 = left Shift, 4098 = right Shift
            # 4160 = left Ctrl, 4224 = right Ctrl
            # 4352 = left Alt, 4608 = right Alt
            
        """ Toolbar buttons for GUI plus basic hotkeys """        
        """ B for Pencil, E for Eraser, I for Eyedropper, P for Palette, S for Selector, F for Fill. Toolbar buttons included """
            
        if ((event.type == KEYDOWN and event.key == K_b and KeyMod == 4096) or (MousePos[0] >2 and MousePos[0] <23 and MousePos[1] >2 and MousePos[1] <23 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Pencil": 
            SwitchMode("Pencil")
        elif ((event.type == KEYDOWN and event.key == K_e and KeyMod == 4096) or (MousePos[0] >25 and MousePos[0] <46 and MousePos[1] >2 and MousePos[1] <23 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Eraser": 
            SwitchMode("Eraser")
        elif ((event.type == KEYDOWN and event.key == K_i and KeyMod == 4096) or (MousePos[0] >48 and MousePos[0] <69 and MousePos[1] >2 and MousePos[1] <23 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Eyedropper": 
            SwitchMode("Eyedropper")
        elif ((event.type == KEYDOWN and event.key == K_p and KeyMod == 4096) or (MousePos[0] >188 and MousePos[0] <209 and MousePos[1] >2 and MousePos[1] <23 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Palette": 
            SwitchMode("Palette")
        elif ((event.type == KEYDOWN and event.key == K_w and KeyMod == 4096) or (MousePos[0] >94 and MousePos[0] <115 and MousePos[1] >2 and MousePos[1] <23 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Marquee Eraser": 
            SwitchMode("Marquee Eraser")
        elif ((event.type == KEYDOWN and event.key == K_f and KeyMod == 4096) or (MousePos[0] >71 and MousePos[0] <92 and MousePos[1] >2 and MousePos[1] <23 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Fill": 
            SwitchMode("Fill")
        
        """ Alt+L for Line, Alt+C for Circle, Alt+E for Ellipse, Alt+S for Square, Alt+R for Rectangle. Toolbar buttons included. """
        
        if ((event.type == KEYDOWN and event.key == K_l and KeyMod == 4096) or (MousePos[0] >2 and MousePos[0] <23 and MousePos[1] >25 and MousePos[1] <46 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Line": 
            SwitchMode("Line")
        elif ((event.type == KEYDOWN and event.key == K_c and KeyMod == 4096) or (MousePos[0] >25 and MousePos[0] <46 and MousePos[1] >25 and MousePos[1] <46 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Shape_Circle": 
            SwitchMode("Circle")
        elif ((event.type == KEYDOWN and event.key == K_o and KeyMod == 4096) or (MousePos[0] >48 and MousePos[0] <69 and MousePos[1] >25 and MousePos[1] <46 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Shape_Ellipse": 
            SwitchMode("Ellipse")
        elif ((event.type == KEYDOWN and event.key == K_s and KeyMod == 4096) or (MousePos[0] >71 and MousePos[0] <92 and MousePos[1] >25 and MousePos[1] <46 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Shape_Square": 
            SwitchMode("Square")
        elif ((event.type == KEYDOWN and event.key == K_r and KeyMod == 4096) or (MousePos[0] >94 and MousePos[0] <115 and MousePos[1] >25 and MousePos[1] <46 and Buttons[0] == 1)) and ToolClicked == False and Mode != "Shape_Rectangle": 
            SwitchMode("Rectangle")
            
        """ Ctrl+N for New Canvas, Ctrl+S for Save, Ctrl+O for Open, Ctrl+X for Cut, Ctrl+C for Copy, Ctrl+V for Paste. Toolbar buttons included. """ 
        
        # Resets canvas to white
        if (event.type == KEYDOWN and event.key == K_n and KeyMod == (4160 or 4224)) or (MousePos[0] >119 and MousePos[0] <140 and MousePos[1] >2 and MousePos[1] <23 and Buttons[0] == 1) and ToolClicked == False:
            Canvas.fill((255,255,255)) 
            UpdatePreview()
            ToolClicked = True
        
        # Saves the canvas as a PNG with a random 12 character filename prefixed by "g_"
        # Need to implement 'proper' saving eventually
        elif (event.type == KEYDOWN and event.key == K_s and KeyMod == (4160 or 4224)) or (MousePos[0]>165 and MousePos[0]<186 and MousePos[1]>2 and MousePos[1]<23 and Buttons[0] == 1) and ToolClicked == False: 
            ToolClicked = True
            NewFileName = ""
            # Generates a random filename
            while len(NewFileName) < 12:
                ListChars = [chr(randint(65,90)), chr(randint(97,122)), chr(randint(48,57))] # can generate any of nums 0~9 and capital/lowercase letters
                NewFileName += ListChars[randint(0,2)]
                
            # Creates a new surface from the canvas, removing the white area used for the toolbar/infobar
            ToSave = pygame.Surface((Settings[0],Settings[1]-50))
            ToSave.blit(Canvas,(0,0,Settings[0],Settings[1]-50),(0,50,Settings[0],Settings[1]-50) )
            
            pygame.image.save(ToSave, "g_"+NewFileName+".png")
            print "FUNCTION - Image saved as g_"+NewFileName+".png"
            
        elif (event.type == KEYDOWN and event.key == K_o and KeyMod == (4160 or 4224)) or (MousePos[0]>142 and MousePos[0]<163 and MousePos[1]>2 and MousePos[1]<23 and Buttons[0] == 1) and ToolClicked == False: 
            print "OPEN - test success" # Placeholder for Open
            ToolClicked = True
        
        elif (event.type == KEYDOWN and event.key == K_x and KeyMod == (4160 or 4224)) or (MousePos[0]>119 and MousePos[0]<140 and MousePos[1]>25 and MousePos[1]<46 and Buttons[0] == 1) and ToolClicked == False: 
            print "CUT - test success" # Placeholder for Cut
            ToolClicked = True
        
        elif (event.type == KEYDOWN and event.key == K_c and KeyMod == (4160 or 4224)) or (MousePos[0]>142 and MousePos[0]<163 and MousePos[1]>25 and MousePos[1]<46 and Buttons[0] == 1) and ToolClicked == False: 
            print "COPY - test success" # Placeholder for Copy
            ToolClicked = True
        
        elif (event.type == KEYDOWN and event.key == K_v and KeyMod == (4160 or 4224)) or (MousePos[0]>165 and MousePos[0]<186 and MousePos[1]>25 and MousePos[1]<46 and Buttons[0] == 1) and ToolClicked == False: 
            print "PASTE - test success" # Placeholder for Paste
            ToolClicked = True
            
        elif (MousePos[0] >188 and MousePos[0] <209 and MousePos[1] >25 and MousePos[1] <46 and Buttons[0] == 1) and ToolClicked == False:
            print "OPTIONS - test success" # Placeholder for Options
            ToolClicked = True

        #======================================================================#
        
        #======================================================================#
        
        if Buttons[0] == 0 and ToolClicked == True: ToolClicked = False
        
        # Cuts off the canvas where the toolbar/infobar are
        if MouseY < 49: MouseY = 49 
        
        if Ruler == True:
            # Note - for now you can only draw straight horizontally/vertically around the origin point until you release Shift
            if (MouseX != SavedX) and RuledY == False: 
                MouseY = SavedY
                RuledX = True
            if (MouseY != SavedY) and RuledX == False: 
                MouseX = SavedX
                RuledY = True
                
        # Hold either Shift for the Ruler function, to draw in straight lines
        if (KeyMod == (4097 or 4098) or (event.type == KEYDOWN and event.key == (K_LSHIFT or K_RSHIFT))):
            if Ruler == False: # Doesn't save these positions unless the ruler was disabled
                SavedX = MouseX
                SavedY = MouseY
            Ruler = True
        else: 
            Ruler = False  
            RuledX = False
            RuledY = False
            
        #======================================================================#
        
        if ToolClicked == False: 
            
            if Mode == "Pencil":
                
                # Alt+3 switches to a filled pencil, Alt+4 switches to an outline pencil
                if ((Buttons[0] == 1 and MousePos[0]>238 and MousePos[0]<257 and MousePos[1]>2 and MousePos[1]<23) or (event.type == KEYDOWN and event.key == K_3 and KeyMod == (4352 or 4608))) and PencilBorder == 1: 
                    PencilBorder = 0
                    ToolClicked = True
                    print "PENCIL - Pencil border width set to 0 (filled)"
                elif ((Buttons[0] == 1 and MousePos[0]>261 and MousePos[0]<282 and MousePos[1]>2 and MousePos[1]<23) or (event.type == KEYDOWN and event.key == K_4 and KeyMod == (4352 or 4608))) and PencilBorder == 0: 
                    PencilBorder = 1
                    ToolClicked = True
                    print "PENCIL - Pencil border width set to 1 pixel"
                    
                # Alt+1 switches to a circular pencil, Alt+2 switches to a square pencil
                elif ((Buttons[0] == 1 and MousePos[0]>284 and MousePos[0]<305 and MousePos[1]>2 and MousePos[1]<23) or (event.type == KEYDOWN and event.key == K_1 and KeyMod == (4352 or 4608))) and PencilType == "Square": 
                    PencilType = "Circle"
                    ToolClicked = True
                    print "PENCIL - Pencil shape set to Circle"
                elif ((Buttons[0] == 1 and MousePos[0]>306 and MousePos[0]<327 and MousePos[1]>2 and MousePos[1]<23) or (event.type == KEYDOWN and event.key == K_2 and KeyMod == (4352 or 4608))) and PencilType == "Circle": 
                    PencilType = "Square"
                    ToolClicked = True
                    print "PENCIL - Pencil shape set to Square"
                    
                # Switches between a Normal color set and a Random color set
                elif (Buttons[0] == 1 and MousePos[0]>238 and MousePos[0]<259 and MousePos[1]>25 and MousePos[1]<46 and PencilColorSet == "Random"): 
                    PencilColorSet = "Normal"
                    ToolClicked = True
                    print "PENCIL - Pencil colors set to Normal"
                elif (Buttons[0] == 1 and MousePos[0]>261 and MousePos[0]<282 and MousePos[1]>25 and MousePos[1]<46 and PencilColorSet == "Normal"): 
                    PencilColorSet = "Random"
                    ToolClicked = True
                    print "PENCIL - Pencil colors set to Random"
                    
                # Tab toggles AlwaysDraw on and off
                elif (Buttons[0] == 1 and MousePos[0]>284 and MousePos[0]<305 and MousePos[1]>25 and MousePos[1]<46) or (event.type == KEYDOWN and event.key == K_TAB): 
                    ToolClicked = True
                    if AlwaysDraw == True: 
                        AlwaysDraw = False
                        print "PENCIL - Always Draw disabled"
                    elif AlwaysDraw == False: 
                        AlwaysDraw = True
                        print "PENCIL - Always Draw enabled"
                        
                # GUI buttons to increase/decrease pencil size
                if (Buttons[0] == 1 and MousePos[0]>216 and MousePos[0]<236 and MousePos[1]>2 and MousePos[1]<23): 
                    if PencilSize >= 100: print "PENCIL - Cannot increase pencil size further!"
                    elif PencilSize < 100: 
                        PencilSize += 1
                        print "PENCIL - Pencil size increased by 1 to " + str(PencilSize)
                elif (Buttons[0] == 1 and MousePos[0]>216 and MousePos[0]<236 and MousePos[1]>25 and MousePos[1]<46): 
                    if PencilSize <= 1: print "PENCIL - Cannot decrease pencil size further!"
                    elif PencilSize > 1: 
                        PencilSize -= 1
                        print "PENCIL - Pencil size decreased by 1 to " + str(PencilSize)
                
                # Dictionaries to improve efficiency with the drawing procedure
                
                PencilColorsDict = {"Normal":Color, "Random":(randint(0,255), randint(0,255), randint(0,255))}
                
                # XY values as tuples (X, Y) for drawing with a circle pencil
                P_CircDict = {"1":(MouseX-PencilOffset,MouseY+PencilOffset), "2":(MouseX, MouseY+PencilOffset), "3":(MouseX+PencilOffset,MouseY+PencilOffset), "4":(MouseX-PencilOffset,MouseY), "5":(MouseX,MouseY), "6":(MouseX+PencilOffset,MouseY), "7":(MouseX-PencilOffset,MouseY-PencilOffset), "8":(MouseX,MouseY-PencilOffset), "9":(MouseX+PencilOffset,MouseY-PencilOffset)}
                
                # TopLeftXY and Width/Height values as tuples(TL_X, TL_Y, width, height) for drawing with a square pencil
                P_RectDict = {"1":((MouseX-(PencilSize/2)-PencilOffset),(MouseY-(PencilSize/2)+PencilOffset),PencilSize,PencilSize), "2":((MouseX-(PencilSize/2)),(MouseY-(PencilSize/2)+PencilOffset),PencilSize,PencilSize), "3":((MouseX-(PencilSize/2)+PencilOffset),(MouseY-(PencilSize/2)+PencilOffset),PencilSize,PencilSize), "4":((MouseX-(PencilSize/2)-PencilOffset),(MouseY-(PencilSize/2)),PencilSize,PencilSize), "5":((MouseX-(PencilSize/2)),(MouseY-(PencilSize/2)),PencilSize,PencilSize), "6":((MouseX-(PencilSize/2)+PencilOffset),(MouseY-(PencilSize/2)),PencilSize,PencilSize), "7":((MouseX-(PencilSize/2)-PencilOffset),(MouseY-(PencilSize/2)-PencilOffset),PencilSize,PencilSize), "8":((MouseX-(PencilSize/2)),(MouseY-(PencilSize/2)-PencilOffset),PencilSize,PencilSize), "9":((MouseX-(PencilSize/2)+PencilOffset),(MouseY-(PencilSize/2)-PencilOffset),PencilSize,PencilSize)}
                
                # Preview - shows where the brush will be drawing. Does not activate if AlwaysDraw is enabled
                if AlwaysDraw == False:
                    UpdatePreview()
                    if "2" in Pencils: Pencil_Draw(Preview,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["2"],P_RectDict["2"],PencilSize,PencilBorder)
                    if "4" in Pencils: Pencil_Draw(Preview,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["4"],P_RectDict["4"],PencilSize,PencilBorder)
                    if "6" in Pencils: Pencil_Draw(Preview,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["6"],P_RectDict["6"],PencilSize,PencilBorder)
                    if "8" in Pencils: Pencil_Draw(Preview,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["8"],P_RectDict["8"],PencilSize,PencilBorder)
                    if "1" in Pencils: Pencil_Draw(Preview,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["1"],P_RectDict["1"],PencilSize,PencilBorder)
                    if "3" in Pencils: Pencil_Draw(Preview,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["3"],P_RectDict["3"],PencilSize,PencilBorder)
                    if "7" in Pencils: Pencil_Draw(Preview,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["7"],P_RectDict["7"],PencilSize,PencilBorder)
                    if "9" in Pencils: Pencil_Draw(Preview,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["9"],P_RectDict["9"],PencilSize,PencilBorder)
                    if "5" in Pencils: Pencil_Draw(Preview,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["5"],P_RectDict["5"],PencilSize,PencilBorder)
                
                # Left mouse button or none when Motion is toggled draw with the main pencil
                if (Buttons[0] == 1 and MousePos[1] > 48) or (event.type == MOUSEMOTION and AlwaysDraw == True): 
                    # The order of pencils makes it so the center pencil always draws on top of the others
                    # A special mode causes the pencil to draw with random colors. Otherwise the colors are user-chosen. 
                    if AlwaysDraw == False: ToolClicked == True
                    if "2" in Pencils: Pencil_Draw(Canvas,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["2"],P_RectDict["2"],PencilSize,PencilBorder)
                    if "4" in Pencils: Pencil_Draw(Canvas,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["4"],P_RectDict["4"],PencilSize,PencilBorder)
                    if "6" in Pencils: Pencil_Draw(Canvas,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["6"],P_RectDict["6"],PencilSize,PencilBorder)
                    if "8" in Pencils: Pencil_Draw(Canvas,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["8"],P_RectDict["8"],PencilSize,PencilBorder)
                    if "1" in Pencils: Pencil_Draw(Canvas,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["1"],P_RectDict["1"],PencilSize,PencilBorder)
                    if "3" in Pencils: Pencil_Draw(Canvas,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["3"],P_RectDict["3"],PencilSize,PencilBorder)
                    if "7" in Pencils: Pencil_Draw(Canvas,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["7"],P_RectDict["7"],PencilSize,PencilBorder)
                    if "9" in Pencils: Pencil_Draw(Canvas,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["9"],P_RectDict["9"],PencilSize,PencilBorder)
                    if "5" in Pencils: Pencil_Draw(Canvas,PencilType,PencilColorsDict[PencilColorSet],P_CircDict["5"],P_RectDict["5"],PencilSize,PencilBorder)
                    
                # Right mouse button draws with a single pencil as white if Always Draw is disabled
                elif Buttons[2] == 1 and AlwaysDraw == False:
                    pygame.draw.circle(Canvas, (255,255,255), (MouseX, MouseY), PencilSize/2)
                    ToolClicked == True
                    
                # 1~0 on the number line quickly set the pencil size
                if event.type == KEYDOWN and KeyMod == 4096 and event.key in PencilSizeDict:
                    ChangePencilSize(PencilSizeDict[event.key])
                    
                # 1~9 on the number pad toggle the pencil offsets
                if event.type == KEYDOWN and event.key in PencilOffsetDict:
                    UpdatePencils(PencilOffsetDict[event.key])
                    
            elif Mode == "Eraser":
                
                # Preview
                if AlwaysErase == False:
                    UpdatePreview()
                    Eraser_Erase(Preview,EraserType,(MouseX,MouseY),(MouseX-EraserSize/2,MouseY-EraserSize/2,EraserSize,EraserSize),abs(EraserSize/2))
                
                # 'Erases' with the current eraser shape 
                if (Buttons[0] == 1 or (event.type == MOUSEMOTION and AlwaysErase == True)) and MousePos[1] > 48: 
                    ToolClicked == True
                    Eraser_Erase(Canvas,EraserType,(MouseX,MouseY),(MouseX-EraserSize/2,MouseY-EraserSize/2,EraserSize,EraserSize),abs(EraserSize/2))
                
                # Tab key toggles Always Erase mode
                if (event.type == KEYDOWN and event.key == K_TAB) or (Buttons[0] == 1 and MousePos[0]>238 and MousePos[0]<259 and MousePos[1]>25 and MousePos[1]<46):
                    ToolClicked = True
                    if AlwaysErase == False: 
                        AlwaysErase = True
                        print "ERASER - Always Erase enabled"
                    elif AlwaysErase == True: 
                        AlwaysErase = False
                        print "ERASER - Always Erase disabled"
                
                # 1~0 on the number line quickly set the eraser size
                if event.type == KEYDOWN and event.key in EraserSizeDict and KeyMod == 4096:
                    ChangeEraserSize(EraserSizeDict[event.key])
                    
                # GUI buttons to increase/decrease pencil size
                if (Buttons[0] == 1 and MousePos[0]>216 and MousePos[0]<236 and MousePos[1]>2 and MousePos[1]<23): 
                    if EraserSize >= 100: print "ERASER - Cannot increase eraser size further!"
                    elif EraserSize < 100: 
                        EraserSize += 1
                        print "ERASER - Eraser size increased by 1 to " + str(EraserSize)
                elif (Buttons[0] == 1 and MousePos[0]>216 and MousePos[0]<236 and MousePos[1]>25 and MousePos[1]<46): 
                    if EraserSize <= 2: print "ERASER - Cannot decrease eraser size further!"
                    elif EraserSize > 2: 
                        EraserSize -= 1
                        print "ERASER - Eraser size decreased by 1 to " + str(EraserSize)
                    
                # Alt+1 and Alt+2 switch between Circle and Square erasers
                if ((event.type == KEYDOWN and event.key == K_1 and KeyMod == (4352 or 4608)) or (Buttons[0] == 1 and MousePos[0]>238 and MousePos[0]<257 and MousePos[1]>2 and MousePos[1]<23)) and EraserType == "Square": 
                    EraserType = "Circle"
                    ToolClicked = True
                    print "ERASER - Eraser shape set to Circle"
                elif ((event.type == KEYDOWN and event.key == K_2 and KeyMod == (4352 or 4608)) or (Buttons[0] == 1 and MousePos[0]>261 and MousePos[0]<282 and MousePos[1]>2 and MousePos[1]<23)) and EraserType == "Circle": 
                    EraserType = "Square"
                    ToolClicked = True
                    print "ERASER - Eraser shape set to Square"
            
            elif Mode == "Eyedropper":
                
                # Left click to change the pencil/fill/shape color to the color at the cursor's pixel
                if Buttons[0] == 1 and EyedropperStarted == False and MousePos[1] > 49: 
                    CanvasClicked = True
                    EyedropperStarted = True
                    if MouseY < 49: MouseY = 50
                    Color = Canvas.get_at((MouseX,MouseY))
                    print "EYEDROPPER - RGB color acquired: " + str(Color[0]) + "," + str(Color[1]) + "," + str(Color[2])
                elif Buttons[0] == 0:
                    EyedropperStarted = False
            
            elif Mode == "Marquee Eraser":
                    
                # The first click
                if Buttons[0] == 1 and SelectorStarted == False: 
                    CanvasClicked = True
                    SelectorX = MouseX
                    SelectorY = MouseY
                    SelectorStarted = True
                    ToolClicked == True
                    
                # Preview
                if Buttons[0] == 1 and SelectorStarted == True:
                    UpdatePreview()
                    pygame.draw.rect(Preview, (0,255,0), (SelectorX, SelectorY, MouseX-SelectorX, MouseY-SelectorY), 1)
                    
                # Release to complete the selection
                if Buttons[0] == 0 and SelectorStarted == True:
                    SelectorX2 = MouseX
                    SelectorY2 = MouseY
                    SelectorStarted = False
                    
                    # required to prevent issues when xy_start > xy_finish
                    if SelectorX2 < SelectorX and SelectorY2 < SelectorY:
                        Canvas.fill((255,255,255), (SelectorX2, SelectorY2, abs(SelectorX-SelectorX2), abs(SelectorY-SelectorY2)))
                    elif SelectorX2 < SelectorX and SelectorY2 > SelectorY:
                        Canvas.fill((255,255,255), (SelectorX2, SelectorY, abs(SelectorX-SelectorX2), abs(SelectorY2-SelectorY)))
                    elif SelectorX2 > SelectorX and SelectorY2 < SelectorY:
                        Canvas.fill((255,255,255), (SelectorX, SelectorY2, abs(SelectorX2-SelectorX), abs(SelectorY-SelectorY2)))
                    elif SelectorX2 > SelectorX and SelectorY2 > SelectorY:
                        Canvas.fill((255,255,255), (SelectorX, SelectorY, abs(SelectorX2-SelectorX), abs(SelectorY2-SelectorY)))
                        
                    UpdatePreview()
            
            elif Mode == "Palette":
                PaletteFormat = [" R", " G", " B"]
                
                # Temporary palette function that allows the user to type in an RGB value
                if event.type == KEYDOWN and len(Palette_Values) < 9 and event.key in PaletteDict:
                    AddToPalette(PaletteDict[event.key])
    
                    # Outputs the R, G or B value that was added
                    if len(Palette_Values) % 3 == 0: 
                        TempColor = int(Palette_Values[len(Palette_Values)-3:len(Palette_Values)]) # last 3 characters
                        if TempColor > 255: TempColor = 255 # same as the for loop below, but only affects CLI output
                        print "PALETTE - Added "+str(TempColor)+PaletteFormat[len(Palette_Values)/3-1]+" to the palette"
                    
                # Activates once there are 9 values, converts the 9 values in Palette_Values to an RGB color then resets it
                if len(Palette_Values) == 9:
                    PV = Palette_Values # just to save a bit of horizontal space
                    ColorTemp = ((int(PV[0]+PV[1]+PV[2]), int(PV[3]+PV[4]+PV[5]), int(PV[6]+PV[7]+PV[8])))
                    ColorTemp2 = [] # used to store ColorTemp values before they are checked for numbers above 255
                    for value in ColorTemp: # loop to set any RGB values above 255 to 255
                        if value > 255: ColorTemp2.append(255)
                        else: ColorTemp2.append(value)                    
                    Color = (ColorTemp2[0], ColorTemp2[1], ColorTemp2[2])
                    Toolbar.fill(Color, (192,6,14,14)) #Fills in the Palette button with the current color
                    print "PALETTE - Color set to " + str(Color)
                    Palette_Values = ""
            
            elif Mode == "Line":
                
                # Click to start the line, release to draw the line until the cursor point
                if Buttons[0] == 1: 
                    ToolClicked == True
                    if LineStarted == False:
                        LineStarted = True
                        LineXY_1 = (MouseX, MouseY)
                        
                    # Preview
                    UpdatePreview()
                    pygame.draw.line(Preview, Color, LineXY_1, (MouseX, MouseY), LineWidth)
                    
                elif Buttons[0] == 0 and LineStarted == True:
                    LineStarted = False
                    LineXY_2 = (MouseX, MouseY)
                    pygame.draw.line(Canvas, Color, LineXY_1, LineXY_2, LineWidth)
                        
                # 1~0 on the number line to set the line width
                if event.type == KEYDOWN and event.key in LineWidthDict:
                    ChangeLineWidth(LineWidthDict[event.key])
            
            elif Mode == "Shape_Circle":
                
                # Click to start the circle, release to draw the circle until the cursor point
                if Buttons[0] == 1: 
                    ToolClicked == True
                    if CircleStarted == False:
                        CircleStarted = True
                        CircleX_1 = MouseX
                        CircleY_1 = MouseY
                        
                    # Preview
                    UpdatePreview()
                    if (MouseX - CircleX_1) >= (MouseY - CircleY_1): Circle_Preview = MouseX - CircleX_1
                    elif (MouseX - CircleX_1) < (MouseY - CircleY_1): Circle_Preview = MouseY - CircleY_1
                    pygame.draw.circle(Preview, Color, (CircleX_1, CircleY_1), abs(Circle_Preview), CircleType)
                    
                elif Buttons[0] == 0 and CircleStarted == True:
                    CircleStarted = False
                    CircleX_2 = MouseX
                    CircleY_2 = MouseY
                    if (CircleX_2 - CircleX_1) >= (CircleY_2 - CircleY_1): Circle_Greater = CircleX_2 - CircleX_1
                    elif (CircleX_2 - CircleX_1) < (CircleY_2 - CircleY_1): Circle_Greater = CircleY_2 - CircleY_1
                    pygame.draw.circle(Canvas, Color, (CircleX_1, CircleY_1), abs(Circle_Greater), CircleType)
                    UpdatePreview()
                    
                # Alt+1 to set Filled circle, Alt+2 to set Outline circle
                #if event.type == KEYDOWN and event.key == K_1 and KeyMod == (4352 or 4608): 
                    #CircleType = 0 
                    #print "CIRCLE - Circle type set to Filled"
                #elif event.type == KEYDOWN and event.key == K_2 and KeyMod == (4352 or 4608): 
                    #CircleType = 1 
                    #print "CIRCLE - Circle type set to Outline"
            
            elif Mode == "Shape_Ellipse":
                
                # Click to start the ellipse, release to draw the ellipse until the cursor point
                if Buttons[0] == 1: 
                    ToolClicked == True
                    if EllipseStarted == False:
                        EllipseStarted = True
                        EllipseX_1 = MouseX
                        EllipseY_1 = MouseY
                        
                    # Preview
                    UpdatePreview()
                    EllipsePreview = Rect(EllipseX_1, EllipseY_1, MouseX-EllipseX_1, MouseY-EllipseY_1)
                    EllipsePreview.normalize()
                    pygame.draw.ellipse(Preview, Color, EllipsePreview, EllipseType)
                        
                elif Buttons[0] == 0 and EllipseStarted == True:
                    EllipseStarted = False
                    EllipseX_2 = MouseX
                    EllipseY_2 = MouseY
                    EllipseRect = Rect(EllipseX_1, EllipseY_1, EllipseX_2-EllipseX_1, EllipseY_2-EllipseY_1)
                    EllipseRect.normalize() # Used to prevent an error when the width or height are negative
                    pygame.draw.ellipse(Canvas, Color, EllipseRect, EllipseType)
                    
                # Alt+1 to set Filled ellipse, Alt+2 to set Outline ellipse
                #if event.type == KEYDOWN and event.key == K_1 and KeyMod == (4352 or 4608): 
                    #EllipseType = 0 
                    #print "ELLIPSE - Ellipse type set to Filled"
                #elif event.type == KEYDOWN and event.key == K_2 and KeyMod == (4352 or 4608): 
                    #EllipseType = 2 
                    #print "ELLIPSE - Ellipse type set to Outline"
            
            elif Mode == "Shape_Rectangle":
                
                # Click to start the rectangle, release to draw the rectangle until the cursor point
                if Buttons[0] == 1: 
                    ToolClicked == True
                    if RectStarted == False:
                        RectStarted = True
                        RectX_1 = MouseX
                        RectY_1 = MouseY
                        
                    # Preview
                    UpdatePreview()
                    pygame.draw.rect(Preview, Color, (RectX_1, RectY_1, MouseX-RectX_1, MouseY-RectY_1), RectType)
                    
                elif Buttons[0] == 0 and RectStarted == True:
                    RectStarted = False
                    RectX_2 = MouseX
                    RectY_2 = MouseY
                    pygame.draw.rect(Canvas, Color, (RectX_1, RectY_1, RectX_2-RectX_1, RectY_2-RectY_1), RectType)
                    
                # Alt+1 to set Filled rectangle, Alt+2 to set Outline rectangle
                if event.type == KEYDOWN and event.key == K_1 and KeyMod == (4352 or 4608): 
                    RectType = 0 
                    print "RECTANGLE - Rectangle type set to Filled"
                elif event.type == KEYDOWN and event.key == K_2 and KeyMod == (4352 or 4608): 
                    RectType = 1 
                    print "RECTANGLE - Rectangle type set to Outline"
                    
            elif Mode == "Shape_Square":
                
                # Click to start the square, release to draw the square until the cursor point
                if Buttons[0] == 1: 
                    ToolClicked == True
                    if SquareStarted == False:
                        SquareStarted = True
                        SquareX_1 = MouseX
                        SquareY_1 = MouseY
                        
                    SquareWH = abs(MouseX-SquareX_1)
                    # Preview
                    UpdatePreview()
                    
                    # Different calculations are needed to ensure the square draws from the starting point
                    if MouseY >= SquareY_1 and MouseX >= SquareX_1: # southeast
                        pygame.draw.rect(Preview, Color, (SquareX_1, SquareY_1, SquareWH, SquareWH), SquareType)
                    elif MouseY <= SquareY_1 and MouseX >= SquareX_1: # northeast
                        pygame.draw.rect(Preview, Color, (SquareX_1, SquareY_1-SquareWH, SquareWH, SquareWH), SquareType)
                    elif MouseY >= SquareY_1 and MouseX <= SquareX_1: # southwest
                        pygame.draw.rect(Preview, Color, (MouseX, SquareY_1, SquareWH, SquareWH), SquareType)
                    elif MouseY <= SquareY_1 and MouseX <= SquareX_1: # northwest
                        pygame.draw.rect(Preview, Color, (SquareX_1-SquareWH, SquareY_1-SquareWH, SquareWH, SquareWH), SquareType)
                        
                elif Buttons[0] == 0 and SquareStarted == True:
                    SquareStarted = False
                    SquareX_2 = MouseX
                    SquareY_2 = MouseY
                    SquareWidth = abs(SquareX_2 - SquareX_1)
                    
                    # Have to handle values 0,1 in arg 3 differently for when drawing towards different corners of the screen
                    if SquareY_2 >= SquareY_1 and SquareX_2 >= SquareX_1: # southeast
                        pygame.draw.rect(Canvas, Color, (SquareX_1, SquareY_1, SquareWidth, SquareWidth), SquareType)
                    elif SquareY_2 <= SquareY_1 and SquareX_2 >= SquareX_1: # northeast
                        pygame.draw.rect(Canvas, Color, (SquareX_1, SquareY_2, SquareWidth, SquareWidth), SquareType)
                    elif SquareY_2 >= SquareY_1 and SquareX_2 <= SquareX_1: # southwest
                        pygame.draw.rect(Canvas, Color, (SquareX_2, SquareY_1, SquareWidth, SquareWidth), SquareType)
                    elif SquareY_2 <= SquareY_1 and SquareX_2 <= SquareX_1: # northwest
                        pygame.draw.rect(Canvas, Color, (SquareX_2, SquareY_2, SquareWidth, SquareWidth), SquareType)
                    UpdatePreview()
                    
                # Alt+1 to set Filled square, Alt+2 to set Outline square
                if event.type == KEYDOWN and event.key == K_1 and KeyMod == (4352 or 4608): 
                    SquareType = 0
                    print "SQUARE - Square type set to Filled"
                elif event.type == KEYDOWN and event.key == K_2 and KeyMod == (4352 or 4608): 
                    SquareType = 1
                    print "SQUARE - Square type set to Outline"
            
            elif Mode == "Fill": 
                FillArray = pygame.PixelArray(Canvas)
                
                # Finds the color of the pixel at the cursor and replaces all similar pixels (tolerance% in multiples of 10)
                # Note - not contiguous, replaces ALL similar pixels
                if Buttons[0] == 1 and MousePos[1] > 49: 
                    ToolClicked == True
                    FillArray.replace(Canvas.get_at((MouseX,MouseY)), Color, FillTolerance)
                    
                # Changes the tolerance of the fill tool using keys 1~0 for 0.10~0.90 and 0, and key = for 1.00
                if event.type == KEYDOWN and event.key in FillTolDict:
                    ChangeFillTolerance(FillTolDict[event.key])
                    
                if (Buttons[0] == 1 and MousePos[0]>216 and MousePos[0]<236 and MousePos[1]>2 and MousePos[1]<23):
                    if FillTolerance >= 1: 
                        FillTolerance = 1
                        print "FILL - Cannot increase tolerance further!"
                    elif FillTolerance < 0.9: 
                        FillTolerance += 0.1
                        print "FILL - Tolerance increased by 0.1 to " + str(FillTolerance)
                elif (Buttons[0] == 1 and MousePos[0]>216 and MousePos[0]<236 and MousePos[1]>25 and MousePos[1]<46):
                    if FillTolerance <= 0.1: 
                        FillTolerance = 0.1
                        print "FILL - Cannot decrease tolerance further!"
                    elif FillTolerance > 0.2: 
                        FillTolerance -= 0.1
                        print "FILL - Tolerance decreased by 0.1 to " + str(FillTolerance)
    
    UpdateScreen()
    time.sleep(0.016) # To avoid being a complete resource hog
    
pygame.quit()
