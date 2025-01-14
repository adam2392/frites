Start analyzing your data with Frites
-------------------------------------

In this section we are going to cover the basics knowledges if you want to start analyzing your data with Frites.

.. note::

    The gallery of examples contains a `tutorial <https://brainets.github.io/frites/auto_examples/index.html#tutorials>`_ section that explain and illustrate the main usages and features of Frites, in a notebook fashion.

Package organization
++++++++++++++++++++

As other Python packages, Frites contains subject-specific submodules. Here's a short description of the main submodules for new users :

* `frites.dataset <https://brainets.github.io/frites/api.html#module-frites.dataset>`_ : container for the electrophysiological data coming from multiple subjects (see also `those examples <https://brainets.github.io/frites/auto_examples/index.html#multi-subjects-dataset>`_ that explain how to define a container depending on your data type)
* `frites.workflow <https://brainets.github.io/frites/api.html#module-frites.workflow>`_ : the workflows perform a series of analyzes (usually a first analysis to extract information using IT measures follow by a second statistical analysis)
* `frites.conn <https://brainets.github.io/frites/api.html#module-frites.conn>`_ : directed and undirected connectivity metrics that can either be computed across trials or at the single trial level

In addition to the main modules above, the  `gallery of examples <https://brainets.github.io/frites/auto_examples/index.html>`_ illustrate the main functionalities of Frites using simulated data. Those functions can be imported from `frites.simulations <https://brainets.github.io/frites/api.html#module-frites.simulations>`_ and can be used to simulate local neural activity modulated by the task such as stimulus-specific brain networks using `autoregressive models <https://brainets.github.io/frites/api.html#autoregressive-model>`_.

Finally, for the developers here the `frites.core <https://brainets.github.io/frites/api.html#module-frites.core>`_ module include the very low level functions to estimate the mutual information (vector and tensor based implementations).


Main Frites' workflows
++++++++++++++++++++++

Frites contains two centrals workflows :

1. `WfMi <https://brainets.github.io/frites/api/generated/frites.workflow.WfMi.html#frites.workflow.WfMi>`_ : the main workflow of mutual-information that is used to **extract feature-specific brain networks**
2. `WfStats <https://brainets.github.io/frites/api/generated/frites.workflow.WfStats.html#frites.workflow.WfStats>`_ : the workflow of statistics we used to perform group-level inferences

Actually, under the hood, the **WfMi** is also using the workflow of statistics so that it return the estimation of mutual-information between a feature and the data but also the corresponding p-values.

.. warning::

    This workflow of mutual-information can be used for many things, including :

        * Provide a meaningful measure of effect-size between the data and a feature
        * To find some significant differences between multiple experimental conditions (``mi_type='cd``)
        * To correlate the brain data with a behavioral model (``mi_type='cc``) and possibly, independently of some experimental conditions (``mi_type='ccd``)
        * Get the corrected p-values to see whether you have a significant amount of information between your data and a feature, either at the group-level or at the subject level
        * Working on sparse data like the sEEG / iEEG where the number of subjects per brain region varies

    In a nutshell, the **WfMi** is the core workflow to find task-related activity. In addition, this workflow can either be used to quantify the amount of information between local neural activity and a feature **(i.e for each brain region)** but also on **connectivity links (i.e on pairs of brain regions)** to see whether there's some differences in term of connectivity between experimental conditions or ultimately, if the connectivity correlates with a behavioral model.

    To see this workflow in action, checkout `those examples <https://brainets.github.io/frites/auto_examples/index.html#mutual-information>`_


Deep integration with Xarray
++++++++++++++++++++++++++++

`Xarray <http://xarray.pydata.org/en/stable/>`_ is a recent python package to handle of multi-dimensional arrays using labels. For those who are familiar with `Pandas <https://pandas.pydata.org/>`_, you can see Xarray as a generalization of Pandas for multi-dimensional arrays.

Xarray provide a container for the data called `DataArray <http://xarray.pydata.org/en/stable/generated/xarray.DataArray.html#xarray.DataArray>`_. This structure comes with two important inputs : 1) `dims` which describe the name of each dimension of the array and 2) `coords` the values taken by each dimension. For example you can define a DataArray with the dimensions ``('roi', 'times')`` where ``roi = ['insula', 'vmPFC', 'dlPFC']`` and ``times = np.linspace(-3, 3, 1000)``. After that, the manipulation of the data happen using the values of the coordinates. Bellow, a minimal slicing example :

.. code-block:: python

    """
    `da` is a xarray.DataArray. With the code line below, we select the data
    coming from the two brain regions Insula and vmPFC. Then we also select
    every time points comprised between [-1.5, 1.5] seconds
    """
    da.sel(roi=['insula', 'vmPFC'], times=slice(-1.5, 1.5))


The example above only show how to slice the data but actually Xarray contains most of the operations using the same label-based syntax.

.. note::

    Frites make an extensive use of Xarray as most of the outputs returned are DataArrays. Since it's a relatively recent package, we wrote `two mini tutorials <https://brainets.github.io/frites/auto_examples/index.html#xarray>`_ to start working with it.
