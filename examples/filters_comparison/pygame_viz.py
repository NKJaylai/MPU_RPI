import pygame
from math import *
import zmq
import numpy as np
import json


WINDOW_SIZE =  800
scale = 100
window = pygame.display.set_mode( (WINDOW_SIZE, WINDOW_SIZE) )
clock = pygame.time.Clock()
cube_points = [n for n in range(8)]
cube_points[0] = np.array([[-1], [-1], [1]])
cube_points[1] = np.array([[1],[-1],[1]])
cube_points[2] = np.array([[1],[1],[1]])
cube_points[3] = np.array([[-1],[1],[1]])
cube_points[4] = np.array([[-1],[-1],[-1]])
cube_points[5] = np.array([[1],[-1],[-1]])
cube_points[6] = np.array([[1],[1],[-1]])
cube_points[7] = np.array([[-1],[1],[-1]])

projection_matrix = [[1,0,0],
                     [0,1,0],
                     [0,0,0]]

def connect_points(i, j, points):
    pygame.draw.line(window, (255, 255, 255), (points[i][0], points[i][1]) , (points[j][0], points[j][1]))
    
def main():
    host = '10.2.171.72'
    port = 8358
    url = 'tcp://'+host+':'+str(port)
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(url)
    socket.setsockopt(zmq.SUBSCRIBE, b'')
    
    roll = 0
    pitch = 0
    yaw = 0
    window.fill((0,0,0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        window.fill((0,0,0))
        point = cube_points
        packet = socket.recv_json(flags=0)
        kal = None
        kal = np.array(json.loads(packet['kalman']))
        if kal.any() != None:
            roll = radians(kal[0])
            yaw = radians(kal[1])
            pitch = radians(kal[2])
            rotation_x = np.array([[1, 0, 0],
                          [0, cos(roll), -sin(roll)],
                          [0, sin(roll), cos(roll)]])
        
            rotation_y = np.array([[cos(pitch), 0, sin(pitch)],
                          [0, 1, 0],
                          [-sin(pitch), 0, cos(pitch)]])
        
            rotation_z = np.array([[cos(yaw), -sin(yaw), 0],
                          [sin(yaw), cos(yaw), 0],
                          [0, 0, 1]])
    
            points = [0 for _ in range(len(cube_points))]
            i = 0
            for point in cube_points:
                rotate_x = np.matmul(rotation_x, point)
                rotate_y = np.matmul(rotation_y, rotate_x)
                rotate_z = np.matmul(rotation_z, rotate_y)
                point_2d = np.matmul(projection_matrix, rotate_z)
            
                x = (point_2d[0][0] * scale) + WINDOW_SIZE/2
                y = (point_2d[1][0] * scale) + WINDOW_SIZE/2
        
                points[i] = (x,y)
                
                i += 1
                pygame.draw.circle(window, (255, 0, 0), (x, y), 5)
            connect_points(0, 1, points)
            connect_points(0, 3, points)
            connect_points(0, 4, points)
            connect_points(1, 2, points)
            connect_points(1, 5, points)
            connect_points(2, 6, points)
            connect_points(2, 3, points)
            connect_points(3, 7, points)
            connect_points(4, 5, points)
            connect_points(4, 7, points)
            connect_points(6, 5, points)
            connect_points(6, 7, points)
        pygame.display.update()
main()