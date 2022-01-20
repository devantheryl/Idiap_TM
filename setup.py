# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 11:00:55 2022

@author: LDE
"""

from setuptools import setup, find_packages

setup(
      name = 'digital_twins_learner',
      version = '0.1.0',
      packages = find_packages(),
      description = 'Framework to train and exploit a digital twins to schedule batches on a production line',
      url = 'https://github.com/devantheryl/Idiap_TM',
      author = 'Lucas Devanthéry',
      author_email = 'devantheryl.pro@gmail.com',
      license = 'MIT',
      
      install_requires = [
          'pandas==1.1.3',
          'numpy==1.19.5',
          'tensorforce==0.6.5',
          'tensorflow==2.6.0',
          'keras==2.6.0',
          'tensorflow-gpu==2.6.0',#to check
          'matplotlib==3.3.4',
          'jupyter',
          'wandb',
          'coverage',
      ]   
)