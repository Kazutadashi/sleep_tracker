# libraries
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

PATH_TO_FILE = "C:/Users/Kazutadashi/Documents/Python/Mental Health/sleep_data.csv"
COLOR_KEY = {'b': 'gray', 's': 'black', 'a': 'silver', 'n': 'silver'}

def sum_all_lists(list_of_lists):
    '''
    Sums a list of lists elementwise.

    :param list_of_lists: The list of lists that you want to sum up
    :return: The sum of all piecewise elements in the list

    Example:
    >> list_of_lists = [[1,2,4,5], [6,5,4,3], [6,5,8,3], [1,4,5,6], [9,0,2,3]]
    >> sum_all_lists(list_of_lists)
        [23, 16, 23, 20]
    '''

    current_sum = []
    for single_list in enumerate(list_of_lists):
        # Checks to see if we are using the first list, if so then just add it and don't check the list before
        if single_list[0] == 0:
            current_sum = single_list[1]
        else:
            # Sum up each element for the current list, and the list before.
            current_sum = [x + y for x, y in zip(list_of_lists[single_list[0]], current_sum)]
    return current_sum


def find_differences(list_of_lists):
    """
    Finds the difference between two lists. Compares the nth with nth-1 list

    :param list_of_lists: A list containing lists of values.
    :return: The differences between each pair of lists

    Example:
    >> list_of_lists = [[1,2,4,5], [6,5,4,3], [6,5,8,3], [1,4,5,6], [9,0,2,3]]
    >> find_differences(list_of_lists)
        [[1, 2, 4, 5], [5, 3, 0, 2], [0, 0, 4, 0], [5, 1, 3, 3], [8, 4, 3, 3]]
    """

    time_blocks = []
    for times in enumerate(list_of_lists):
        if times[0] == 0:
            time_blocks.append(times[1])
        else:
            temp = []
            for a_i, b_i in zip(list_of_lists[times[0]], list_of_lists[times[0] - 1]):
                # If either of these values are -1, then we had no entry for this cell in the sleeping data.
                # To avoid adding extra non-existent time, we set the difference to 0.
                if a_i == -1 or b_i == -1:
                    a_i = b_i
                temp.append(abs(a_i - b_i))
            time_blocks.append(temp)
    return time_blocks


def get_colors(lists_of_lists_of_times):
    """
    Gets color data from each data point. Each data point is in the form "cHH:MMpm/am"
    where c is the color value, and HH:MM is the 12 hour time format. This is used to properly
    color the stacked barchart to visualize the sleeping patterns.

    :param lists_of_lists_of_times: All data points from the data
    :return: A list of colors for each row of data.

    Example:
    >> data = [[e12:00am,e12:00am,e12:00am,e12:00am]
                [b1:00am,a3:00am,a3:33am,a1:00am]
                [s8:00am,b5:00am,b5:20am,b1:30am]]
    >> get_colors(data)
        [[e,e,e,e], [b,a,a,a], [s,b,b,b]]
    """

    colors = []
    # For each column i, and each row j, find the ijth element and add the color value to the list
    for i in range(len(lists_of_lists_of_times)):
        current_colors = []
        for j in range(len(lists_of_lists_of_times[i])):
            if type(lists_of_lists_of_times[i][j]) == float:
                current_colors.append('n')
            else:
                current_colors.append(lists_of_lists_of_times[i][j][0])
        colors.append(current_colors)
    return colors


def convert_times_to_seconds(lists_of_lists_of_times):
    """
    Converts a 12 hour time formatted data point into seconds to use in time calculation.

    :param lists_of_lists_of_times: All data points from the data
    :return: returns a list of lists containing numbers ranging from 0 to 86400 (12:00am/start to 12:00am/end)

    Example:
    >> data = [[e12:00am,e12:00am,e12:00am,e12:00am]
                [b1:00am,a3:00am,a3:33am,a1:00am]]
    >> get_colors(data)
        [[0, 0, 0, 0], [3600, 10800, 12780, 3600]]
    """
    colors = []
    for i in range(len(lists_of_lists_of_times)):
        current_colors = []
        for j in range(len(lists_of_lists_of_times[i])):
            # Check to see if the entry is missing (or is nan),
            # if it is, change this value to -1 for use in other functions.
            if type(lists_of_lists_of_times[i][j]) == float:
                lists_of_lists_of_times[i][j] = -1
            else:
                # removes the symbol at the beginning of the value. This is used later to determine what color we need
                time_to_convert = lists_of_lists_of_times[i][j][1:]

                # Converts from 12H format to 24H
                in_time = datetime.datetime.strptime(time_to_convert, "%I:%M%p").strftime("%H:%M")
                military_time = in_time.split(":")

                # Lastly we convert the time into seconds for later calculations
                seconds = int(military_time[0]) * 3600 + int(military_time[1]) * 60
                lists_of_lists_of_times[i][j] = seconds
    return lists_of_lists_of_times


def plot_sleep(PATH_TO_FILE):
    """
    Plots the sleeping data using a stacked barchat. Each block represents a state which can be
    - a: awake
    - b: in bed
    - s: sleeping

    Each piece of the plot represents a block of time during the day with a color to represent what state
    we are in during that time block.

    :param PATH_TO_FILE: Path to sleeping data
    :return: Nothing. Plots a matplotlib barchat.
    """

    # Loads data and gives us the shape of the data to use in determining amount of time blocks.
    sleeping_data = pd.read_csv(PATH_TO_FILE)
    shape = sleeping_data.shape

    # Getting the dates to plot for each day
    dates = sleeping_data.columns.tolist()

    # Converts the data into a 2 dimensional python list.
    # Note for future projects: Not sure why I did this, as it only complicated things later, just stick with dataframes.
    all_sleep_events = []
    for i in range(shape[0]):
        temp_event = []
        for j in range(shape[1]):
            # Takes each data point and adds it to a list
            temp_event.append(sleeping_data.iloc[i, j])
        # Adds the row to the main 2d list.
        all_sleep_events.append(temp_event)

    # Tells us how many xticks we will need.
    r = range(shape[1])

    # Gets the color data from our data.
    color_data = get_colors(all_sleep_events)

    # Converts all time into seconds, so we can do math on it.
    all_sleep_events = convert_times_to_seconds(all_sleep_events)

    # Set width of barplots.
    barWidth = 1

    # finding the differences of each row for proper placement of timeblocks
    time_blocks = find_differences(all_sleep_events)

    # Adds a barplot to the graph. If it is the first one, we start from 0, if it is not, we start from the top of the
    # last time block and stack them on top of each other. This gives us a stacked barplot where each section is a block
    # of time.
    bottom_of_next_block = []
    previous_events = []
    previous_event = []
    for event in enumerate(time_blocks):

        # If we are the beginning of our times, then we don't need to check the previous one
        # After, set the previous event to the one we just checked.
        if event[0] == 0:
            plt.bar(r, event[1], edgecolor='white', width=barWidth)
            previous_event = event[1]
            previous_events.append(previous_event)

        else:
            # Sum up all of the previous blocks, and this value as the new height the block needs to be stacked on
            bottom_of_next_block = sum_all_lists(previous_events)

            # Convert the color symbols in the data into colors for matplotlib to use.
            current_bar_color = []
            for item in color_data[event[0]]:
                current_bar_color.append(COLOR_KEY[item])

            # Plot this row of data, and then add it to the previous blocks to be used for calculating the next bottom.
            plt.bar(r, event[1], color=current_bar_color, edgecolor='white', width=barWidth, bottom=bottom_of_next_block)
            previous_event = event[1]
            previous_events.append(previous_event)

    # Setting the xticks correctly.
    plt.xticks(r, dates, fontweight='normal', rotation="45", ha="right")

    # Setting the yticks correctly.
    # Makes a tick for each hour (every 3600 seconds)
    y_ticks = list(np.arange(0, 86400, 3600))

    # Relabels each ytick that is currently in seconds, to standard 12 hour time format
    y_labels = []
    for y_tick in y_ticks:
        seconds_to_hm = str(datetime.timedelta(seconds=int(y_tick)))
        final = datetime.datetime.strptime(seconds_to_hm, "%H:%M:%S").strftime("%I:%M%p")
        y_labels.append(final)
    plt.yticks(y_ticks, labels=y_labels)

    # Show graphic
    plt.show()

plot_sleep(PATH_TO_FILE)
