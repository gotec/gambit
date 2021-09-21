# gambit

`gambit` is an Open Source name disambiguation tool for version control systems.

## Download and installation

`gambit` is pure `python` code. It has no platform-specific dependencies and thus works on all
platforms. Assuming you are using `pip`, you can install latest version of `gambit` by running:

```
> pip install gambit-disambig
```

This also installs the necessary dependencies. `gambit` depends on the `python-Levenshtein` package to compute Levenshtein distances for edited lines of code. On sytems running Windows, automatically compiling this C based module might fail during installation. In this case, unofficial Windows binaries can be found [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein), which might help you get started.

## How to use gambit
After installation, we suggest to check out our [tutorial](https://github.com/gotec/gambit/blob/master/TUTORIAL.ipynb), detailing how to get started using `gambit`. We also provide detailed inline documentation serving as reference.

We have published some motivating results as well as details on the disambiguation algorithm and its hyperparameters in ["gambit – An Open Source Name Disambiguation Tool for Version Control Systems"](https://arxiv.org/abs/2103.05666). An earlier version of gambit used to obtain the results shown in our paper is archived on [zenodo.org](http://doi.org/10.5281/zenodo.4384646).
Due to GDPR, we cannot publish the manually disambiguated ground-truth data on zenodo. However, if you require this data for research purposes or replication of our results please feel free to contact us directly.

All functions of `gambit` have been tested on Ubuntu, Mac OS, and Windows.

## How to cite gambit

```
@INPROCEEDINGS{gote2021gambit,
  author={Gote, Christoph and Zingg, Christian},
  booktitle={2021 IEEE/ACM 18th International Conference on Mining Software Repositories (MSR)}, 
  title={gambit – An Open Source Name Disambiguation Tool for Version Control Systems}, 
  year={2021},
  volume={},
  number={},
  pages={80-84},
  doi={10.1109/MSR52588.2021.00021}
}
```

## License

This software is licensed under the GNU Affero General Public License v3 (AGPL-3.0).
