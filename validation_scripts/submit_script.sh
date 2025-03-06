#!/bin/sh
#SBATCH --job-name=postprocess_gsi
#SBATCH --partition=savio3_htc 
#SBATCH --account=co_aiolos 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00


    # Path to the Python script for creating plots
    # PLOT_SCRIPT="/global/scratch/users/siennaw/scripts/HRRRpy/create_plots.py"
~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 2019_1  
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 102 & 
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 103 & 
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 401 &
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 402 &
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 403 &
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 404 &
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 405 &
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 406
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 407 &
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 408 & 
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 409 & 
# ~/.conda/envs/smoke_env/bin/python -u create_csv_PA.py 410 &

# module purge 
# module load anaconda3/2024.02-1-11.4
# conda run -n smoke_env python temp.py

# conda run -n geo_env python temp.py

# ~/.conda/envs/smoke_env/bin/python temp.py 

wait 

#  ~/.conda/envs/smoke_env/bin/python -u create_DA_timeseries.py 
