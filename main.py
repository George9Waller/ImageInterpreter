# Project to parse image files and create a sample of all the colours
import math
import colorsys
from random import shuffle
from PIL import Image, ImageDraw
from suggestions import suggestions_algorithm


def parse_pixels(image):
    """Takes an image and returns a dictionary of its colours, ordered by appearance, and their frequency"""
    # converts the image to rgb colour space
    image.convert("RGB")

    # initialises a new dictionary
    colours = {}

    print("Parsing image pixels: {} todo".format(image.width * image.height))
    # iterates through all the pixels in the image by column and then row
    for j in range(image.width):
        for k in range(image.height):
            # if the colour is already in the dictionary then the frequency value is incremented by 1
            if image.getpixel((j, k)) in colours:
                colours[image.getpixel((j, k))] += 1
            else:
                # otherwise a new key is made in the dictionary for the colour
                colours[image.getpixel((j, k))] = 1

    return colours


def create_colour_graphic(image, width=2000, random=False, grid=50):
    """Creates an image from a dictionary's of colours"""
    # get a dictionary of all the colours
    colours = parse_pixels(image)

    # calculate total number of pixels and create a blank image
    height = image.width * image.height
    colour_graphic = Image.new("RGB", (width, 60000))

    # calculate the minimum frequency required for one pixel in the new file
    specific_value = math.ceil(height / 60000)

    # iterates over the dictionary of colours and removes all with less than the minimum frequency for one pixel
    multiplier = 1.002
    graphic_height = 0
    reduced_colours = {}

    while graphic_height < 60000:
        reduced_colours = {}
        graphic_height = 0
        multiplier -= 0.002
        """iterates over the dictionary of colours and creates a reduced set with all colours occupying at least one 
        pixel based on the multiplied specific_value"""
        for key, value in list(colours.items()):
            if colours[key] >= math.floor(specific_value * multiplier):
                reduced_colours[key] = value
                # calculate the height which will be occupied in the graphic
                frequency = math.floor(value / (specific_value * multiplier))
                if frequency == 0:
                    frequency = 1
                graphic_height += frequency

        print('height: {} | frequency needed: {} | multiplier: {}'.format(graphic_height,
                                                                          math.floor(specific_value * multiplier),
                                                                          multiplier))

    # creates a drawing object
    draw = ImageDraw.Draw(colour_graphic)

    # randomises the colours if parameter passed
    colour_data_set = list(reduced_colours.items())
    if random:
        colour_data_set = list(reduced_colours.items())
        shuffle(colour_data_set)

    # iterates over all the colours in the reduced dictionary & draws rectangles with a proportional height to frequency
    y = 0
    for key, value in colour_data_set:
        # sets the height for each rectangle and ensures it is at least 1 pixel tall
        frequency = math.floor(value / (specific_value * multiplier))
        if frequency == 0:
            frequency = 1

        draw.rectangle([(0, y), (width - 1, y + frequency)], fill='rgb' + str(key[:3]))
        # print("Rectangle with coordinates ({}, {}), ({}, {}) and a colour of {}".format(0, y, width - 1, y +
        # frequency, key[:3]))
        y += frequency
        if y >= 60000:
            break

    # grid top colours
    colour_key_list = [key for key, value in colour_data_set]
    create_grid(colour_key_list[:grid*grid], 'colour_grid.png', grid)

    # sorted top colours
    sorted_colour_key_list = sort_colours(colour_key_list[:2500])
    create_grid(sort_colours(colour_key_list[:grid*grid]), 'colour_grid_sorted.png', grid)

    # calculate suggestions
    create_suggestions(colours.items(), colour_key_list, random=False, grid=grid)

    # returns the resulting graphic as an image
    return colour_graphic


def create_suggestions(colours, colour_key_list, random=False, grid=50):
    """Creates an image file from the suggestions algorithm"""
    colour_data_set = suggestions_algorithm(colours, number_requested=(grid * grid))
    if random:
        shuffle(colour_data_set)
    create_grid(colour_data_set, 'suggestions_graphic.png', grid)

    sorted_colour_key_list = sort_colours(colour_data_set)

    create_grid(sorted_colour_key_list, 'suggestions_graphic_sorted.png', grid)


def sort_colours(colour_key_list):
    # convert 0-255 colours to 0-1 float
    colour_float_list = list()
    for elem in colour_key_list:
        new_colour = []
        for x in range(3):
            new_colour.append(elem[x] / 255.0)
        colour_float_list.append(new_colour)

    colour_float_list.sort(key=lambda rgb: colorsys.rgb_to_hls(*rgb))

    sorted_colour_key_list = []
    for elem in colour_float_list:
        new_colour = []
        for colour_value in elem:
            new_colour.append(int(colour_value * 255))
        sorted_colour_key_list.append(tuple(new_colour))

    return sorted_colour_key_list


def create_grid(colours, name, grid):
    swatch_width = 200
    length = (grid * swatch_width) + (grid * 10)
    suggestions_graphic = Image.new("RGB", (length, length))
    draw = ImageDraw.Draw(suggestions_graphic)
    x = 0
    y = 10
    count = 0

    for elem in colours:
        x += 10
        draw.rectangle([(x, y), (x + swatch_width, y + swatch_width)], fill='rgb' + str(elem[:3]))
        draw.text((x+5, y+5), str(elem[:3]), fill=choose_colour_contrast(elem[:3]))
        x += swatch_width
        count += 1
        if count == grid:
            count = 0
            x = 0
            y += swatch_width + 10

    suggestions_graphic.save(name, 'PNG')


def calculate_colour(c):
    """run the contrast calculation on a rgb component"""
    c = c / 255.0
    if c <= 0.03928:
        c = c / 12.92
    else:
        c = math.pow((c + 0.055) / 1.055, 2.4)
    return c


def choose_colour_contrast(colour):
    L = (0.2126 * colour[0]) + (0.7152 * colour[1]) + (0.0722 * colour[2])
    if L > 150:
        text_colour = (0, 0, 0)
    else:
        text_colour = (255, 255, 255)

    return text_colour


def create_image(filename):
    # open image
    try:
        im = Image.open(filename)
    except FileNotFoundError:
        print('File Not Found: process aborted')
        return None 

    # call the function and saves the result
    colour_graphic = create_colour_graphic(im, random=False)
    colour_graphic.save('colour_graphic.png', 'PNG')


if __name__ == '__main__':
    create_image('Foxy.jpg')
