# 4DHumans: Reconstructing and Tracking Humans with Transformers
Code repository for the paper:
**Humans in 4D: Reconstructing and Tracking Humans with Transformers**
[Shubham Goel](https://people.eecs.berkeley.edu/~shubham-goel/), [Georgios Pavlakos](https://geopavlakos.github.io/), [Jathushan Rajasegaran](http://people.eecs.berkeley.edu/~jathushan/), [Angjoo Kanazawa](https://people.eecs.berkeley.edu/~kanazawa/)<sup>\*</sup>, [Jitendra Malik](http://people.eecs.berkeley.edu/~malik/)<sup>\*</sup>

[![arXiv](https://img.shields.io/badge/arXiv-2305.20091-00ff00.svg)](https://arxiv.org/pdf/2305.20091.pdf)  [![Website shields.io](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](https://shubham-goel.github.io/4dhumans/)     [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Ex4gE5v1bPR3evfhtG7sDHxQGsWwNwby?usp=sharing)  [![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/brjathu/HMR2.0)


![teaser](assets/teaser.png)

 This codebase must be run in Google Colab. Login to google colab, create a new notebook and first store the codebase to the google drive. 

To effectively run the codebase depends on how the system is set up, such as the Python version (Use Python version 3.11.12) It is tightly coupled with specific system properties and configurations. Some dependencies used in this project may not work the same way on every system. This can cause issues when trying to install or run different parts of the codebase, if the dependancies are not installed or incompatible with the system. If the website is successfully run, make sure you select "Runtime" in the taskbar, click "Change runtime type" and select "T4 GPU". 



## Run tracking demo on videos
The pre-trained model tracker builds on PHALP, please install that first:
```bash
pip install git+https://github.com/brjathu/PHALP.git
```

Install the latest versions of torch. 
```bash
pip install torch
pip install -e .[all]
```


## Installation and Setup
First, make sure to save the entire codebase file in Google Drive, and import the google drive to Google Colab to run the website. In the terminal, navigate to the website directory, using the 2 commands listed below, and first install the requirements by typing the command pip install -r requirements.txt in the terminal and  run python backend.py to start the flask web server: 
```bash

cd /drive/MyDrive/4D-Humans/website
pip install -r requirements.txt
python backend.py

```
Before running the website using ngrok, create an account with ngrok using the link https://ngrok.com/ . After logging in to the site, go to the "Your Authentication" section and generate an authentication token. Paste the authentication token in this code snippet below  inside a code cell in the Colab notebook that was created. 

from pyngrok import ngrok

Replace "YOUR_AUTHTOKEN" with the one you copied from ngrok's website
!ngrok config add-authtoken YOUR_AUTHTOKEN


All checkpoints and data will automatically be downloaded to `$HOME/.cache/4DHumans` the first time you run the demo code.

Besides these files, you also need to download the *SMPL* model. You will need the [neutral model](http://smplify.is.tue.mpg.de) for training and running the codebase. Please go to the corresponding website and register to get access to the downloads section. Download the model and place `basicModel_neutral_lbs_10_207_0_v1.0.0.pkl` in `./data/` and in the website directory



"# universitygaitrecognitionproject" 
