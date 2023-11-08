from Board import Board
import pygame
import pygame.freetype
from sys import exit
from ChessFunctionsAndConstants import *
import random
from Move import Move


class DisplayModule:

    def __init__(self,board:Board):
        self.board=board
        self.bb=pygame.transform.scale(pygame.image.load('images/bb.png'),(50,50))
        self.bh=pygame.transform.scale(pygame.image.load('images/bh.png'),(50,50))
        self.bk=pygame.transform.scale(pygame.image.load('images/bk.png'),(50,50))
        self.bp=pygame.transform.scale(pygame.image.load('images/bp.png'),(50,50))
        self.bq=pygame.transform.scale(pygame.image.load('images/bq.png'),(50,50))
        self.br=pygame.transform.scale(pygame.image.load('images/br.png'),(50,50))
        self.wb=pygame.transform.scale(pygame.image.load('images/wb.png'),(50,50))
        self.wh=pygame.transform.scale(pygame.image.load('images/wh.png'),(50,50))
        self.wk=pygame.transform.scale(pygame.image.load('images/wk.png'),(50,50))
        self.wp=pygame.transform.scale(pygame.image.load('images/wp.png'),(50,50))
        self.wq=pygame.transform.scale(pygame.image.load('images/wq.png'),(50,50))
        self.wr=pygame.transform.scale(pygame.image.load('images/wr.png'),(50,50))
        self.ptoi={'r':self.br,'n':self.bh,'b':self.bb,'q':self.bq,'k':self.bk,'p':self.bp,'R':self.wr,'N':self.wh,'B':self.wb,'Q':self.wq,'K':self.wk,'P':self.wp}
        pygame.init()
        size_x=600
        size_y=600
        screen=pygame.display.set_mode((size_x,size_y))
        self.screen=screen
        pygame.display.set_caption('CHESS')
        clock=pygame.time.Clock()
        surface=pygame.Surface((size_x,size_y))
        surface.fill('black')
        text_mod=pygame.font.Font(None,40)
        movstate=1
        valid=[]
        status=0
        while True:
            
            for x in range(64):
                if ((x%8)+(x//8))%2==0:
                    pygame.draw.rect(surface,'burlywood2',pygame.Rect(100+50*(x%8),100+50*(x//8),50,50))
                else:
                    pygame.draw.rect(surface,'burlywood4',pygame.Rect(100+50*(x%8),100+50*(x//8),50,50))
            for move in valid:
                p=self.cord_to_pos(move)
                #pygame.draw.rect(surface,'red',pygame.Rect(p[0],p[1],50,50))
                pygame.draw.circle(surface,'red',(p[0]+25,p[1]+25),10)
            events=pygame.event.get()
            m=self.board.legalMoves()
            screen.blit(surface,(0,0))
            if len(m)==0:
                text=text_mod.render(f"""BLACK WINS!!!""",0,(255,255,255))
                pos=(70,550)
                screen.blit(text,pos)
                valid=[]
                status=1
            for event in events:
                if event.type==pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if status==1:
                        continue
                    else:
                        pos=pygame.mouse.get_pos()
                        if pos[0]>500 or pos[1]>500:
                            continue
                        pos=self.pos_to_cord(pos)

                        if movstate==1:
                            for mov in m:
                                if mov.start==pos:
                                    valid.append(mov)
                            if valid!=[]:
                                movstate=2
                        elif movstate==2:
                            newvalid=[]
                            for mov in valid:
                                if mov.end==pos:
                                    newvalid.append(mov)
                            valid=newvalid
                            if valid==[]:
                                movstate=1
                            if valid!=[]:
                                self.board.make_move(valid[0])
                                valid=[]
                                movstate=1
                                self.board.search(3,True)
                                if self.board.bestMove==None:
                                    text=text_mod.render(f"""WHITE WINS!!!""",0,(255,255,255))
                                    pos=(70,550)
                                    screen.blit(text,pos)
                                    valid=[]
                                    status=1
                                else:
                                    self.board.make_move(self.board.bestMove)
            
            
            text=text_mod.render(f"""{"WHITE" if self.board.currentTurn==WHITE else "BLACK"} TO MOVE""",0,(255,255,255))
            
            pos=(100,70)
            screen.blit(text,pos)
            for n in range(8,0,-1):
                text=text_mod.render(f"{n}",0,(255,255,255))
                pos=(80,110+((8-n)*50))
                screen.blit(text,pos)
            text=text_mod.render("a    b    c    d     e    f     g    h",0,(255,255,255))
            pos=(120,510)
            screen.blit(text,pos)
            self.draw_peices()
            
            pygame.display.update()
            clock.tick(60)

    def draw_peices(self):
        board=self.board.board
        for x in range(64):
                piece=pieceToCharacter(self.board.board[x])
                if piece!=" ":
                    self.screen.blit(self.ptoi[piece],(100+50*(x%8),100+50*(x//8)))

    def pos_to_cord(self,pos):
        pos=list(pos)
        pos[0]-=100
        pos[1]-=100
        a=(pos[0]//50)
        b=(pos[1]//50)*8
        return a+b
    
    def cord_to_pos(self,Move:Move):
        start=Move.start
        stop=Move.end
        return (100+(stop%8)*50,100+(stop//8)*50)
        

                



c = Board()
print(c.printBoard())
print(c.board)
dm=DisplayModule(c)
