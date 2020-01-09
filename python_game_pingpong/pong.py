# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 22:35:22 2019
@author: mdeepan
About the game: Computer is playing in the left side automatically and user in the right side
"""

import pygame
import sys
import random
from pygame.locals import *

pygame.init()
fps = pygame.time.Clock()

game_over = False
width = 600
height = 400
ball_x = int(width/2)
ball_y = int(height/2)
player_width = 90
player_height = 12
computer_width = 90
computer_height = 12
ball_radius = 22
ball_pos = [ball_x, ball_y]
player_pos = [width - 2* player_height, height/2 - player_width/2]
computer_pos = [computer_height, height/2 - computer_width/2]
screen = pygame.display.set_mode((width, height))
movex = random.randint(1,3)
movey = random.randint(1,4)
player_score = 0
comp_score = 0
checkvar = 0
check_state = True
x_snap_start = 0
y_snap_start = 0
predicted_ball_pos = 0
speed = 60
snap_pos = [0,0]

#def quit
def quit_game():
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
        
        
#move pong ball
def move_pongball(ball_x, ball_y, movex, movey):
    #print("moving ball")
    ball_x += movex
    ball_y -= movey
    ball_pos = [ball_x, ball_y]
    return ball_pos

#finding collision with boundaries
def find_collisionwithwalls(ball_pos, movex, movey):
    if (ball_pos[1] <= 10 or ball_pos[1] >= 400):
        return True

#finding collision with pads
def find_collisionwithpads(player_pos, ball_pos, movex, movey):
    if (ball_pos[0] >= width - 3*player_height and 
        ball_pos[0] <= width - 2*player_height and ball_pos[1] >= player_pos[1] and 
        ball_pos[1] <= player_pos[1] + player_width + ball_radius/2):
        return True

#recentering the ball after a miss
def recentering_ball(ball_pos, comp_score, player_score):
    if (ball_pos[0] >= 610) or (ball_pos[0] <= -10):
        pygame.time.delay(100)
        #display_score(ball_pos, comp_score, player_score)
        return True    
        
#move computer's pad to hit the ball
check_initial_state = True
check_final_state = True
def check_first_co(computer_pos, ball_pos, y_snap_start, x_snap_start, snap_pos):
    global check_initial_state
    print(str(ball_pos)+", "+str(computer_pos))
    if ball_pos[0] <= 300 and check_initial_state:
        x_snap_start = ball_pos[0]
        y_snap_start = ball_pos[1]
        snap_pos = [int(x_snap_start), int(y_snap_start)]
        print(y_snap_start)
        check_initial_state = False
    return snap_pos

def check_last_co(computer_pos, ball_pos, snap_pos, predicted_ball_pos):
    global check_final_state
    if ball_pos[0] <= snap_pos[0] - 1 and check_final_state and snap_pos[1] != 0:
        x_snap_end = int(ball_pos[0])
        y_snap_end = int(ball_pos[1])
        print(y_snap_end)
        one_framesnap = (y_snap_end - snap_pos[1]) / (snap_pos[0] - x_snap_end)
        print (one_framesnap)
        if one_framesnap >= 0:
            print("inside if to predict")
            predicted_ball_pos = ((one_framesnap * 265) + ball_pos[1] - 800) * -1
            if predicted_ball_pos < 0:
                predicted_ball_pos = ((one_framesnap * 265) + ball_pos[1] - 800)
            if predicted_ball_pos > 400:
                predicted_ball_pos = ((one_framesnap * 265) + ball_pos[1])
            print(predicted_ball_pos)
            check_final_state = False
        elif one_framesnap <= 0:
            print("inside elif to predict")
            predicted_ball_pos = ((one_framesnap * 265) + ball_pos[1]) * -1
            if predicted_ball_pos < 0:
                predicted_ball_pos = (one_framesnap * 265) + ball_pos[1]
            print(predicted_ball_pos)
        check_final_state = False
    return predicted_ball_pos

def move_comp_pad(predicted_ball_pos, computer_pos,movex, movey):
    if predicted_ball_pos != 0:
        #print("moving computer pad")
        #print(computer_pos[0])
        computer_pos[1] = predicted_ball_pos - (computer_width/2)
        if (ball_pos[0] <= 3 * player_height and 
        ball_pos[0] >= 2*player_height and ball_pos[1] >= computer_pos[1] and 
        ball_pos[1] <= computer_pos[1] + player_width + ball_radius/2):
            print("Found Collision")
            '''movex = movex
            movey = -movey
            print(str(movex)+", "+str(movey))
            move_pongball(ball_pos[0], ball_pos[1], movex, movey)'''
            return True



while not game_over:
    
    for event in pygame.event.get():   
        quit_game()        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                movex = movex * 2
                movey = movey * 2
            if event.key == pygame.K_DOWN:
                if player_pos[0] <= width and player_pos[1] <= width:
                    player_pos[1] += 40
            elif event.key == pygame.K_UP:
                if player_pos[0] <= width and player_pos[1] <= width:
                    player_pos[1] -= 40  
                    
    screen.fill((0,0,0)) 
    
    if find_collisionwithwalls(ball_pos, movex, movey):
        movey = -movey
        move_pongball(ball_pos[0], ball_pos[1], movex, movey)
        
    if find_collisionwithpads(player_pos, ball_pos, movex, movey):
        movex = -movex - 1
        movey = movey + 1
        y_snap_start = 0
        predicted_ball_pos = 0
        check_initial_state = True
        check_final_state = True
        move_pongball(ball_pos[0], ball_pos[1], movex, movey)
        
    if recentering_ball(ball_pos, comp_score, player_score):
        print("recentering now.....")
        if (ball_pos[0] >= 610):
            comp_score += 1
        elif (ball_pos[0] <= -10):
            player_score += 1
        if player_score + comp_score % 5:
            speed += 3
        #print(str(comp_score)+", "+str(player_score))
        ball_pos[0] = width//2
        ball_pos[1] = height//2
        if random.random() < 0.2:
            movex = -random.randint(2,4)
            movey = random.randint(2,3)
        elif random.random() >= 0.2 and random.random() <= 0.5:
            movex = -random.randint(2,4)
            movey = -random.randint(2,3)
        elif random.random() >= 0.6 and random.random() <= 0.8:
            movex = random.randint(2,4)
            movey = random.randint(2,3)
        else:
            movex = random.randint(3,4)
            movey = -random.randint(2,3)
        print(str(movex)+", "+str(movey))
        move_pongball(ball_pos[0], ball_pos[1], movex, movey)
        y_snap_start = 0
        predicted_ball_pos = 0
        check_initial_state = True
        check_final_state = True

    ball_pos = move_pongball(ball_pos[0], ball_pos[1], movex, movey)
    
    snap_pos = check_first_co(computer_pos, ball_pos, y_snap_start, x_snap_start, snap_pos)
    
    predicted_ball_pos = check_last_co(computer_pos, ball_pos, snap_pos, predicted_ball_pos)
    
    if move_comp_pad(predicted_ball_pos, computer_pos, movex, movey):
        movex = -movex
        movey = movey
        move_pongball(ball_pos[0], ball_pos[1], movex, movey)
    
    myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
    label1 = myfont1.render("Score "+str(comp_score), 1, (255,0,0))
    screen.blit(label1, (50,20))
    myfont2 = pygame.font.SysFont("Comic Sans MS", 20)
    label2 = myfont2.render("Score "+str(player_score), 1, (255,0,0))
    screen.blit(label2, (470, 20))
    
    pygame.draw.line(screen, (255,255,255), [width // 2, 0],[width // 2, height], 1)
    pygame.draw.rect(screen, (0,255,0), (player_pos[0],player_pos[1],player_height,player_width))
    pygame.draw.rect(screen, (0,255,0), (computer_pos[0],computer_pos[1],computer_height,computer_width))
    pygame.draw.circle(screen, (255,255,255), (ball_pos[0],ball_pos[1]), ball_radius, 20)
    pygame.draw.circle(screen, (255,255,255), [width//2, height//2], 70, 1)
    pygame.draw.line(screen, (255,255,255), [width - 2* player_height, 0],[width - 2*player_height, height], 1)
    pygame.draw.line(screen, (255,255,255), [2* player_height, 0],[2*player_height, height], 1)
    pygame.draw.line(screen, (255,255,255), [width // 2, 0],[width // 2, height], 1)
    pygame.display.set_caption('Py-Pong')
    
    fps.tick(speed)
    pygame.display.update()
 
