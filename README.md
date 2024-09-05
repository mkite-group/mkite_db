<div align="center">
  <img src="https://raw.githubusercontent.com/mkite-group/mkite_db/main/docs/_static/mkite-logo.svg" width="500"><br>
</div>

# What is mkite?

mkite is a suite of tools for running high-throughput materials simulations in distributed computing platforms.
The mkite suite decouples the production database from client workers, facilitating scaling of simulations across heterogeneous computing environments.
The infrastructure enables exploration of combinatorial materials spaces using workflows, recipes, data visualizations, and more.

Some advantages of mkite:

- It stores and organizes complex materials workflows on databases. For example, mkite allows creating workflows with more than one parent input branch (say, interfaces between solids and molecules).
- The server is agnostic to the computing environments where the tasks are performed, and the clients are unaware of the production database. This facilitates distributing the tasks across heterogeneous computing systems.
- It provides textual descriptions for workflows, and enables adapting them on-the-fly. This helps as a "lab notebook" for computational materials scientists.
- It is adaptable to many software packages and inputs. The recipe system also interacts well with other libraries, such as ASE, pymatgen, cclib, and more.

## Documentation

General tutorial for `mkite` and its plugins are available in the [main documentation](https://mkite.org).
Complete API documentation is pending.

## Installation

To install `mkite_db`, first install `mkite_core` and `mkite_engines`.
Then, install this repository with pip:

```bash
pip install mkite_core mkite_engines
pip install mkite_db
```

Alternatively, for a development version, clone this repo and install it in editable form:

```bash
pip install -U git+https://github.com/mkite-group/mkite_db
```

## Contributions

Contributions to the entire mkite suite are welcomed.
You can send a pull request or open an issue for this plugin or either of the packages in mkite.
When doing so, please adhere to the [Code of Conduct](CODE_OF_CONDUCT.md) in the mkite suite.

The mkite package was created by Daniel Schwalbe-Koda <dskoda@ucla.edu>.

### Citing mkite

If you use mkite in a publication, please cite the following paper:

```bibtex
@article{mkite2023,
    title = {mkite: A distributed computing platform for high-throughput materials simulations},
    author = {Schwalbe-Koda, Daniel},
    year = {2023},
    journal = {arXiv:2301.08841},
    doi = {10.48550/arXiv.2301.08841},
    url = {https://doi.org/10.48550/arXiv.2301.08841},
    arxiv={2301.08841},
}
```

## License

The mkite suite is distributed under the following license: Apache 2.0 WITH LLVM exception.

All new contributions must be made under this license.

SPDX: Apache-2.0, LLVM-exception

LLNL-CODE-848161
