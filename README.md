# ImageInterpreter

A package for interpreting image files and producing graphical results based on the content.

Made using:
* [Pillow](https://pillow.readthedocs.io/en/stable/)
* [Color Harmonies](https://github.com/baptistemanteau/colorharmonies)

## Docs

#### Example use case to create one of each graphic
```Python
analysed_image = AnalyseImage('Foxy.jpg')

analysed_image.create_color_frequency_bars()

analysed_image.create_color_grid()

analysed_image.create_color_suggestions_grid()

```
---
### AnalyseImage Object:
This is the object used to control and manage the creation of graphics

#### Instantiation
A new object must have a filepath which is the exact name (including extension) of an image file as supported by [Pillow](https://pillow.readthedocs.io/en/stable/)
<br>
The file must be stored in a folder named ```source``` in the root directory of the program.
```Python
analysed_image = AnalyseImage(filename: string, use_cache: bool, grid_swatch_width: int, grid_spacing: int, target_height: int)
```
Parameter | Default | Description
--- | --- | ------
filename | | The string filename including extension for an image in the program root directory
use_cache | True | Tells the program whether to check, read or create cache files or calculate the data each time. Can be used if creating an image with the same name as a previous one which would cause the cache to read incorrect data.
grid_swatch_width | 200 | The default grid swatch width used when creating a grid graphic and calculating the resolution of data to calculate. Should use the smallest values you expect to use so that a larger amount of data is cached.
grid_spacing | 10 | The default grid spacing used when creating a grid graphic and calculating the resolution of data to calculate. Should use the smallest values you expect to use so that a larger amount of data is cached.
target_height | 60000 | The height of the frequency bars graphics when created, maximum is 60000. Use the largest number you expect to use to generate the highest resolution of data is cached for all graphic types.

#### Attributes:
Name | Description
--- | ------
.color_frequency_bars | The most recent Color Frequency Bar Image made with the object
.color_grid | The most recent Color Grid Image made with the object
.color_suggestions_grid | The most recent Color Suggestions Grid Image made with the object
---
### Methods

#### Color Frequency Bar
Creates a graphic 60,000 pixels tall with proportionally sized to the frequency of that color in the original image
```Python
.create_color_frequency_bars(width: int, random: bool, ordered: bool, save: bool)
```
Parameter | Default | Description
--- | --- | ------
width | 2000 | the width in pixels of the produced graphic
random | False | randomizes the order of colors when presented as bars instead of order of appearance
ordered | False | orders the colors chromatically, this overrides the random parameter
save | True | Decides whether to save the graphic

Returns: the colour data dictionary {(r, g, b): frequency} or {(r, g, b, a), frequency} used to create the graphic

---
#### Color Grid
Creates a graphic grid of colored squares from the original image 
```Python
.create_color_grid(ordered: bool, random: bool, save: bool, grid: int, text: bool, background: rgb_tuple, extra_large: bool, arg_swatch_width: int, arg_grid_spacing: int)
```
Parameter | Default | Description
--- | --- | ------
ordered | False | orders the colores chromatically by HSL - is prioiritised over randomization
random | False | randomizes the order of colors when prsented as bars instead of order of appearance
save | True | Decides whether to save the graphic
grid | 50 | the number of columns/rows in the grid upto 100
text | True | adds the rgb tuple value as a text overlay on each color
background | (0, 0, 0) | an rgb tuple of the background color for the grid - each value 0-255
extra_large | False | overrides the reduced data set to create larger grids typically 300+ rows/columns. This is dependant on either the image default swatch width/grid spacing or the values passed to this function.
arg_swatch_width | -1 | if a positive value (1 or more) is passed this swatch width overrides the image default swatch width
arg_grid_spacing | -1 | if a positive value (0 or more) is passed this grid spacing overrides the image default grid spacing

Returns: the list of color tuples (r, g, b) or (r, g, b, a) used to create the graphic

---
#### Color Suggestions Grid
Creates a graphic grid of colored squares from the based on a suggestions algorithm using [Color Harmonies](https://github.com/baptistemanteau/colorharmonies)
```Python
.create_color_suggestions_grid(ordered: bool, random: bool, save: bool, grid: int, text: bool, background: tuple, extra_large: bool, arg_swatch_width: int, arg_grid_spacing: int)
```
Parameter | Default | Description
--- | --- | ------
ordered | False | orders the colores chromatically by HSL - is prioiritised over randomization
random | False | randomizes the order of colors when prsented as bars instead of order of appearance
save | True | Decides whether to save the graphic
grid | 50 | the number of columns/rows in the grid upto 100
text | True | adds the rgb tuple value as a text overlay on each color
background | (0, 0, 0) | an rgb tuple of the background color for the grid - each value 0-255
extra_large | False | overrides the reduced data set to create larger grids typically 300+ rows/columns. This is dependant on either the image default swatch width/grid spacing or the values passed to this function.
arg_swatch_width | -1 | if a positive value (1 or more) is passed this swatch width overrides the image default swatch width
arg_grid_spacing | -1 | if a positive value (0 or more) is passed this grid spacing overrides the image default grid spacing

Returns: the list of color suggestions tuples (r, g, b) used to create the graphic

---
#### Create Basic Selection
Creates a basic selection of graphics for the AnalyseImage object
```Python
.create_basic_selection(grid_spacing: int, swatch_width: int)
```
Parameter | Default | Description
--- | --- | ------
grid_spacing | 200 | sets a grid spacing to override the object default when making the selection
swatch_width | 10 | sets a swatch width to override the object default when making the selection

Created Images:

Type | Ordered | Random | Text
---- | --- | --- | --- 
Frequency Bars | False | False |
Frequency Bars | False | True |
Frequency Bars | True | False |
Color Grid | False | True | True
Color Grid | False | True | False
Color Grid | True | False | True
Color Grid | True | False | False
Suggestions Grid | False | True | True
Suggestions Grid | False | True | False
Suggestions Grid | True | False | True
Suggestions Grid | True | False | False

Return: None

---
### Example Images
```Python
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
 ```
 [Files](https://github.com/George9Waller/ImageInterpreter/tree/master/Example_Images_Foxy)
 ---
 Color Grid Ordered True: 
![Abstract Image](https://github.com/George9Waller/ImageInterpreter/blob/master/Example_Images_Foxy/Foxy_orderedTrue_randomFalse_grid50_textTrue_background(0%2C%200%2C%200)_color_grid.png "Color Grid - Ordered True")
  ---
  Color Grid Ordered False: 
![Abstract Image](https://github.com/George9Waller/ImageInterpreter/blob/master/Example_Images_Foxy/Foxy_orderedFalse_randomTrue_grid50_textFalse_background(0%2C%200%2C%200)_color_grid.png "Color Grid - Ordered False")
  ---
  Color Suggestions Grid Ordered False: 
![Abstract Image](https://github.com/George9Waller/ImageInterpreter/blob/master/Example_Images_Foxy/Foxy_suggestions_orderedFalse_randomTrue_grid50_textFalse_background(0%2C%200%2C%200)_color_grid.png "Color Suggestions Grid - Ordered False")
  ---
  Color Suggestions Grid Ordered True: 
![Abstract Image](https://github.com/George9Waller/ImageInterpreter/blob/master/Example_Images_Foxy/Foxy_suggestions_orderedTrue_randomFalse_grid50_textFalse_background(0%2C%200%2C%200)_color_grid.png "Color Suggestions Grid - Ordered True")
  ---
  Color Frequency Bars Random False: 
![Abstract Image](https://github.com/George9Waller/ImageInterpreter/blob/master/Example_Images_Foxy/Foxy_width2000_height60000_randomFalse_orderedFalse_color_frequency_bars.png "Color Frequency Bars - Random False")
 
