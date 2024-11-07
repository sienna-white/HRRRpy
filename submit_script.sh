#!/bin/sh
#SBATCH --job-name=gsi
#SBATCH --partition=savio2 
#SBATCH --account=co_aiolos 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=3
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00


    # Path to the Python script for creating plots
    # PLOT_SCRIPT="/global/scratch/users/siennaw/scripts/HRRRpy/create_plots.py"
~/.conda/envs/smoke_env/bin/python -u create_DA_timeseries.py

  