<div align="center">

# PetiteFinder

<h4>
An automated tool to compute Petite colony frequencies in baker's yeast
</h4>

</div>

## Motivation

Here goes the motivation for the tool.
Details: 

## Demo

<img align="center" src="/demo/showcase.gif" width=1000px alt="petiteFinder Demo">

<details closed>
<summary>
<big><b>Under the hood:</b></big>
</summary>
  
- The trained and optimized Faster-RCNN detector (predicts bounding box + class + score), coupled with a feature pyramid network (FPN) based on the ResNet50 backbone.
  
- Sliced inference, i.e. detecting objects on the smaller slices of the original image and then merging them together with greedy non-maximal merging (NMM) algorithm.
  
- A simple crossplatform GUI tool to vizualize and modify annotatations in COCO format.
  
  <img align="center" src="/demo/scheme.png" width=700px>

</details>


## Installation

The colony detection module of PetiteFinder was build on an open-source image detection toolbox [MMDetection](https://github.com/open-mmlab/mmdetection) and 
a CV library for large scale object detection via slicing called [SAHI](https://github.com/obss/sahi). The GUI module was designed with the [tkinter](https://docs.python.org/3/library/tkinter.html) python library.

- Clone the repo:
```console
git-lfs clone https://github.com/javathejhut/petiteFinder
cd petiteFinder
```

<details closed>
<summary>
<big><b>Details for systems with CUDA devices:</b></big>
</summary>


- Create and activate a new `conda` environment:
```console
conda create --name petiteEnv python=3.7
conda activate petiteEnv
```

- Install `SAHI` using pip:
```console
pip install sahi==0.8.19
```

- Install pytorch, torchvision and CUDA Toolkit (recommended versions):
```console
conda install pytorch=1.10.0 torchvision=0.11.1 cudatoolkit=11.3 -c pytorch
```

- It is recommended to install `MMDetection` using [MIM](https://github.com/open-mmlab/mim), which automatically handles the dependencies of `OpenMMLab` projects, including `mmcv` and other python packages:

```console
pip install openmim
mim install mmdet
```

- Install `tkiner` for GUI interface (in case it is not installed on your system):

```console
conda install -c anaconda tk
```
</details>


<details closed>
<summary>
<big><b>Details for systems with CPU only:</b></big>
</summary>

- Create and activate a new `conda` environment:

```console
conda create --name petiteEnv python=3.7
conda activate petiteEnv
```

- Install `SAHI` using pip:
```console
pip install sahi==0.8.19
```

- Install CPU version of `pytorch`, `torchvision` and `cpuonly` (recommended versions):

```console
conda install pytorch cpuonly torchvision -c pytorch
```

- It is recommended to install `MMDetection` using [MIM](https://github.com/open-mmlab/mim), which automatically handles the dependencies of `OpenMMLab` projects, including `mmcv` and other python packages:

```console
pip install openmim
mim install mmdet
```

- Install `tkinter` for GUI interface (in case it's not installed on your system):

```console
conda install -c anaconda tk
```

</details>


## 1. Standard Command Line Usage

To run the colony detection model on a folder with images use the `predict` command:
- Provide a path to folder with images with a `-i` flag.
- Provide an output directory with a `-o` flag. This is the directory where all results are saved (annotations, petite colonies frequency CSV, annotated images).
- Specify a compute device with a `-d` flag. Choices are `cpu` and `gpu`.
- Specify to what level of details you want the results with a `-p` flag. Choices are `complete`, `frequency_only`, `json_only`, `visualize_only`. 
- For more details, access help by running `python petiteFinder.py predict -h`.

Example:
```
python petiteFinder.py predict -d gpu -i ./demo/input_images/ -o ./demo/output/ -p complete 
```

## 2. Interactive Visualization & Inspection

To visualize the resulting annotations and interactively modify them use the `amend` command:

- Provide a path to a resulting annotation `.json` file with `-i` flag. The annotation file contains the path to each image that will be opened.
- For more details, access help by running `python petiteFinder.py amend -h`.

Example:
```
python petiteFinder.py amend -i ./demo/output/pF_predicted.json
```
This will open a tkinter window:

<img align="center" src="/demo/GUI.png" width=500px>

- Navigate an image folder with `<` and `>` buttons and chose an image to visualize. Zoom in and out relative to the cursor with a mouse wheel or by pressing `<i>` and `<o>` keys. There are two GUI modes that can be chosen with the corresponding buttons: `Draw Mode` and `Remove Mode`, or by pressing `<d>` or `<r>` keys, respectively. 

- Hover over the bounding box to see the additional information in the upper right corner, such as category (`p` - Petite, `g` - Grande) and `Score` (the confidence provided by the model in the range from 0 to 1).

- In the `Draw mode`, chose a category of the colony you want to annotate with a bounding box (in case it was not detected by the model) by `Petite` and `Grande` buttons, or alternatively, by pressing `<p>` or `<g>` keys. Draw a bounding box around the object by moving a mouse after pressing and holding the left mouse button.

- In the `Remove mode`, click on the bounding boxes you want to remove (they will light up red) and then press `Delete selected` button or `<BackSpace>`/`<Delete>`keys to clear them of the image. 

- Press `Save` button to save amended annotations to the `amended_*.json` file. 


## Citation

If you use this software in your research, please cite it as:

```
@software{petiteFinder,
  author       = {Nunn, Christopher J. and Klyshko, Eugene},
  title        = {{PetiteFinder: An automated tool to compute Petite colony frequencies in baker's yeast}},
  url          = {https://github.com/javathejhut/petiteFinder}
}
```

## Contributors

 - <a align="left" href="https://github.com/javathejhut">Chris Nunn</a>
 - <a align="left" href="https://github.com/klyshko">Eugene Klyshko</a>


