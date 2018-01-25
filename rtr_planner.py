import random
import math
import numpy as np
import cv2
import utility as util
import copy 
random.seed(1)
class Robot:

	def __init__(self,p1,width,height):
		self.pos = [0,0]
		self.width = width
		self.height = height
		#self.theta = 0
		self.centr_p1 = p1
		

	def get4pointsofrobot(self,q):
		
		r1 = math.sqrt(math.pow(self.width/4,2)+math.pow(self.height/2,2))
		r2 = math.sqrt(math.pow(self.width/4,2)+math.pow(self.height/2,2))
		r3 = math.sqrt(math.pow(self.width/4*3,2)+math.pow(self.height/2,2))
		r4 = math.sqrt(math.pow(self.width/4*3,2)+math.pow(self.height/2,2))


		angle1 = math.pi-math.acos(self.width/4/r1)
		angle2 = -angle1
		angle3 = math.acos(self.width*3/4/r3)
		angle4 = -angle3

		point1 = [q.x + r1*math.cos(angle1-q.theta),
					q.y + r1*math.sin(angle1-q.theta)]
		point2 = [q.x + r2*math.cos(angle2-q.theta),
					q.y + r2*math.sin(angle2-q.theta)]
		point4 = [q.x + r3*math.cos(angle3-q.theta),
					q.y + r3*math.sin(angle3-q.theta)]
		point3 = [q.x + r4*math.cos(angle4-q.theta),
					q.y + r4*math.sin(angle4-q.theta)]

		return [point1,point2,point3,point4]

	def ifCrash(self,q,obstacles,img,primitive,direction):
		points_of_robot = self.get4pointsofrobot(q)
		Crash = False
		turn_radius = math.sqrt(2)*self.height/2
		#turn_radius = 5
		if(primitive == "translate" and direction=="forward"):
			#print(points_of_robot[3])
			points_of_robot[3] =[points_of_robot[3][0]+turn_radius*math.cos(q.theta),points_of_robot[3][1]+turn_radius*math.sin(q.theta)] 
			points_of_robot[2] =[points_of_robot[2][0]+turn_radius*math.cos(q.theta),points_of_robot[2][1]+turn_radius*math.sin(q.theta)]  
		if(primitive == "translate" and direction=="backward"):
			points_of_robot[0] =[points_of_robot[0][0]-turn_radius*math.cos(q.theta),points_of_robot[0][1]-turn_radius*math.sin(q.theta)] 
			points_of_robot[1] =[points_of_robot[1][0]-turn_radius*math.cos(q.theta),points_of_robot[1][1]-turn_radius*math.sin(q.theta)] 


		Crash = util.CrossesObstacles(points_of_robot[0],points_of_robot[-1],obstacles)
		if(Crash):
			return True
		for i in range(len(points_of_robot)-1):
			Crash = util.CrossesObstacles(points_of_robot[i],points_of_robot[i+1],obstacles)
			if(Crash):
				return True
		
		#print("RAnge: "+str(util.inRangeOfImg(points_of_robot,img)))
		if(not util.inRangeOfImg(points_of_robot,img)):
			return True
		return Crash

class Tree:

	class q:

		def __init__(self,position,theta):
			self.x = position[0]
			self.y = position[1]
			self.theta = theta

		def Translate(self,direction,cost):
			#print("lol")
			#print(self.x)
			#print(self.y)
			if(direction == "forward"):
				self.x += cost*math.cos(self.theta) 
				self.y += cost*math.sin(self.theta)
			elif(direction == "backward"):
				self.x -= cost*math.cos(self.theta) 
				self.y -= cost*math.sin(self.theta)
			else:
				print("Specify directionection by 'forward' or 'backward'")

		def Rotate(self,angle):
			self.theta += angle

		def __str__(self):
			return ("|" +str(self.x) + " " + str(self.y) + " " + str(self.theta) + "|" ) 

	class TCI:
		
		def __init__(self,q_begin,q_end):
			self.q_begin = q_begin
			self.q_end = q_end

	class RCI:

		def __init__(self,q_begin,q_end):
			self.q_begin = q_begin
			self.q_end = q_end

	def __init__(self,Robot,img):
		self.edges = []
		self.vertexes = []
		self.robot = Robot
		self.img = img

	def AddVertex(self,q_new):
		#print(q_new)
		self.vertexes.append(copy.deepcopy(q_new))

	def AddEdge(self,qnear,qnew):
		self.edges.append([copy.deepcopy(qnear),copy.deepcopy(qnew)])

	def Init(self,q,obstacles):
		self.AddVertex(q)
		print(q)
		TCI = self.TCIExtend(q,"forward",obstacles)
		self.AddVertex(TCI.q_end)
		self.AddEdge(q,TCI)
		TCI = self.TCIExtend(q,"backward",obstacles)
		self.AddVertex(TCI.q_end)
		self.AddEdge(q,TCI)

	def Extend(self,q,turndirection,obstacles):
		RCI,collision = self.RCIExtend(q,turndirection,obstacles)
		self.AddVertex(RCI.q_end)
		self.AddEdge(q,RCI)
		TCI = self.TCIExtend(RCI.q_end,"forward",obstacles)
		self.AddVertex(TCI.q_end)
		self.AddEdge(RCI.q_end,TCI)
		TCI = self.TCIExtend(RCI.q_end,"backward",obstacles)
		self.AddVertex(TCI.q_end)
		self.AddEdge(RCI.q_end,TCI)

		return collision

	def TCIExtend(self,q,direction,obstacles):
		q_begin = copy.deepcopy(q)
		q_end = copy.deepcopy(q)
		while not self.robot.ifCrash(q_end,obstacles,self.img,"translate",direction):
			q_end.Translate(direction,1)
		return self.TCI(q_begin,q_end)

	def RCIExtend(self,q,angle,obstacles):
		collision = False
		q_end = copy.deepcopy(q)
		q_begin = copy.deepcopy(q)
		rez_angle = 0
		while abs(rez_angle) < abs(angle) and not collision:
			rez_angle += math.copysign(1,angle)*0.1
			q_end.Rotate(math.copysign(1,angle)*0.1)
			collision = self.robot.ifCrash(q_end,obstacles,self.img,"rotate","backward")


		if(collision):
			q_end.theta -= math.copysign(1,angle)*0.1

		return (self.RCI(q_begin,q_end),collision)

	def NearestNeighbor(self,new_vertex):

		min_dist = None
		min_q = None
		orient = None
		
		for edge in self.edges:
			if(edge[0].x == edge[1].q_end.x and edge[0].y == edge[1].q_end.y):
				candidate_q = [edge[1].q_end.x,edge[1].q_end.y]

			else:
				candidate_q = util.ClosestPoint(edge[0],edge[1].q_end,self.q(new_vertex,0))
			candidate_dist = math.hypot(new_vertex[0] - candidate_q[0],new_vertex[1]-candidate_q[1])
			if min_dist == None or candidate_dist < min_dist:
				min_dist = candidate_dist
				min_q = candidate_q 
				orient = edge[0].theta 
				
		return self.q(min_q,orient)

	def draw_all(self,obstacles,robot,color):

		def draw_robot(img,q,robot,color):
			p_for_line = robot.get4pointsofrobot(q)
			for i in range(len(p_for_line)-1):
				cv2.line(img,(int(p_for_line[i][0]),int(p_for_line[i][1])),(int(p_for_line[i+1][0]),int(p_for_line[i+1][1])),color)				
			cv2.line(img,(int(p_for_line[0][0]),int(p_for_line[0][1])),(int(p_for_line[-1][0]),int(p_for_line[-1][1])),color)
			return img
		
		img = self.img
		n = 0
		for vertex in self.vertexes:

			cv2.circle(img,(math.ceil(vertex.x),math.ceil(vertex.y)),2,(0,0,255))
			if(n%50==0 or True):
				draw_robot(img,vertex,robot,color)
		for edge in self.edges:
			cv2.line(img,(math.ceil(edge[0].x),math.ceil(edge[0].y)),(math.ceil(edge[1].q_end.x),math.ceil(edge[1].q_end.y)),(255,0,0))
		for obstacle in obstacles:
			for i in range(len(obstacle)-1):
				cv2.line(img,(obstacle[i][0],obstacle[i][1]),(obstacle[i+1][0],obstacle[i+1][1]),(0,255,0))
		return img

class RTR_PLANNER:

	def __init__(self,Robot,img):
		self.win_name = "Win1"
		self.Tree = Tree(Robot,img)
		self.dims = [img.shape[:2][1],img.shape[:2][0]]

	def construct(self,q_init,q_end,obstacles,max_expand_dist = 50,n_of_iterations = 50):
		self.Tree.Init(q_init,obstacles)		
		for k in range(n_of_iterations):
			P_g = self.RandomPos(self.dims)
			q_near = self.Tree.NearestNeighbor(P_g)
			turndirection = self.MinTurndirection(q_near,P_g)
			collision = self.Tree.Extend(q_near,turndirection,obstacles)
			if collision:
				self.Tree.Extend(q_near, -math.copysign(1,turndirection)* (2*math.pi - abs(turndirection)),obstacles)

		return self.Tree


	def MinTurndirection(self,q_nearest,random_point):
		x = random_point[0] - q_nearest.x
		y = random_point[1] - q_nearest.y

		dx = math.cos(q_nearest.theta)
		dy = math.sin(q_nearest.theta)
		angle = math.atan2(x*dy - y*dx,x*dx+y*dy)

		return angle

	def RandomPos(self,dims):
		return [random.randint(0,dims[0]),random.randint(0,dims[1])]



def main():
	img = cv2.imread("floor_without_p.png",1)
	#print(img.shape[:2][1])
	q_root = Tree.q([150,50],0)
	q_end = Tree.q([500,400],0)
	robot = Robot([q_root.x,q_root.y],75,40)
	rt_tree = RTR_PLANNER(robot,img)
	#wall3 = util.build_wall((0,0),(img.shape[:2][1],0),200)
	#wall4 = util.build_wall((img.shape[:2][1]-2,0),(img.shape[:2][1]-2,img.shape[:2][0]),200)
	#wall1 = util.build_wall((img.shape[:2][1],img.shape[:2][0]-2),(0,img.shape[:2][0]-2),200)
	#wall2 = util.build_wall((0,img.shape[:2][0]),(0,0),200)
	wall6 = util.build_wall([0,100],[img.shape[:2][1]-300,100],200)
	wall5 = util.build_wall([img.shape[:2][1],200],[300,200],200)
	wall7 = util.build_wall([0,300],[img.shape[:2][1]-300,300],200)
	#obstacles = [wall1,wall2,wall3,wall4,wall5,wall6,wall7]
	obstacles = [wall6,wall5,wall7]
	tree1 = rt_tree.construct(q_root,q_end,obstacles,50,100)
	rt_tree2 = RTR_PLANNER(robot,img)
	tree2 = rt_tree2.construct(q_end,q_root,obstacles,50,100)

	img1 = tree1.draw_all(obstacles,robot,(0,255,0))
	img1 = tree2.draw_all(obstacles,robot,(0,0,255))

	win_name = "Win1"
	cv2.namedWindow(win_name)
	cv2.imshow(win_name,img1)
	cv2.waitKey(0)

if __name__ == '__main__':
	main()

