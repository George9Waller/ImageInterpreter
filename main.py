# Project to parse image files and create a sample of all the colours as graphics
import os
import math
import colorsys
import pickle
from random import shuffle
import bz2
from PIL import Image, ImageDraw
from suggestions import suggestions_algorithm


class AnalyseImage:
    """Image class"""

    def __init__(self, filename: str, use_cache=True, grid_swatch_width=200, grid_spacing=10, target_height=60000):
        """
        Constructor for image
        :param filename: String
        :param use_cache: tells the program to ignore cached data for the image
        :param grid_swatch_width: the width in pixels of each square on a grid graphic
        :param grid_spacing: the number of pixels separating each row/column
        :param target_height: the number of pixels for color frequency bars and number of colors sampled for grids
        """
        # open image
        try:
            self.__im = Image.open('{}'.format(filename))
        except FileNotFoundError:
            print('File Not Found: process aborted')
            raise

        # image class attributes
        self.color_frequency_bars = None
        self.color_grid = None
        self.color_suggestions_grid = None

        """Private attributes"""
        # create directory
        if not os.path.exists('./Results'):
            os.mkdir('./Results')
        try:
            os.mkdir('./Results/{}'.format(self.__im.filename.split('.')[0]))
        except FileExistsError:
            pass
        self.__path = './Results/{}'.format(self.__im.filename.split('.')[0])

        # graphic max length
        self.__max_length = 60000

        # target height which defines the resolution of data calculated - Do Not Exceed 60,000
        self.__target_height = target_height
        if self.__target_height > self.__max_length:
            self.__target_height = self.__max_length

        # specific value is the frequency required to occupy one pixel of the target height
        self.__specific_value = math.ceil((self.__im.width * self.__im.height) / self.__target_height)

        # Parse Pixels
        print('\n{}\n1. Parsing pixels'.format(filename))
        self.__colors = self.__load_data('im_color', self.__parse_pixels, use_cache=use_cache)

        # Check if greyscale
        print('2. Checking if the image is greyscale')
        self.__is_greyscale = self.__check_if_greyscale()

        # Create color data
        print('3. Creating color data')
        self.__reduced_colors = self.__load_data('im_refinedColor', self.__refine_color_data, use_cache=use_cache)

        # Create reduced color list for grids
        self.__reduced_color_key_ordered_list = list({k: v for k, v in sorted(self.__reduced_colors.items(),
                                                                              key=lambda item: item[1], reverse=True)})

        # grid variables
        self.__grid_swatch_width = grid_swatch_width
        self.__grid_spacing = grid_spacing
        self.__grid_max_size = self.__get_max_grid_size(self.__reduced_color_key_ordered_list, self.__grid_swatch_width,
                                                        self.__grid_spacing, output=False)
        self.__grid_extended_max_size = self.__get_max_grid_size(self.__colors.keys(), self.__grid_swatch_width,
                                                                 self.__grid_spacing, output=False)
        print('4. The normal maximum grid size is {}'.format(self.__grid_max_size))

        # Create suggestions
        print('5. Gathering {} suggestions'.format(self.__grid_extended_max_size))
        self.__color_suggestions = self.__load_data('im_suggestions', suggestions_algorithm, use_cache=use_cache,
                                                    colour_dict=self.__colors.items(),
                                                    number_requested=(self.__grid_extended_max_size *
                                                                      self.__grid_extended_max_size))

    def create_color_frequency_bars(self, width=2000, random=False, ordered=False, save=True):
        """
        Creates a color frequency bars image file
        :param width: int width of the resulting image, default: 2000
        :param random: bool whether to randomize the order of colours, default: False
        :param ordered: orders the colors chromatically, overriding the random parameter
        :param save: bool whether to save the resulting image in the format
        {filename}_color_frequency_bars.png to program directory
        :return: A dictionary of the colours used and their frequency in the original
        """
        print('\nCreating Color Frequency Bars for {} | width: {} | height: {} | random: {} | ordered: {} | save: {}'
              .format(self.__im.filename, width, self.__target_height, random, ordered, save))

        # check environment for multiplier
        try:
            print('Multiplier: {}'.format(self.__multiplier))
        except AttributeError:
            print('3.1. recreating color data in current environment')
            self.__refine_color_data()

        # Create a blank image
        colour_graphic = Image.new("RGB", (width, self.__target_height))

        # creates a drawing object
        draw = ImageDraw.Draw(colour_graphic)

        # orders the colors chromatically
        if ordered:
            colour_data_set = self.__sort_dictionary_colors_by_hsl(self.__reduced_colors)
        else:
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
            colour_graphic.save('{}/{}_width{}_height{}_random{}_ordered{}_color_frequency_bars.png'
                                .format(self.__path, self.__im.filename.split('.')[0], width, self.__target_height,
                                        random, ordered), 'PNG')
            print('Color Frequency Bars saved to the Results directory: {}_width{}_height{}_random{}_ordered{}_color_'
                  'frequency_bars.png'.format(self.__im.filename.split('.')[0], width, self.__target_height, random,
                                              ordered))

        print('Color Frequency Bars: Finished')
        self.color_frequency_bars = colour_graphic
        return colour_data_set

    def create_color_grid(self, ordered=False, random=False, save=True, grid=50, text=True, background=(0, 0, 0),
                          extra_large=False, arg_swatch_width=-1, arg_grid_spacing=-1):
        """
        Creates a grid of the image colors
        :param ordered: bool to order the colors chromatically, default: False
        :param random: bool to randomize the order of colors, default: False
        :param save: bool to save the file, default: True
        :param grid: int for the number of rows/columns in the grid, must be 100 or less, default: 50
        :param text: bool to add the color tuple overlay text to each color, default: True
        :param background: rgb tuple for the grid background in the format (r, g, b), default: black
        :param extra_large: overrides reduced color list to make a larger grid
        :param arg_swatch_width: overrides the object default swatch width
        :param arg_grid_spacing: overrides the object default grid spacing
        :return: the list of colors used ordered by frequency
        """

        colors = self.__reduced_color_key_ordered_list
        swatch_width = self.__grid_swatch_width
        grid_spacing = self.__grid_spacing
        max_grid_size = self.__grid_max_size

        if arg_swatch_width > 0:
            swatch_width = arg_swatch_width
        if arg_grid_spacing > -1:
            grid_spacing = arg_grid_spacing

        # override reduced colors
        if extra_large:
            colors = list(self.__colors.keys())
            max_grid_size = self.__get_max_grid_size(colors, swatch_width, grid_spacing)

        self.color_grid = self.__create_grid(colors, grid=grid, text=text,
                                             ordered=ordered, random=random, save=save, suggestions=False,
                                             background=background, arg_swatch_width=swatch_width,
                                             arg_grid_spacing=grid_spacing, arg_max_grid_size=max_grid_size)

        return colors

    def create_color_suggestions_grid(self, ordered=False, random=False, save=True, grid=50, text=True,
                                      background=(0, 0, 0), extra_large=False, arg_swatch_width=-1,
                                      arg_grid_spacing=-1):
        """
        Creates a grid from the suggestions based on the image
        :param ordered: bool to order colors chromatically, default: False
        :param random: bool to randomize to order of colors, default: False
        :param save: bool to save the file, default: True
        :param grid: int for the number of rows/columns in the grid, must be 100 or less, default: 50
        :param text: bool to add the color tuple overlay text to each color, default: True
        :param background: rgb tuple for the grid background in the format (r, g, b), default: black
        :param extra_large: overrides the normal max grid size to the full extended range
        :param arg_swatch_width: overrides the object default swatch width
        :param arg_grid_spacing: overrides the object default grid spacing
        :return: the list of rgb tuples used to make the grid
        """
        swatch_width = self.__grid_swatch_width
        grid_spacing = self.__grid_spacing
        max_grid_size = self.__grid_max_size

        if arg_swatch_width > 0:
            swatch_width = arg_swatch_width
        if arg_grid_spacing > -1:
            grid_spacing = arg_grid_spacing

        if extra_large:
            max_grid_size = self.__get_max_grid_size(self.__color_suggestions, swatch_width, grid_spacing)

        self.color_suggestions_grid = self.__create_grid(self.__color_suggestions, grid=grid, text=text,
                                                         ordered=ordered, random=random, save=save, suggestions=True,
                                                         background=background, arg_swatch_width=swatch_width,
                                                         arg_grid_spacing=grid_spacing, arg_max_grid_size=max_grid_size)

        return self.__color_suggestions

    def create_basic_selection(self, grid_spacing=10, swatch_width=200):
        """
        Creates a basic selection of all graphics for an image
        """
        self.create_color_frequency_bars()
        self.create_color_frequency_bars(random=True)
        analysed_image.create_color_frequency_bars(ordered=True)

        self.create_color_grid(random=True, arg_grid_spacing=grid_spacing, arg_swatch_width=swatch_width)
        self.create_color_grid(random=True, text=False, arg_grid_spacing=grid_spacing, arg_swatch_width=swatch_width)
        self.create_color_grid(ordered=True, arg_grid_spacing=grid_spacing, arg_swatch_width=swatch_width)
        self.create_color_grid(ordered=True, text=False, arg_grid_spacing=grid_spacing, arg_swatch_width=swatch_width)

        self.create_color_suggestions_grid(random=True, arg_grid_spacing=grid_spacing, arg_swatch_width=swatch_width)
        self.create_color_suggestions_grid(random=True, text=False, arg_grid_spacing=grid_spacing,
                                           arg_swatch_width=swatch_width)
        self.create_color_suggestions_grid(ordered=True, arg_grid_spacing=grid_spacing, arg_swatch_width=swatch_width)
        self.create_color_suggestions_grid(ordered=True, text=False, arg_grid_spacing=grid_spacing,
                                           arg_swatch_width=swatch_width)

    def __parse_pixels(self):
        """Creates a dictionary of its colours, ordered by appearance, and their frequency for the image object"""
        # converts the image to rgb colour space
        self.__im.convert("RGB")

        # initialises a new dictionary
        colors = {}

        print("{} pixels".format(self.__im.width * self.__im.height))
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

        return reduced_colours

    def __create_grid(self, colors, grid=50, text=True, ordered=False, random=False, save=True, suggestions=False,
                      background=(0, 0, 0), arg_swatch_width=-1, arg_grid_spacing=-1, arg_max_grid_size=-1):
        """
        Creates a grid image from the supplied colors
        :param colors: a list of rgb color tuples in the format (r, g, b) 0-255
        :param grid: an integer for the number of rows/columns, max 100, default: 50
        :param text: a bool for whether to overlay the tuple as text on each color, default: True
        :param ordered: a bool whether to order the colors chromatically
        :param random: a bool whether to randomise the order of colors
        :param save: a bool whether to save the resulting graphic
        :param background: an rgb tuple for the grid background, default: black
        :param arg_swatch_width: a swatch width int can be passed to override the object swatch width
        :param arg_grid_spacing: a grid spacing int can be passed to override the object grid spacing
        :param arg_max_grid_size: a max grid size int can be passed to override the object max grid size
        :return: an Image object with the color grid drawn on it
        """
        # grid variables
        swatch_width = self.__grid_swatch_width
        grid_spacing = self.__grid_spacing

        if arg_swatch_width > 0:
            swatch_width = arg_swatch_width
        if arg_grid_spacing > 0:
            grid_spacing = arg_grid_spacing

        # turn off text if too narrow
        if swatch_width < 80:
            text = False

        # limit grid to __max_grid_size
        if arg_max_grid_size > 0:
            if grid > arg_max_grid_size:
                grid = arg_max_grid_size
        else:
            if grid > self.__grid_max_size:
                grid = self.__grid_max_size


        print('\nCreating Color Grid for {} | ordered: {} | random: {} | grid: {} | text: {} | '
              'background: {} | save: {}'.format(self.__im.filename.split('.')[0], ordered, random, grid, text,
                                                 background, save))

        # randomise colors
        if random:
            shuffle(colors)
            colors = colors[:grid * grid]
        else:
            colors = colors[:grid * grid]

        # order colors
        if ordered:
            colors = self.__sort_colors_by_hsl(colors)

        # Create image file
        length = (grid * swatch_width) + ((grid + 1) * grid_spacing)
        if length > self.__max_length:
            length = self.__max_length
        grid_graphic = Image.new("RGB", (length, length), color=background)
        draw = ImageDraw.Draw(grid_graphic)

        # variables for drawing
        x = 0
        y = grid_spacing
        count = 0

        # Draw grid
        for color in colors:
            x += grid_spacing
            draw.rectangle([(x, y), (x + swatch_width, y + swatch_width)],
                           fill='rgb' + str(color[:3]))
            if text:
                draw.text((x + 5, y + 5), str(color[:3]), fill=self.__choose_text_contrast_color(color[:3]))
            x += swatch_width
            count += 1

            # starts a new line if count reaches full width
            if count >= grid:
                count = 0
                x = 0
                y += (swatch_width + grid_spacing)

        # Save the image
        if suggestions:
            type_string = '_suggestions'
        else:
            type_string = ''

        if save:
            grid_graphic.save(
                '{}/{}{}_ordered{}_random{}_grid{}_text{}_background{}_color_grid.png'
                .format(self.__path, self.__im.filename.split('.')[0], type_string, ordered, random, grid, text,
                        background), 'PNG')
            print(
                'Color {} Grid saved to the Results directory: {}{}_ordered{}_random{}_grid{}_text{}'
                '_background{}_color_grid.png'.format(type_string, self.__im.filename.split('.')[0],
                                                      type_string, ordered, random, grid, text, background))

        print('Color {} Grid: Finished'.format(type_string))
        return grid_graphic

    def __check_if_greyscale(self):
        """
        Iterates through all the colors in the image color dictionary and returns True if they are all greyscale
        :return: True if the image is greyscale
        """
        for color in self.__colors:
            if color[0] != color[1] != color[2]:
                return False
        return True

    def __load_data(self, type_string, function, use_cache=True, **kwargs):
        """
        Loads data from cache files if present or creates files to improve efficiency
        :param type_string: a string for the sub-folder to be called
        :param function: a function to be called to generate the data to be dumped to the file
        :param use_cache: skips the caching process and calculates data from scratch regardless
        :param kwargs: takes arguments for functions requiring arguments
        :return: the data which has been retrieved or generated
        """
        # bypass cache
        if not use_cache:
            if type_string == 'im_suggestions':
                return function(colour_dict=kwargs['colour_dict'], number_requested=kwargs['number_requested'])
            else:
                return function()

        # Check temp folder exists
        if not os.path.exists('./imageinterpreter_cache'):
            os.mkdir('./imageinterpreter_cache')

        # Check sub-folder exists
        if not os.path.exists('./imageinterpreter_cache/{}'.format(type_string)):
            os.mkdir('./imageinterpreter_cache/{}'.format(type_string))

        # Check file exists
        if os.path.exists('./imageinterpreter_cache/{}/{}'.format(type_string, self.__im.filename.split('.')[0])):
            infile = bz2.BZ2File('./imageinterpreter_cache/{}/{}'.format(type_string, self.__im.filename.split('.')[0]),
                                 'r')
            data = pickle.load(infile)
            infile.close()

        # Create temp file
        else:
            outfile = bz2.BZ2File('./imageinterpreter_cache/{}/{}'.format(type_string,
                                                                          self.__im.filename.split('.')[0]), 'w')

            if type_string == 'im_suggestions':
                data = function(colour_dict=kwargs['colour_dict'], number_requested=kwargs['number_requested'])
            else:
                data = function()

            pickle.dump(data, outfile)
            outfile.close()

        return data

    def __get_max_grid_size(self, data, swatch_width, grid_spacing, output=True):
        """
        Calculates the maximum number of grid rows/columns
        :param data: a data structure with a length
        :param swatch_width: an integer width for each swatch
        :return: an integer max number of rows/columns
        """
        if output:
            print('\n')
        max_grid_size = math.floor(math.sqrt(len(data)))
        if max_grid_size * (swatch_width + grid_spacing) > self.__max_length:
            if output:
                print('The grid size was limited by a max width of: {}'.format(self.__max_length))
            max_grid_size = math.floor(self.__max_length / (swatch_width + grid_spacing))
        if output:
            print('The grid max size is: {}'.format(max_grid_size))

        return max_grid_size

    @staticmethod
    def __choose_text_contrast_color(color):
        """
        Uses color luminosity to decide if overlay text should be white or black
        :param color: A tuple in the format (r, g, b) with values 0-255
        :return: A tuple in the format (r, g, b) for either white or black
        """
        luminance = (0.2126 * color[0]) + (0.7152 * color[1]) + (0.0722 * color[2])
        if luminance > 150:
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

    @staticmethod
    def __sort_dictionary_colors_by_hsl(color_dictionary):
        """
        Orders a dictionary of rgb(tuple), frequency chromatically by HSL
        :param color_dictionary: a dictionary of key rgb tuple and any value
        :return: a sorted dictionary of rgb tuple and value from input dictionary
        """
        # convert 0-255 colours to 0-1 float
        color_float_list = list()
        for key, value in color_dictionary.items():
            new_colour = []
            for x in range(3):
                new_colour.append(key[x] / 255.0)
            color_float_list.append(new_colour)

        # sorts colors
        color_float_list.sort(key=lambda rgb: colorsys.rgb_to_hls(*rgb))

        # converts sorted floats to 0-255 integers
        sorted_color_key_dictionary = {}
        for elem in color_float_list:
            new_colour = []
            for colour_value in elem:
                new_colour.append(int(colour_value * 255))
            try:
                sorted_color_key_dictionary[tuple(new_colour)] = color_dictionary[tuple(new_colour)]
            except KeyError:
                # Allow RGBA tuple
                new_colour.append(255)
                sorted_color_key_dictionary[tuple(new_colour)] = color_dictionary[tuple(new_colour)]

        return sorted_color_key_dictionary.items()


if __name__ == '__main__':

    analysed_image = AnalyseImage('Foxy.jpg', grid_swatch_width=30, grid_spacing=5)

    analysed_image.create_basic_selection()

    analysed_image.create_color_grid(grid=1000, extra_large=True, arg_swatch_width=30, arg_grid_spacing=5, text=False,
                                     ordered=True)
    analysed_image.create_color_grid(grid=1000, extra_large=True, arg_swatch_width=30, arg_grid_spacing=5, text=False)

    analysed_image.create_color_suggestions_grid(grid=1000, extra_large=True, arg_swatch_width=30, arg_grid_spacing=5,
                                                 text=False)
    analysed_image.create_color_suggestions_grid(grid=1000, extra_large=True, arg_swatch_width=30, arg_grid_spacing=5,
                                                 text=False, ordered=True)
