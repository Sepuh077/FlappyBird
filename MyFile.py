import pygame
import numpy

pygame.init()
win=pygame.display.set_mode((500,500))
pygame.display.set_caption("Flappy Bird")

Up=pygame.image.load('images/RJ_1.png')
Down=pygame.image.load('images/RJ_2.png')
bg=pygame.image.load('images/pygame_bg.jpg')

score=0
max_score=0
x=225
y=225
width=50
height=37
ms=7
alldist=0
isjump=False
jump=80
h=list()
start=False
passg=list()
xPos=list()
for i in range(3):
    h.append(-1)
    xPos.append(-100)
    passg.append(True)
jumpcount=int(6)
ylimit=500-height-ms
i=1
dist=0


run=True
while run:
    pygame.time.delay(33)

    win.blit(bg, (0, 0))
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
    keys=pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and isjump==False:
        isjump=True
        jumpcount=6
        start=True
    else:
        isjump=False
    if start:
        if isjump or jumpcount!=6:
            if jumpcount>=1:
                if y-(jumpcount**2)/2<=0:
                    y=0
                else:
                    y -= (jumpcount ** 2) / 2
                jumpcount-=1
            else:
                isjump=False
                animcount = 0
                jumpcount=6
                i=1
        else:
            i+=1
            if y+(i**2)/2<=ylimit:
                y+=(i**2)/2
            else:
                y=ylimit

        if dist<=0:
            h[2]=h[1]
            xPos[2]=xPos[1]
            passg[2]=passg[1]
            h[1]=h[0]
            xPos[1]=xPos[0]
            passg[2] = passg[1]
            h[0]=numpy.random.randint(10,350)
            xPos[0]=510
            passg[0]=False
            dist=500
        else:
            dist-=ms
        for j in range(3):
            pygame.draw.rect(win,(0,255,0), (xPos[j],500-h[j],80,h[j]))
            pygame.draw.rect(win,(0,255,0)  ,(xPos[j],0,80,500-h[j]-140))
            xPos[j]-=ms
        alldist+=ms
        ms=7+(alldist//3000)

        for j in range(3):
            if x+width>=xPos[j] and x<=xPos[j]+80 and (y+height>=500-h[j] or y<=360-h[j]):
                    pygame.time.delay(500)
                    win.blit(bg, (0, 0))
                    alldist=0
                    ms=7
                    score=0
                    start=False
                    y=225
                    for var in range(3):
                        xPos[var]=-100
                        passg[var]=True
                        h[var]=-1
                    break
        for j in range(3):
            if xPos[j]+80<225 and passg[j]==False:
                score+=1
                passg[j]=True

        if score>max_score:
            max_score=score
        font = pygame.font.Font('freesansbold.ttf', 15)
        text = font.render("Score: "+str(score), True, (255,255,255))
        text1=font.render("Record: "+str(max_score),True,(255,255,255))
        textRect = text.get_rect()
        text1Rect=text1.get_rect()
        textRect.center = (30, 10)
        text1Rect.center=(36, 30)
        win.blit(text, textRect)
        win.blit(text1, text1Rect)

    if isjump:
        win.blit(Up,(x,y))
    else:
        win.blit(Down,(x,y))

    if not(start):
        font = pygame.font.Font('freesansbold.ttf', 40)
        Play=font.render("Press 'Space' to play",True,(255,255,255))
        playrect=Play.get_rect(center=(250,250))
        win.blit(Play,playrect)
    pygame.display.update()

pygame.quit()