There are three principal scripts to orchestrate the linking task and one python program that performs comparisons.

The three scripts in order of invocation:

1. `setup.sh` creates a working directory and copies files needed for the linking task into it.
2. `create_jobs` splits data files and creates jobs to process the split data.
3. `qmanager` submits jobs to the HPC job queue.

Finally, `link.py` runs the comparisons between records and writes out the results.  You will not need to invoke `link.py` directly. 

There is a [screencast](https://youtu.be/IPmu4bmOdys) that shows the use of each of these scripts/programs.

Open a pull request to contribute changes.  You can also create an issue if you have suggestions, comments, or questions.
