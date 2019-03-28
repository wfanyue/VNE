import time
from network import Network
from analysis import Analysis
from algorithm import Algorithm


def main():

    # Step1: 读取底层网络和虚拟网络请求文件
    network_files_dir = 'networks/'
    sub_filename = 'sub-wm.txt'
    networks = Network(network_files_dir)
    sub, queue1, queue2 = networks.get_networks_single_layer(sub_filename, 1000)

    # Step2: 配置映射算法
    node_arg = 50
    algorithm = Algorithm('ml_1', node_arg=node_arg, link_arg=5)
    algorithm.configure(sub)

    # Step3: 处理虚拟网络请求事件
    start = time.time()
    algorithm.handle(sub, queue1, queue2)
    time_cost = time.time() - start
    print(time_cost)

    # Step4: 输出映射结果文件
    tool = Analysis('results_single/')
    tool.save_result(algorithm.evaluation, 'ML-VNE-%s-2.txt' % node_arg)


if __name__ == '__main__':
    main()