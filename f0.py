# init
size = get_world_size()

source = {
	Items.Hay:		Entities.Grass,
	Items.Wood:		Entities.Tree,
	Items.Carrot:	Entities.Carrot,
	Items.Pumpkin:	Entities.Pumpkin,
	Items.Cactus:	Entities.Cactus,
	Items.Power:	Entities.Sunflower,
	Items.Bone:		Entities.Apple
}
# ---------------------------------------------------------
# 收获
def harv():
	if can_harvest():
		return harvest()
	return False

# 浇水，阈值手动配
def water():
	if get_water() < 0.5:
		return use_item(Items.Water)
	return False

# 移动到指定位置
def moveTo(p):
	x, y = get_pos_x(), get_pos_y()
	x1, y1 = p
	# East x+1, West x-1, North y+1, South y-1
	dx = (x1 - x) % size
	dy = (y1 - y) % size
	
	if dx > size - dx:
		hor_dir = West
		hor_step = size - dx
	else:
		hor_dir = East
		hor_step = dx
	
	if dy > size - dy:
		ver_dir = South
		ver_step = size - dy
	else:
		ver_dir = North
		ver_step = dy
	
	for i in range(hor_step):
		move(hor_dir)
	for i in range(ver_step):
		move(ver_dir)

# 计算距离	
def getDistance(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	dx = min(abs(x2 - x1), size - abs(x2 - x1))
	dy = min(abs(y2 - y1), size - abs(y2 - y1))
	return dx + dy

# 路径遍历导航
def sortPosByDistance(posList):
	sorted = []
	unvisited = []
	for p in posList:
		unvisited.append(p)
	current = posList[0]

	while unvisited:
		min_dist = 99999
		nearest = None
		for p in unvisited:
			dist = getDistance(current, p)
			if dist < min_dist:
				min_dist = dist
				nearest = p
		if nearest == None:
			break
		sorted.append(nearest)
		unvisited.remove(nearest)
		current = nearest
	
	return sorted
# ---------------------------------------------------------
def targetUpdate(target = Items.Hay):
	if target == Items.Hay or target == Items.Wood:
		return target
	else:
		cost = get_cost(source[target])
		
		# 南瓜特判
		if target == Items.Pumpkin:
			cost[Items.Carrot] = cost[Items.Carrot] * 2
		
		for i in cost:
			if num_items(i) < cost[i] * size * size:
				return targetUpdate(i)
			else:
				return target
# ---------------------------------------------------------
def plantFarm(target):
	if target == Items.Hay:
		plantGrass()
	elif target == Items.Wood:
		plantTree()
	elif target == Items.Carrot:
		plantCarrot()
	elif target == Items.Pumpkin:
		plantPumpkin()
	elif target == Items.Cactus:
		plantCactus()
	elif target == Items.Power:
		plantSunflower()
	elif target == Items.Bone:
		doDinosaur()
# ---------------------------------------------------------
def plantGrass():
	for i in range(size):
		for j in range(size):
			harv()
			if get_ground_type() != Grounds.Grassland:
				till()
			move(North)
		move(East)
				
def plantTree():
	for i in range(size):
		for j in range(size):
			harv()
			if (i + j) % 2 == 0:
				plant(Entities.Tree)
			else:
				plant(Entities.Bush)
			move(North)
		move(East)

def plantCarrot():
	for i in range(size):
		for j in range(size):
			harv()
			if get_ground_type() != Grounds.Soil:
				till()
			plant(Entities.Carrot)
			move(North)
		move(East)
		
def plantPumpkin():
	# 第一遍犁地
	for i in range(size):
		for j in range(size):
			harv()
			if get_ground_type() != Grounds.Soil:
				till()
			plant(Entities.Pumpkin)
			move(North)
		move(East)
	
	# 更新地块状态
	deadList = []
	for i in range(size):
		for j in range(size):
			if can_harvest() == False:
				deadList.append([i, j])
			move(North)
		move(East)
	
	# 吃掉坏南瓜
	while True:
		# 跳出
		if len(deadList) == 0:
			break
			
		# 排序
		sortedList = sortPosByDistance(deadList)
		
		# 补种
		for pos in sortedList:
			moveTo(pos)
			plant(Entities.Pumpkin)
		
		# 检测
		for pos in sortedList:
			moveTo(pos)
			if can_harvest() == True:
				deadList.remove(pos)
	
	# 无人机复位
	moveTo([0, 0])

def plantSunflower():
	# 第一遍犁地
	petalCount = []
	for i in range(size):
		colCount = []
		for j in range(size):
			harv()
			if get_ground_type() != Grounds.Soil:
				till()
			plant(Entities.Sunflower)
			water()
			colCount.append(measure())
			move(North)
		petalCount.append(colCount)
		move(East)

	# 分组
	groupTiles = {}
	for i in range(size):
		for j in range(size):
			count = petalCount[i][j]
			if count not in groupTiles:
				groupTiles[count] = []
			groupTiles[count].append([i, j])

	# 排序收获
	for p in range(15, 6, -1):
		if p not in groupTiles:
			continue
		tileList = groupTiles[p]
		
		sortedList = sortPosByDistance(tileList)
		
		for pos in sortedList:
			moveTo(pos)
			harv()
			
	# 无人机复位
	moveTo([0, 0])

def plantCactus():
	# 第一遍犁地
	for i in range(size):
		for j in range(size):
			harv()
			if get_ground_type() != Grounds.Soil:
				till()
			plant(Entities.Cactus)
			move(North)
		move(East)
	
	# 按行冒泡
	for j in range(size):
		moveTo([0, j])

		for m in range(size):
			moveTo([0, j])
			ifSwapped = False
			for n in range(size - m - 1):
				currentSize = measure()
				nextSize = measure(East)
				if currentSize > nextSize:
					swap(East)
					ifSwapped = True
				if n < size - m - 2:
					move(East)
			if ifSwapped == False:
				break
	
	# 按列冒泡
	for i in range(size):
		moveTo([i, 0])

		for m in range(size):
			moveTo([i, 0])
			ifSwapped = False
			for n in range(size - m - 1):
				currentSize = measure()
				nextSize = measure(North)
				if currentSize > nextSize:
					swap(North)
					ifSwapped = True
				if n < size - m - 2:
					move(North)
			if ifSwapped == False:
				break
	
	# 无人机复位
	moveTo([0, 0])

def dinomove(direction):
	harv()
	if move(direction) == False:
		change_hat(Hats.Purple_Hat)
		moveTo([0, 0])
		return False
	return True

def doDinosaur():
	change_hat(Hats.Dinosaur_Hat)
	dinomove(North)
	for i in range(size - 1):
		if i % 2 == 0:
			for j in range(1, size - 1):
				dinomove(North)
		else:
			for j in range(1, size - 1):
				dinomove(South)
		dinomove(East)
	for j in range(size - 1):
		dinomove(South)
	for i in range(size - 1):
		dinomove(West)
	change_hat(Hats.Purple_Hat)
# ---------------------------------------------------------
def main():
	clear()
	
	while True:
		# target update
		if num_items(Items.Power) < 1000:
			target = targetUpdate(Items.Power)
		else:
			target = targetUpdate(Items.Bone)
		
		plantFarm(target)
# ---------------------------------------------------------
if __name__ == "__main__":
	main()