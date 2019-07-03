SpinACP: Application Command Protocol for SpiNNaker
---------------------------------------------------

SpinACP is a library providing a framework for the definition and execution of commands in the Application Processors of the SpiNNaker platform. It can also be used to reconfigure memory data structures of an application running on the board.

Installation
--------------------------

1. Download SpinACP to your project folder. 
2. In the SpinACP folder, setup the Python libraries:

::

	% python setup.py

3. In the SpinACP folder, build and install the C libraries:

::

	% make install

Usage instructions
------------------

To use SpinACP in your SpiNNaker application, include the header files in your C file:

::

	#include "PATH_TO/acp.h"

In the host-side Python code, first import the MPI libraries:

:: 

	import spynnaker_acp

Authorship and copyright
------------------------

SpinACP is being developed by `Francesco Barchi <mailto:francesco.barchi@polito.it>`__.

+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+
|  **Please always cite the publication, also if using SpinACP in comparisons and pipelines**                                                                                                                                           |
+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+
| .. image:: https://user-images.githubusercontent.com/7613428/60581998-40d00b00-9d88-11e9-9a24-efd28e1bcaca.png   | *Flexible on-line reconfiguration of multi-core neuromorphic platforms*;                                           |
|    :alt: Please cite                                                                                             | Francesco Barchi, Gianvito Urgese, Alessandro Siino, Santa Di Cataldo, Enrico Macii, Andrea Acquaviva;             |
|    :target: https://ieeexplore.ieee.org/document/8676216                                                         | `IEEE Transactions on Emerging Topics in Computing <https://ieeexplore.ieee.org/document/8676216>`__;              |
|    :width: 76px                                                                                                  | doi: 10.1109/TETC.2019.2908079                                                                                     |
+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+
| **Please respect the license of the software**                                                                                                                                                                                        |
+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+
| .. image:: https://user-images.githubusercontent.com/7613428/60581999-4168a180-9d88-11e9-87e3-ce5e127b84a1.png   | SpinACP is free and open source software, so you can use it for any purpose, free of charge.                       |
|    :alt: Respect the license                                                                                     | However, certain conditions apply when you (re-)distribute and/or modify SpinACP; please respect the               |
|    :target: https://github.com/neuromorphic-polito/SpinACP/blob/master/LICENSE.rst                               | `license <https://github.com/neuromorphic-polito/SpinACP/blob/master/LICENSE.rst>`__.                              |
|    :width: 76px                                                                                                  |                                                                                                                    |
+------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------+

*icons on this page by Austin Andrews / https://github.com/Templarian/WindowsIcons*
