# benchmarktu1402

A structural dynamics benchmark problem which is generated as part of COST Action TU1402 on 
Quantifying the Value of Information and is intended to serve as a reference case 
study for validation of Structural Health Monitoring (SHM) methods and decision-making tools 
relying on the Value of Information.

## Getting started

- Pull down a copy of the code by cloning or downloading the repository
- Open a terminal and change the current directory to the benchmark folder
- Run the benchmark backend through the terminal by typing
```
python main.py
```
- Run the benchmark user interface (UI) through the terminal by typing
```
python benchmarktu1402.py
```

## Documentation

A description of the problem set-up, the modelling assumptions and the workflow to be followed in the Graphical User Interface (GUI) is available in the corresponding [IOMAC paper](https://github.com/ETH-WindMil/benchmarktu1402/blob/master/IOMAC_2019.pdf) which serves as documentation.


## Results

Upon running the analysis, a file named "Output_nodes.dat" is firstly generated, containing the information
of output nodes and consisting of three columns:
- Column 1 stores the labels of output nodes
- Columns 2-3 store the corresponding nodal coordinates

Depending on the type of analysis, the following files are further generated for each job named *Job_name*:

**Modal Analysis**

<div style="margin-left:55px">
<table>
  <thead>
      <tr>
        <th align="left", width="240">File name</th>
        <th align="left", width="500">Description</th>
      </tr>
  </thead>
  <body>
      <tr>
          <td> <i>Job_name</i>_frequencies.dat </td>
          <td> Contains the system natural frequencies </td>
      </tr>
      <tr>
          <td> <i>Job_name</i>_modes.dat </td>
          <td> Contains the corresponding mode shapes at output locations </td>
      </tr>
  </tbody>
</table>
</div>

**Dynamic Analysis**

<table>
  <thead>
      <tr>
        <th align="left", width="200">File name</th>
        <th align="left", width="500">Description</th>
      </tr>
  </thead>
  <body>
      <tr>
          <td> <i>Job_name</i>_displacements.dat </td>
          <td> Contains the displacement time history at output locations </td>
      </tr>
      <tr>
          <td> <i>Job_name</i>_accelerations.dat </td>
          <td> Contains the acceleration time history at output locations </td>
      </tr>
      <tr>
          <td> <i>Job_name</i>_strains.dat </td>
          <td> Contains the strain time history at output locations </td>
      </tr>
  </tbody>
</table>

## How to Cite

Tatsis, K. and Chatzi, E. (2019) "A numerical benchmark for system identification under operational and environmental variability", Proceedings of the 7th International Operational Modal Analysis Conference (IOMAC).

## Found a Bug?

If you think you've found a bug, go ahead and create a new [GitHub issue](https://help.github.com/en/articles/creating-an-issue). Be sure to include as much information as possible so that we can reproduce the bug.

## Notes

- The model parameters and output requests can be reconfigured and through main.py
- All python dependencies are included in [Anaconda](https://www.anaconda.com/distribution/) installations
