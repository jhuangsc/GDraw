#Gary Zeng


#== Pygame imports
#import pygame, os
#os.environ['SDL_VIDEO_CENTERED'] = '1'

#from pygame.locals import *
#from pygame.color import THECOLORS

#import platform
#if platform.system() == "Windows":
    #os.environ['SDL_VIDEODRIVER'] = 'windib'

#pygame.init() 


#from pygame.time import delay as Sleep
#from pygame.event import get as GetEvents
#from pygame.mouse import get_pos as GetMousePos


#Height = 700
#Width = 1000

#window = pygame.display.set_mode((Width, Height)) 
#pygame.display.set_caption('Text Rendering Demonstration')

#from pygame.display import get_surface as GetScreenSurface
#screen = GetScreenSurface()
#ScreenFill = screen.fill
#=====================================

from pygame.display import flip as Display
from pygame.draw import rect as DrawRect

from pygame.font import SysFont

def WriteText(Text,Font,Color,Location,MaxPerLine,LineSpace=5,Justify=False,Indent=0):
    """\
    Text - Text to print
    Font - Pygame font object
    Color - Color tuple
    Location - (x,y)Top left corner of where text is to be printed
    MaxPerLine - Width in pixels of each line
    
    [Optional]
    LineSpace - Space between line breaks
    Justify - (True/False)
    Indent - Spaces to indent at beginning of each paragraph
    """
    
    Location = list(Location)#Make editable

    #Get lengths and heights of word
    SpaceWidth = Font.metrics(" ")[0][4]
    Height = Font.metrics("|")[0][3]

        
    
    #Split into paragraphs and words
    Line = []
    for Paragraph in Text.split("\n"):
        
        Line = []
        LineWidth = SpaceWidth*Indent
        LineToPrint = " "*Indent
        
        for Word in Paragraph.split(" "):
            Word += " "
            
            WordWidth = 0
            for Chr in Word:
                WordWidth += Font.metrics(Chr)[0][4]
            
            NewLineWidth = LineWidth + WordWidth
            
            #If fits onto line, add to line
            if NewLineWidth<=MaxPerLine:
                LineWidth = NewLineWidth
                Line.append(Word)
            
            #Otherwise, write the current line, set new line as word
            else:
                
                #Create string to be printed
                if Justify:
                    # = (ToAddAfterEachWord,Leftovers)
                    SpacesToAdd_ToEachLine,SpacesToAdd_LeftOvers = divmod((MaxPerLine-LineWidth)/SpaceWidth,len(Line)-1)
                    for i in xrange(len(Line)-1):
                        Line[i] += " "*SpacesToAdd_ToEachLine
                        if i<SpacesToAdd_LeftOvers:
                            Line[i] += " "
                
                #Convert Line to string and print
                for word in Line:
                    LineToPrint += word
                
                screen.blit(Font.render(LineToPrint,1,Color), Location)
                
                LineToPrint = ""
                
                Line = [Word]
                LineWidth = WordWidth
                Location[1] += Height + LineSpace#Move target down for new line
        
        if Line!=[]:
            for word in Line:
                LineToPrint += word
            screen.blit(Font.render(LineToPrint,1,Color), Location)
            
        Location[1] += Height + LineSpace
        

#LoremIpsum = \
#orem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

#Font1 = SysFont("timesnewroman", 18)
#WriteText(LoremIpsum,Font1,THECOLORS["red"],(50,50),340,5)

#Font2 = SysFont("impact", 25)
#WriteText(LoremIpsum,Font2,THECOLORS["blue"],(50,300),500,5,True,5)

#Font3 = SysFont("arial", 20)
#WriteText(LoremIpsum,Font3,THECOLORS["yellow"],(700,50),200,5,True)


#Display()


#Running = True
#while Running:
    #Events = GetEvents()
    
    #for Event in Events: 
        #if Event.type == QUIT:
            #quit("Quit")
            #Running = False
    #Sleep(500)
