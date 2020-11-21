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
```Python
analysed_image = AnalyseImage(filename: string)
```
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
.create_color_frequency_bars(width: int, random: bool, save: bool)
```
Parameter | Default | Description
--- | --- | ------
width | 2000 | the width in pixels of the produced graphic
random | False | randomizes the order of colors when prsented as bars instead of order of appearance
save | True | Decides whether to save the graphic

---
#### Color Grid
Creates a graphic grid of colored squares from the original image 
```Python
.create_color_grid(ordered: bool, random: bool, save: bool, grid: int, text: bool, background: tuple)
```
Parameter | Default | Description
--- | --- | ------
ordered | False | orders the colores chromatically by HSL - is prioiritised over randomization
random | False | randomizes the order of colors when prsented as bars instead of order of appearance
save | True | Decides whether to save the graphic
grid | 50 | the number of columns/rows in the grid upto 100
text | True | adds the rgb tuple value as a text overlay on each color
background | (0, 0, 0) | an rgb tuple of the background color for the grid - each value 0-255

---
#### Color Suggestions Grid
Creates a graphic grid of colored squares from the based on a suggestions algorithm using [Color Harmonies](https://github.com/baptistemanteau/colorharmonies)
```Python
.create_color_suggestions_grid(ordered: bool, random: bool, save: bool, grid: int, text: bool, background: tuple)
```
Parameter | Default | Description
--- | --- | ------
ordered | False | orders the colores chromatically by HSL - is prioiritised over randomization
random | False | randomizes the order of colors when prsented as bars instead of order of appearance
save | True | Decides whether to save the graphic
grid | 50 | the number of columns/rows in the grid upto 100
text | True | adds the rgb tuple value as a text overlay on each color
background | (0, 0, 0) | an rgb tuple of the background color for the grid - each value 0-255

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
![Abstract Image](https://github.com/George9Waller/ImageInterpreter/blob/master/Example_Images_Foxy/Foxy_suggestions_orderedFalse_randomTrue_grid50_textFalse_background(0%2C%200%2C%200)_color_suggestions_grid.png "Color Suggestions Grid - Ordered False")
  ---
  Color Suggestions Grid Ordered True: 
![Abstract Image](https://github.com/George9Waller/ImageInterpreter/blob/master/Example_Images_Foxy/Foxy_suggestions_orderedTrue_randomFalse_grid50_textTrue_background(0%2C%200%2C%200)_color_suggestions_grid.png "Color Suggestions Grid - Ordered True")
  ---
  Color Frequency Bars Random False: 
![Abstract Image](https://github.com/George9Waller/ImageInterpreter/blob/master/Example_Images_Foxy/Foxy_width2000_height60000_randomFalse_color_frequency_bars.png "Color Frequency Bars - Random False")
 
