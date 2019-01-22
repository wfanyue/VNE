import math
import random
import os
import numpy as np

# 仿真时间
TOTAL_TIME = 50000

# 生成网络所需的参数
SCALE = 100
NODE_CAPACITY = 100
LINK_CAPACITY = 100

# 仅与虚拟网络请求相关的参数
DURATION_MEAN = 1000
MIN_DURATION = 250
MIN_NUM_NODE = 3
MAX_NUM_NODE = 20
MAX_DISTANCE = 20

# itm和sgb2alt指令的绝对路径
itm = '/home/kuso/ns-2.35/gt-itm/bin/itm'
sgb2alt = '/home/kuso/ns-2.35/gt-itm/bin/sgb2alt'

# 生成文件的存放目录
spec_dir = 'generated/spec/'
alt_dir = 'generated/alt/'
save_path = 'networks/'
if not os.path.exists(spec_dir):
    os.makedirs(spec_dir)
if not os.path.exists(alt_dir):
    os.makedirs(alt_dir)
if not os.path.exists(save_path):
    os.makedirs(save_path)


def dis(coordinate1, coordinate2):
    """给定两个节点坐标，求解它们之间的欧氏距离"""
    return math.sqrt(pow(coordinate1[0] - coordinate2[0], 2) + pow(coordinate1[1] - coordinate2[1], 2))


def make_sub_wm(nodes_number, connect_prob):
    """生成物理网络文件（基于waxman随机型网络模型）"""

    # Step1: 生成GT-ITM配置文件
    spec_filename = 'itm-spec-sub'
    with open(spec_dir + spec_filename, 'w') as f:
        f.write("geo 1\n")
        f.write("%d %d 2 %f 0.2\n" % (nodes_number, SCALE, connect_prob))

    # Step2: 执行itm指令生成.gb文件
    cmd = "%s %s" % (itm, spec_dir + spec_filename)
    os.system(cmd)

    # Step3: 执行sgb2alt指令将刚刚生成的gb文件转换为alt文件
    gb_filename = spec_filename + '-0.gb'
    alt_filename = 'sub.alt'
    cmd = "%s %s %s" % (sgb2alt, spec_dir + gb_filename, alt_dir + alt_filename)
    os.system(cmd)

    # Step4: 读取刚刚生成的alt文件
    with open(alt_dir + alt_filename) as f:
        lines = f.readlines()

    # Step5: 生成物理网络并存储为指定文件
    sub_filename = 'sub.txt'
    with open(save_path + sub_filename, 'w') as sub_file:

        coordinates = []

        # Step5-1: 写入物理网络的节点数量和链路数量
        a, b, c, d = [x for x in lines[1].split()]
        num_nodes = int(a)
        num_edges = int(int(b) / 2)
        sub_file.write("%d %d\n" % (num_nodes, num_edges))

        # Step5-2: 依次写入节点信息（x坐标，y坐标，拥有的节点资源）
        for line in lines[4:4 + num_nodes]:
            t1, t2, x, y = [int(x) for x in line.split()]
            coordinates.append((x, y))
            resource = random.uniform(1, 2) * NODE_CAPACITY * 0.5
            sub_file.write("%d %d %f\n" % (x, y, resource))

        # Step5-3: 依次写入链路信息（起始节点，终止节点，拥有的带宽资源，长度）
        for line in lines[-num_edges:]:
            from_id, to_id, length, a = [int(x) for x in line.split()]
            resource = random.uniform(1, 2) * LINK_CAPACITY * 0.5
            distance = dis(coordinates[from_id], coordinates[to_id])
            sub_file.write("%d %d %f %f\n" % (from_id, to_id, resource, distance))


# transits： transit域数量
# stubs: 每个transit节点连接的stub域数量
# transit_nodes: 每个transit域中节点数量
# transit_p: transit域内的连通性
# stub_nodes: 每个stub域中节点数量
# stub_p: stub域内的连通性
def make_sub_ts(transits, stubs, transit_nodes, transit_p, stub_nodes, stub_p):
    """生成物理网络文件（基于Transit-Stub模型）"""

    # Step1: 生成GT-ITM配置文件
    spec_filename = 'itm-spec-sub-ts'
    with open(spec_dir + spec_filename, 'w') as f:
        f.write("ts 1 47\n")
        f.write("%d 0 0\n" % stubs)
        f.write("%d 2 3 1.0\n" % transits)
        f.write("%d 5 3 %f\n" % (transit_nodes, transit_p))
        f.write("%d 5 3 %f\n" % (stub_nodes, stub_p))

    # Step2: 执行itm指令生成.gb文件
    cmd = "%s %s" % (itm, spec_dir + spec_filename)
    os.system(cmd)

    # Step3: 执行sgb2alt指令将刚刚生成的gb文件转换为alt文件
    gb_filename = spec_filename + '-0.gb'
    alt_filename = 'sub-ts.alt'
    cmd = "%s %s %s" % (sgb2alt, spec_dir + gb_filename, alt_dir + alt_filename)
    os.system(cmd)

    # Step4: 读取刚刚生成的alt文件
    with open(alt_dir + alt_filename) as f:
        lines = f.readlines()

    # Step5: 生成物理网络并存储为指定文件
    sub_filename = 'sub-ts.txt'
    with open(save_path + sub_filename, 'w') as sub_file:

        coordinates = []

        # Step5-1: 写入物理网络的节点数量和链路数量
        a, b, c, d, e, f, g = [x for x in lines[1].split()]
        num_nodes = int(a)
        num_edges = int(int(b) / 2)
        sub_file.write("%d %d\n" % (num_nodes, num_edges))

        # Step5-2: 依次写入节点信息（x坐标，y坐标，拥有的节点资源）
        count = 0
        for line in lines[4:4 + num_nodes]:
            count += 1
            t1, t2, x, y = [x for x in line.split()]
            x = int(x)
            y = int(y)
            coordinates.append((x, y))
            resource = random.uniform(1, 2) * NODE_CAPACITY * 0.5
            if count <= transit_nodes:
                sub_file.write("%d %d %f\n" % (x, y, 200 + resource))
            else:
                sub_file.write("%d %d %f\n" % (x, y, resource))

        # Step5-3: 依次写入链路信息（起始节点，终止节点，拥有的带宽资源，长度）
        for line in lines[-num_edges:]:
            from_id, to_id, length, a = [int(x) for x in line.split()]
            resource = random.uniform(1, 2) * LINK_CAPACITY * 0.5
            distance = dis(coordinates[from_id], coordinates[to_id])
            if from_id < transit_nodes and to_id < transit_nodes:
                sub_file.write("%d %d %f %f\n" % (from_id, to_id, 200 + resource, distance))
            elif from_id < transit_nodes or to_id < transit_nodes:
                sub_file.write("%d %d %f %f\n" % (from_id, to_id, 100 + resource, distance))
            else:
                sub_file.write("%d %d %f %f\n" % (from_id, to_id, resource, distance))


# possion_mean的含义：虚拟网络请求的到达服从泊松分布，且平均每1000个时间单位内到达的数量为40个
def make_reqs(possion_mean):
    """生成虚拟网络请求文件"""

    # 时间间隔
    interval = 1000
    # 虚拟网络请求数量
    req_num = int(possion_mean / interval * TOTAL_TIME)
    # 在一个时间间隔内到达的VNR数量
    k = 0
    # 记录该时间间隔内已到达的VNR数量
    count_k = 0
    # 记录已经经历了多少个时间间隔
    p = 0
    # 每个时间间隔的起始时间
    start = 0

    # 按照以下步骤分别生成req_num个虚拟网络请求文件
    for i in range(req_num):

        # Step1: 生成GT-ITM配置文件
        spec_filename = 'itm-spec%d' % i
        with open(spec_dir + spec_filename, 'w') as f:
            f.write("geo 1\n")
            t = MIN_NUM_NODE + random.randint(0, MAX_NUM_NODE - MIN_NUM_NODE)
            f.write("%d %d 2 0.5 0.2\n" % (t, SCALE))

        # Step2: 执行itm指令生成gb文件
        cmd = "%s %s" % (itm, spec_dir + spec_filename)
        os.system(cmd)

        # Step3: 执行sgb2alt指令将刚刚生成的gb文件转换为alt文件
        gb_filename = spec_filename + '-0.gb'
        alt_filename = '%d.alt' % i
        cmd = '%s %s %s' % (sgb2alt, spec_dir + gb_filename, alt_dir + alt_filename)
        os.system(cmd)

        # Step4: 读取生成的alt文件
        with open(alt_dir + alt_filename) as f:
            lines = f.readlines()

        # Step5: 生成虚拟网络请求并存储为指定文件
        print("generate req%d" % i)
        req_filename = 'req%d.txt' % i
        with open(save_path + req_filename, 'w') as req_file:

            coordinates = []

            a, b, c, d = [x for x in lines[1].split()]

            # Step5-1: 写入虚拟网络请求整体信息（节点数量、链路数量、到达时间、持续时间、映射范围）
            # ①虚拟网络请求的节点数
            num_nodes = int(a)
            # ②虚拟网络请求的链路数
            num_edges = int(int(b) / 2)
            # ③虚拟网络请求的到达时间（保证虚拟网络请求的到达服从泊松分布）
            if count_k == k:
                k = 0
                while k == 0:
                    k = np.random.poisson(possion_mean)
                count_k = 0
                start = p * interval
                p += 1
            count_k += 1
            time = start + ((count_k + 1) / (k + 1)) * interval
            # ④虚拟网络请求的持续时间（服从指数分布）
            duration = MIN_DURATION + int(-math.log(random.random()) * (DURATION_MEAN - MIN_DURATION))
            req_file.write("%d %d %d %d %d\n" % (num_nodes, num_edges, time, duration, MAX_DISTANCE))

            # Step5-2: 依次写入节点信息（x坐标，y坐标，请求的节点资源）
            for line in lines[4:4 + num_nodes]:
                t1, t2, x, y = [int(x) for x in line.split()]
                coordinates.append((x, y))
                resource = random.random() * NODE_CAPACITY * 0.5
                req_file.write("%d %d %f\n" % (x, y, resource))

            # Step5-3: 依次写入链路信息（起始节点，终止节点，请求的带宽资源，时延）
            for line in lines[-num_edges:]:
                from_id, to_id, length, a = [int(x) for x in line.split()]
                resource = random.random() * LINK_CAPACITY * 0.5
                delay = dis(coordinates[from_id], coordinates[to_id])
                req_file.write("%d %d %f %f\n" % (from_id, to_id, resource, delay))


if __name__ == '__main__':
    # make_sub_wm(100, 0.5)
    # make_sub_ts(1, 3, 4, 0.5, 8, 0.5)
    # 平均每1000个时间单位内到达40个虚拟网络请求
    make_reqs(40)