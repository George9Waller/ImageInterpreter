# Project to parse image files and create a sample of all the colours
import os
import math
import colorsys
from random import shuffle
from PIL import Image, ImageDraw
from suggestions import suggestions_algorithm


class AnalyseImage:
    """Image class"""

    def __init__(self, filename: str):
        """
        Constructor for image
        :type filename: String
        """
        # open image
        try:
            self.__im = Image.open(filename)
        except FileNotFoundError:
            print('File Not Found: process aborted')
            raise

        # image class attributes
        self.color_frequency_bars = None
        self.color_grid = None
        self.color_suggestions_grid = None

        """Private attributes"""
        # create directory
        os.mkdir('./{}'.format(self.__im.filename.split('.')[0]))
        self.__path = './{}'.format(self.__im.filename.split('.')[0])

        # grid variables
        self.__grid_swatch_width = 200
        self.__grid_spacing = 10
        self.__grid_max_size = 100

        # target height which defines the resolution of data calculated - Do Not Exceed 60,000
        self.__target_height = 60000

        # specific value is the frequency required to occupy one pixel of the target height
        self.__specific_value = math.ceil((self.__im.width * self.__im.height) / self.__target_height)

        # Parse Pixels
        self.__colors = self.__parse_pixels()

        # Create color data
        print('Creating color data')
        self.__reduced_colors = self.__refine_color_data()

        # Create suggestions
        print('Gathering suggestions')
        self.__color_suggestions = suggestions_algorithm(self.__colors.items(), number_requested=(
                self.__grid_max_size * self.__grid_max_size))

        # Create reduced color list for grids
        self.__reduced_color_key_ordered_list = list({k: v for k, v in sorted(self.__reduced_colors.items(),
                                                                              key=lambda item: item[1], reverse=True)})

    def create_color_frequency_bars(self, width=2000, random=False, save=True):
        """
        Creates a color frequency bars image file
        :param width: int width of the resulting image, default: 2000
        :param random: bool whether to randomize the order of colours, default: False
        :param save: bool whether to save the resulting image in the format
        {filename}_color_frequency_bars.png to program directory
        :return: A dictionary of the colours used and their frequency in the original
        """
        print('\nCreating Color Frequency Bars for {} | width: {} | height: {} | random: {} | save: {}'
              .format(self.__im.filename, width, self.__target_height, random, save))

        # Create a blank image
        colour_graphic = Image.new("RGB", (width, self.__target_height))

        # creates a drawing object
        draw = ImageDraw.Draw(colour_graphic)

        # randomises the colour data if parameter is passed
        colour_data_set = list(self.__reduced_colors.items())
        if random:
            shuffle(colour_data_set)

        # iterates over colours in the reduced dictionary & draws rectangles with a proportional height to frequency
        y = 0
        for key, value in colour_data_set:
            # sets the height for each rectangle and ensures it is at least 1 pixel tall
            frequency = math.floor(value / (self.__specific_value * self.__multiplier))
            if frequency == 0:
                frequency = 1

            draw.rectangle([(0, y), (width - 1, y + frequency)], fill='rgb' + str(key[:3]))
            y += frequency
            if y >= self.__target_height:
                break

        if save:
            colour_graphic.save('{}/{}_width{}_height{}_random{}_color_frequency_bars.png'
                                .format(self.__path, self.__im.filename.split('.')[0], width, self.__target_height,
                                        random), 'PNG')
            print('Color Frequency Bars saved to the file directory: {}_width{}_height{}_random{}_color_'
                  'frequency_bars.png'.format(self.__im.filename.split('.')[0], width, self.__target_height, random))

        print('Color Frequency Bars: Finished')
        self.color_frequency_bars = colour_graphic
        return colour_data_set

    def create_color_grid(self, ordered=False, random=False, save=True, grid=50, text=True, background=(0, 0, 0)):
        """
        Creates a grid of the image colors
        :param ordered: bool to order the colors chromatically, default: False
        :param random: bool to randomize the order of colors, default: False
        :param save: bool to save the file, default: True
        :param grid: int for the number of rows/columns in the grid, must be 100 or less, default: 50
        :param text: bool to add the color tuple overlay text to each color, default: True
        :param background: rgb tuple for the grid background in the format (r, g, b), default: black
        :return: the list of colors used ordered by frequency
        """
        print('\nCreating Color Grid for {} | ordered: {} | random: {} | grid: {} | text: {} | background: {} | '
              'save: {}'.format(self.__im.filename.split('.')[0], ordered, random, grid, text, background, save))

        # randomizes the color list is parameter passed
        if random:
            color_data_set = self.__reduced_color_key_ordered_list
            shuffle(color_data_set)
            color_data_set = color_data_set[:grid*grid]
        else:
            color_data_set = self.__reduced_color_key_ordered_list[:grid*grid]

        # orders the colors if parameter passed
        if ordered:
            color_grid = self.__create_grid(self.__sort_colors_by_hsl(color_data_set), grid, text, background)

        else:
            color_grid = self.__create_grid(color_data_set, grid, text, background)

        # saves the file
        if save:
            color_grid.save('{}/{}_ordered{}_grid{}_text{}_background{}_color_grid.png'
                            .format(self.__path, self.__im.filename.split('.')[0], ordered, grid, text, background),
                            'PNG')
            print('Color Grid saved to the file directory as: {}_ordered{}_random{}_grid{}_text{}_background{}_'
                  'color_grid.png'.format(self.__im.filename.split('.')[0], ordered, random, grid, text, background))

        print('Color Grid: Finished')
        self.color_grid = color_grid
        return color_data_set

    def create_color_suggestions_grid(self, ordered=False, random=False, save=True, grid=50, text=True,
                                      background=(0, 0, 0)):
        """
        Creates a grid from the suggestions based on the image
        :param ordered: bool to order colors chromatically, default: False
        :param random: bool to randomize to order of colors, default: False
        :param save: bool to save the file, default: True
        :param grid: int for the number of rows/columns in the grid, must be 100 or less, default: 50
        :param text: bool to add the color tuple overlay text to each color, default: True
        :param background: rgb tuple for the grid background in the format (r, g, b), default: black
        :return: the list of rgb tuples used to make the grid
        """
        print('\nCreating Color Suggestions Grid for {} | ordered: {} | random: {} | grid: {} | text: {} | '
              'background: {} | save: {}'.format(self.__im.filename.split('.')[0], ordered, random, grid, text,
                                                 background, save))

        color_data_set = self.__color_suggestions[:grid*grid]

        # randomizes the data if parameter passed
        if random:
            shuffle(self.__color_suggestions)
            color_data_set = color_data_set[:grid * grid]

        # orders the colors is parameter passed
        if ordered:
            color_grid = self.__create_grid(color_data_set, grid, text, background)
        else:
            color_grid = self.__create_grid(self.__sort_colors_by_hsl(color_data_set), grid, text, background)

        # saves the file
        if save:
            color_grid.save(
                '{}/{}_ordered{}_grid{}_text{}_background{}_color_suggestions_grid.png'
                .format(self.__path, self.__im.filename.split('.')[0], ordered, grid, text, background), 'PNG')
            print(
                'Color Suggestions Grid saved to the file directory: {}_ordered{}_random{}_grid{}_text{}_background{}'
                '_color_suggestions_grid.png'.format(self.__im.filename.split('.')[0], ordered, random,
                                                     grid, text, background))

        print('Color Suggestions Grid: Finished')
        self.color_suggestions_grid = color_grid
        return color_data_set

    def __parse_pixels(self):
        """Creates a dictionary of its colours, ordered by appearance, and their frequency for the image object"""
        # converts the image to rgb colour space
        self.__im.convert("RGB")

        # initialises a new dictionary
        colors = {}

        print("Parsing image pixels: {} todo".format(self.__im.width * self.__im.height))
        # iterates through all the pixels in the image by column and then row
        for x in range(self.__im.width):
            for y in range(self.__im.height):
                # if the colour is already in the dictionary then the frequency value is incremented by 1
                if self.__im.getpixel((x, y)) in colors:
                    colors[self.__im.getpixel((x, y))] += 1
                else:
                    # otherwise a new key is made in the dictionary for the colour
                    colors[self.__im.getpixel((x, y))] = 1
        return colors

    def __refine_color_data(self):
        """Refines the color data to the resolution of the specific value, reducing the multiplier to fill the target
        height - returining a dictionary of the color rgba(255, 255, 255, 255) and frequency """
        # iterates over the dictionary of colours and removes all with less than the minimum frequency for one pixel
        self.__multiplier = 1.002
        graphic_height = 0
        reduced_colours = {}

        while graphic_height < self.__target_height:
            reduced_colours = {}
            graphic_height = 0
            self.__multiplier -= 0.002
            """iterates over the dictionary of colours and creates a reduced set with all colours occupying at least one 
            pixel based on the multiplied specific_value"""
            for key, value in list(self.__colors.items()):
                if self.__colors[key] >= math.floor(self.__specific_value * self.__multiplier):
                    reduced_colours[key] = value
                    # calculate the height which will be occupied in the graphic
                    frequency = math.floor(value / (self.__specific_value * self.__multiplier))
                    if frequency == 0:
                        frequency = 1
                    graphic_height += frequency

            """print('height: {} | frequency needed: {} | multiplier: {}'
                  .format(graphic_height, math.floor(self.__specific_value * self.__multiplier), self.__multiplier))"""
        return reduced_colours

    def __create_grid(self, colors, grid=50, text=True, background=(0, 0, 0)):
        """
        Creates a grid image from the supplied colors
        :param colors: a list of rgb color tuples in the format (r, g, b) 0-255
        :param grid: an integer for the number of rows/columns, max 100, default: 50
        :param text: a bool for whether to overlay the tuple as text on each color, default: True
        :param background: an rgb tuple for the grid background, default: black
        :return: an Image object with the color grid drawn on it
        """
        # limit grid to __max_grid_size
        if grid > self.__grid_max_size:
            grid = self.__grid_max_size

        # Create image file
        length = (grid * self.__grid_swatch_width) + (grid * self.__grid_spacing)
        grid_graphic = Image.new("RGB", (length, length), color=background)
        draw = ImageDraw.Draw(grid_graphic)

        # variables for drawing
        x = 0
        y = self.__grid_spacing
        count = 0

        # Draw grid
        for color in colors:
            x += self.__grid_spacing
            draw.rectangle([(x, y), (x + self.__grid_swatch_width, y + self.__grid_swatch_width)],
                           fill='rgb' + str(color[:3]))
            if text:
                draw.text((x+5, y+5), str(color[:3]), fill=self.__choose_text_contrast_color(color[:3]))
            x += self.__grid_swatch_width
            count += 1

            # starts a new line if count reaches full width
            if count >= grid:
                count = 0
                x = 0
                y += (self.__grid_swatch_width + self.__grid_spacing)

        return grid_graphic

    @staticmethod
    def __choose_text_contrast_color(color):
        """
        Uses color luminosity to decide if overlay text should be white or black
        :param color: A tuple in the format (r, g, b) with values 0-255
        :return: A tuple in the format (r, g, b) for either white or black
        """
        L = (0.2126 * color[0]) + (0.7152 * color[1]) + (0.0722 * color[2])
        if L > 150:
            text_colour = (0, 0, 0)
        else:
            text_colour = (255, 255, 255)

        return text_colour

    @staticmethod
    def __sort_colors_by_hsl(color_key_list):
        """
        Sorts colors by HSL
        :param color_key_list: a list of color tuples in the format (r, g, b) 0-255
        :return: a sorted list of color tuples in the format (r, g, b) 0-255
        """
        # convert 0-255 colours to 0-1 float
        color_float_list = list()
        for elem in color_key_list:
            new_colour = []
            for x in range(3):
                new_colour.append(elem[x] / 255.0)
            color_float_list.append(new_colour)

        # sorts colors
        color_float_list.sort(key=lambda rgb: colorsys.rgb_to_hls(*rgb))

        # converts sorted floats to 0-255 integers
        sorted_color_key_list = []
        for elem in color_float_list:
            new_colour = []
            for colour_value in elem:
                new_colour.append(int(colour_value * 255))
            sorted_color_key_list.append(tuple(new_colour))

        return sorted_color_key_list


if __name__ == '__main__':
    analysed_image = AnalyseImage('Foxy.jpg')

    analysed_image.create_color_frequency_bars()
    analysed_image.create_color_frequency_bars(random=True)

    analysed_image.create_color_grid(random=True)
    analysed_image.create_color_grid(random=True, text=False)
    analysed_image.create_color_grid(ordered=True)
    analysed_image.create_color_grid(random=True, ordered=True)

    analysed_image.create_color_suggestions_grid(random=True)
    analysed_image.create_color_suggestions_grid(random=True, text=False)
    analysed_image.create_color_suggestions_grid(ordered=True)
    analysed_image.create_color_suggestions_grid(random=True, ordered=True)
