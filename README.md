<div align="center">
<h1>
  PetiteFinder
</h1>

<h4>
  An automated tool to compute Petite colony frequencies in baker's yeast
</h4>

</div>

## <div align="center">Overview</div>

Here goes the motiovation for the tool.

### Demo

![petiteFinder demo](demo/showcase.gif)


### Installation

The colony detection module of PetiteFinder was build on an open-source image detection toolbox [MMDetection](https://github.com/open-mmlab/mmdetection) and 
a CV library for large scale object detection via slicing called [SAHI](https://github.com/obss/sahi). The GUI module was designed with [tkinter](https://docs.python.org/3/library/tkinter.html) python library.

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
conda install pytorch=1.10.0 torchvision=0.11.1 (cudatoolkit=11.3) -c pytorch
```

- It is recommended to install `MMDetection` using [MIM](https://github.com/open-mmlab/mim), which automatically handles the dependencies of `OpenMMLab` projects, including `mmcv` and other python packages:

```console
pip install openmim
mim install mmdet
```

- Install `tkiner` for GUI interface:

```console
conda install -c anaconda tk
```

- Install additional libraries such as `pandas`:

```console
conda install pandas pillow
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

- Install `tkiner` for GUI interface:

```console
conda install -c anaconda tk
```

- Install additional libraries such as `pandas`:

```console
conda install pandas pillow
```
</details>



### Standard command line usage

<img width="700" alt="sahi-predict" src="">


### Interactive Visualization & Inspection 

<img width="700" alt="sahi-fiftyone" src="">

Find detailed info at [Interactive Result Visualization and Inspection](https://github.com/obss/sahi/issues/357).


## <div align="center">Citation</div>

If you use this package in your work, please cite it as:

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




