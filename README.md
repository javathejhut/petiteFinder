<div align="center">

# PetiteFinder

<h4>
An automated tool to compute Petite colony frequencies in baker's yeast
</h4>

</div>

## Overview

Here goes the motiovation for the tool.

### Demo

![petiteFinder demo](demo/showcase.gif)


### Installation

The colony detection module of PetiteFinder was build on an open-source image detection toolbox [MMDetection](https://github.com/open-mmlab/mmdetection) and 
a CV library for large scale object detection via slicing called [SAHI](https://github.com/obss/sahi). The GUI module was designed with [tkinter](https://docs.python.org/3/library/tkinter.html) python library.

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

- Install `tkiner` for GUI interface (in case it's not installed on your system):

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



### Standard command line usage

To run the colony detection model on a folder with images use `predict` command:
- Provide a path to folder with images with a `-i` flag,
- Specify to what level of details you want the results with a `-p` flag. Choces are `complete`, `frequency_only`, `json_only`, `visualize_only`
- Provide a path to an output folder where to write down results (annotations, petite colonies frequency, annotated images, etc)

Example:
```
python petiteFinder.py predict -i ./demo/input_images/ -o ./demo/output/ -p complete 
```

### Interactive Visualization & Inspection 
To visualize the resulting annotations and interactively modify them use `amend` command:
- Provide a path to a resulting `.json` file with `-i` flag
Example:
```
python petiteFinder.py amend -i ./demo/output/pF_predicted.json
```
This will open a tkinter window:
<img src="/demo/GUI.png" width=500px>
![petiteFinder GUI](/demo/GUI.png) 



## <div align="center">Citation</div>

If you use this software in your research, please cite it as:

```
@software{petiteFinder,
  author       = {Nunn, Chris and Klyshko, Eugene},
  title        = {{PetiteFinder: An automated tool to compute Petite colony frequencies in baker's yeast}},
  url          = {https://github.com/javathejhut/petiteFinder}
}
```

## Contributors

 - <a align="left" href="https://github.com/javathejhut" target="_blank">Chris Nunn</a>
 - <a align="left" href="https://github.com/klyshko" target="_blank">Eugene Klyshko</a>




