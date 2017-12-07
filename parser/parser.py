import matplotlib.pyplot as plt
import numpy as np
import os

results = open("longresults", "r")

algorithms = ['cubic', 'ctcp', 'dctcp', 'bic', 'bbr']
delays = [8, 80, 150, 220, 290]
losses = [0, 0.01, 0.1, 0.6, 1.2]
interval = 1 #1 second per bandwidth measurement
result_data = {}
counter = 1

def plot_graph(dataset, base_algo, sub_algo, loss, delay):
    base_plot = {}
    sub_plot = {} 
    
    for result in dataset:
        if dataset[result][0]["run"] == "1" or dataset[result][0]["run"] == "2": #Always combined same run in dict
            #Yes, the if statement below is pretty useless. As of now. Not sure if this will have a purpose. 
            if dataset[result][0]["c"] == "1":
                t = 0
                u = 1
            elif dataset[result][0]["c"] == "2":
                t = 0 
                u = 1
            if len(dataset[result]) < 2:
                print("Not complete error for algorithm: " + base_algo + " in combination with " + sub_algo) 
                return False
            if dataset[result][t]["algo"] == base_algo and dataset[result][u]["algo"] == sub_algo:
                if dataset[result][t]["loss"] == loss and dataset[result][t]["delay"] == delay: #The other one will always have the same delay and loss
                    base_plot[dataset[result][t]["run"]] = [int(x) for x in dataset[result][t]["bandwidth"].split(" ")]
                    sub_plot[dataset[result][u]["run"]] = [int(x) for x in dataset[result][u]["bandwidth"].split(" ")]
    
    if "1" not in base_plot:
        return False

    print("Bandwidth points " + base_algo +  " per 1 second: " + str(base_plot))
    print("Bandwidth points " + sub_algo + " per 1 second: " + str(sub_plot)) 
    base_y = np.array(base_plot["1"])
    sub_y = np.array(sub_plot["1"])
    base_algor, = plt.plot(base_y, label=base_algo, color="red")
    sub_algor, = plt.plot(sub_y, label=sub_algo, color="darkgreen")
    plot_height = max(max(base_plot["1"]), max(sub_plot["1"])) + 1000
    if len(base_plot) > 1 and len(sub_plot) > 1:
        base_y_2 = np.array(base_plot["2"])
        sub_y_2 = np.array(sub_plot["2"])
        print(len(base_plot["1"]))
        plot_height = max(max(base_plot["1"]), max(sub_plot["1"]), max(base_plot["2"]), max(sub_plot["2"])) + 1000
        label1 = base_algo + " reverse"
        label2 = sub_algo + " reverse"
        base_algo_2, = plt.plot(base_y_2, label=label1, color="purple")
        sub_algo_2, = plt.plot(sub_y_2, label=label2, color="lightgreen")
        plt.legend(handles=[base_algor, sub_algor, base_algo_2, sub_algo_2])
    else:
        plt.legend(handles=[base_algor, sub_algor])
    plt.ylabel("Bytes sent")
    plt.xlabel("Seconds")
    plt.axis([0,20,20000,plot_height])
    if not os.path.exists(base_algo):
        os.makedirs(base_algo)
    filename = base_algo + "/" + base_algo + "_vs_" + sub_algo + "_" + delay + "_" + loss + ".png"
    plt.savefig(filename)
    plt.close()
    #plt.show()
    return True

for result in results:
    if result != "\n":
        parameters = result.split(":")
        test_info = parameters[0]
        test_data = parameters[1].rstrip("\n").lstrip()
        dictionary = dict(item.split("=") for item in test_info.split(" "))
        dictionary.update({"bandwidth":test_data})
        if dictionary["testnum"] not in result_data:
            result_data[dictionary["testnum"]] = [dictionary]
        else:
            result_data[dictionary["testnum"]].append(dictionary)

print("length result_data: " + str(len(result_data)))
#print(result_data)

# Plot graph for base_algorithm and sub_algorithm
for delay in delays:
    for loss in losses:
        plot_graph(result_data, "cubic", "bbr" , str(loss), str(delay))


