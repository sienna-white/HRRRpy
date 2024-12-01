#!/bin/sh
#SBATCH --job-name=postprocess_gsi
#SBATCH --partition=savio3
#SBATCH --account=co_aiolos 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00


    # Path to the Python script for creating plots
    # PLOT_SCRIPT="/global/scratch/users/siennaw/scripts/HRRRpy/create_plots.py"
~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 101 & 
~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 102 & 
~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 103 & 
~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 104 & 
~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 105 & 
~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 106 &
~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 107 & 
~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 108 & 
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 108 & #create_DA_timeseries.py

wait 

#  ~/.conda/envs/smoke_env/bin/python -u create_DA_timeseries.py 
