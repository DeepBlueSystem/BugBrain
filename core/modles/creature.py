import random
import torch
import numpy as np
from core.brain.brain import BugBrain
import pygame

# ======================
# 虫子类（猎物）
# ======================
class Bug:
    def __init__(self, brain=None, x=None, y=None, config=None, generation=0):
        self.config = config  # 全局配置（世界大小、速度等）
        # 随机出生位置
        self.x = x or random.randint(100, config['world']['width']-100)
        self.y = y or random.randint(100, config['world']['height']-100)
        
        self.speed = config['creature']['speed']  # 移动速度
        self.size = 6  # 身体大小
        self.energy = 100  # 能量，耗尽即死亡
        self.age = 0  # 年龄
        self.max_age = 600  # 最大寿命
        
        # 大脑神经网络，如果没传入就新建一个
        self.brain = brain or BugBrain(input_size=6, hidden_size=8, output_size=2)
        self.color = (180, 220, 80)  # 虫子颜色
        self.generation = generation  # 世代（进化第几代）
        self.iq = 0.5  # 智商评分（用于进化筛选）
        self.eat_count = 0  # 吃东西计数
        self.angle = random.uniform(0, np.pi*2)  # 朝向角度
        self.turn_speed = 0.2  # 转向速度

    # 思考 + 移动（核心AI逻辑）
    def think_and_move(self, foods, predators):
        self.energy -= 0.15  # 持续消耗能量
        self.age += 1  # 年龄增长

        # 寻找最近的食物
        closest_food = None
        min_food_dist = 9999
        for f in foods:
            d = np.hypot(self.x-f.x, self.y-f.y)
            if d < min_food_dist:
                min_food_dist = d
                closest_food = f

        # 寻找最近的捕食者
        closest_pred = None
        min_pred_dist = 9999
        for p in predators:
            d = np.hypot(self.x-p.x, self.y-p.y)
            if d < min_pred_dist:
                min_pred_dist = d
                closest_pred = p

        # 构造大脑输入：食物位置、捕食者位置、能量、年龄
        fx = (closest_food.x - self.x)/self.config['world']['width'] if closest_food else 0
        fy = (closest_food.y - self.y)/self.config['world']['height'] if closest_food else 0
        px = (self.x - closest_pred.x)/self.config['world']['width'] if closest_pred else 0
        py = (self.y - closest_pred.y)/self.config['world']['height'] if closest_pred else 0
        energy = self.energy / 100
        age = self.age / self.max_age

        # 6个输入值
        inputs = [fx, fy, px, py, energy, age]
        # 大脑输出：移动方向 dx, dy
        dx, dy = self.brain(inputs)
        target_dx, target_dy = dx.item(), dy.item()

        # 根据输出调整朝向
        if abs(target_dx)+abs(target_dy) > 0.05:
            target_angle = np.arctan2(target_dy, target_dx)
            diff = (target_angle - self.angle + np.pi) % (2*np.pi) - np.pi
            self.angle += diff * self.turn_speed

        # 加一点随机抖动
        self.angle += random.uniform(-0.02, 0.02)
        self.dx = np.cos(self.angle)
        self.dy = np.sin(self.angle)

        # 移动
        self.x += self.dx * self.speed * 4.5
        self.y += self.dy * self.speed * 4.5
        # 限制在世界范围内
        self.x = np.clip(self.x, 5, self.config['world']['width']-5)
        self.y = np.clip(self.y, 5, self.config['world']['height']-5)

    # 吃食物，恢复能量
    def eat(self, foods):
        for i, f in enumerate(foods):
            if np.hypot(self.x-f.x, self.y-f.y) < 10:
                self.energy += 25
                self.eat_count +=1
                self.iq += 0.001  # 吃的越多越“聪明”
                del foods[i]
                return

    # 繁殖（遗传 + 变异）
    def reproduce(self):
        if self.energy > 70 and random.random() < 0.015:
            self.energy -= 40
            baby_brain = self.brain.copy()  # 复制大脑
            baby_brain.mutate(0.1)  # 变异
            baby = Bug(brain=baby_brain, config=self.config, generation=self.generation+1)
            baby.iq = self.iq * random.uniform(0.92, 1.08)
            return baby
        return None

    # 是否死亡（能量耗尽 / 老死）
    def is_dead(self):
        return self.energy <=0 or self.age>self.max_age

    # 绘制虫子到屏幕
    def draw(self, screen):
        x,y=int(self.x),int(self.y)
        pygame.draw.ellipse(screen, self.color, (x-6,y-2,12,4))
        head = (self.color[0]+50, self.color[1]+30, self.color[2]+20)
        pygame.draw.circle(screen, head, (x,y), 3)
        a1 = (x+np.cos(self.angle-0.3)*6, y+np.sin(self.angle-0.3)*6)
        a2 = (x+np.cos(self.angle+0.3)*6, y+np.sin(self.angle+0.3)*6)
        pygame.draw.line(screen,head,(x,y),a1,2)
        pygame.draw.line(screen,head,(x,y),a2,2)

    # 保存/加载大脑权重
    def save_brain(self, path="bugs/best_bug.pth"):
        self.brain.save(path)

    def load_brain(self, path="bugs/best_bug.pth"):
        self.brain.load(path)

# ======================
# 捕食者类（猎杀虫子）
# ======================
class Predator:
    def __init__(self, brain=None, x=None, y=None, config=None):
        self.config = config
        self.x = x or random.randint(100, config['world']['width']-100)
        self.y = y or random.randint(100, config['world']['height']-100)
        self.speed = 3.2  # 速度比虫子快
        self.size = 10
        self.energy = 180
        self.age = 0
        self.max_age = 1200
        
        # 捕食者的大脑
        self.brain = brain or BugBrain(input_size=4, hidden_size=10, output_size=2)
        self.color = (255, 60, 60)  # 红色
        self.angle = random.uniform(0, np.pi*2)
        self.turn_speed = 0.18

    # 捕食者思考：追踪虫子
    def think_and_move(self, bugs):
        self.energy -= 0.12
        self.age +=1

        # 寻找最近的虫子
        closest_bug = None
        min_dist = 9999
        for b in bugs:
            d = np.hypot(self.x-b.x, self.y-b.y)
            if d < min_dist:
                min_dist = d
                closest_bug = b

        if closest_bug:
            # 输入：虫子位置、距离、能量
            bx = (closest_bug.x - self.x) / self.config['world']['width']
            by = (closest_bug.y - self.y) / self.config['world']['height']
            dist = min_dist / max(self.config['world']['width'], self.config['world']['height'])
            energy = self.energy / 180
            inputs = [bx, by, dist, energy]
            
            # 大脑输出移动方向
            dx, dy = self.brain(inputs)
            target_dx, target_dy = dx.item(), dy.item()

            # 转向朝向虫子
            target_angle = np.arctan2(target_dy, target_dx)
            diff = (target_angle - self.angle + np.pi) % (2*np.pi) - np.pi
            self.angle += diff * self.turn_speed

        # 随机抖动 + 移动
        self.angle += random.uniform(-0.02, 0.02)
        self.dx = np.cos(self.angle)
        self.dy = np.sin(self.angle)
        self.x += self.dx * self.speed * 4
        self.y += self.dy * self.speed * 4
        self.x = np.clip(self.x, 5, self.config['world']['width']-5)
        self.y = np.clip(self.y, 5, self.config['world']['height']-5)

    # 猎杀虫子
    def hunt(self, bugs):
        for i, b in enumerate(bugs):
            if np.hypot(self.x-b.x, self.y-b.y) < 18:
                self.energy += 60
                del bugs[i]
                return

    # 捕食者繁殖
    def reproduce(self):
        if self.energy > 120 and random.random() < 0.006:
            self.energy -= 60
            baby_brain = self.brain.copy()
            baby_brain.mutate(0.08)
            return Predator(brain=baby_brain, config=self.config)
        return None

    # 是否死亡
    def is_dead(self):
        return self.energy <=0 or self.age>self.max_age

    # 绘制捕食者
    def draw(self, screen):
        x,y=int(self.x),int(self.y)
        pygame.draw.ellipse(screen, self.color, (x-10,y-4,20,8))
        head = (255,100,100)
        pygame.draw.circle(screen, head, (x,y), 5)
        a1 = (x+np.cos(self.angle-0.3)*9, y+np.sin(self.angle-0.3)*9)
        a2 = (x+np.cos(self.angle+0.3)*9, y+np.sin(self.angle+0.3)*9)
        pygame.draw.line(screen,head,(x,y),a1,2)
        pygame.draw.line(screen,head,(x,y),a2,2)

    # 保存/加载捕食者大脑
    def save_brain(self, path="predators/best_pred.pth"):
        self.brain.save(path)

    def load_brain(self, path="predators/best_pred.pth"):
        self.brain.load(path)