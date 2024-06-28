from argparse import ArgumentParser
import os
import glob


def get_file_trios(indir):
    if 'CanESM5' in indir:
        search_string = os.path.join(indir, '*r1i1p2f1*.nc')
    else:
        search_string = os.path.join(indir, '*.nc')
    files = [os.path.basename(file) for file in glob.glob(search_string)]
    parts = {f.split('_', 1)[1] for f in files if 'ssp370' not in f}
    return [['pr_' + part, 'tasmin_' + part, 'tasmax_' + part] for part in parts]


def build_job_file(trio, indir, outdir, model, id):
    pr, tasmin, tasmax = trio
    part = pr.split('_', 1)[1]
    snow = 'snow_' + part
    rain = 'rain_' + part
    filepath = os.path.join(outdir, 'pr_gen_{}_{}.pbs'.format(model, id))
    with open(filepath, 'w+') as jobfile:
        jobfile.write('''#!/bin/bash
#PBS -l nodes=1:ppn=2
#PBS -l vmem=12000mb
#PBS -l walltime=48:00:00
#PBS -o /storage/home/eyvorchuk/nobackup/logs/pr_climo_mbcn
#PBS -e /storage/home/eyvorchuk/nobackup/errors/pr_climo_mbcn
#PBS -m ae
#PBS -N pr_climo_''' + str(model) + '_' + str(id) + '\n')

        jobfile.write('\n')
        jobfile.write('echo "$(date) Setting up virtual environment"')
        jobfile.write('''
ce_dp=/storage/home/eyvorchuk/code/climate-explorer-data-prep
cd $ce_dp
source venv/bin/activate
''')

        jobfile.write('\n')
        jobfile.write('echo "$(date) Loading modules"')
        jobfile.write('''
module load cdo-bin
module load netcdf-bin
module load nco-bin
''')

        jobfile.write('\n')
        jobfile.write('echo "$(date) Copying pr/tasmin/tasmax datafiles"\n')
        jobfile.write('cp {} $TMPDIR\n'.format(os.path.join(indir, pr)))
        jobfile.write('cp {} $TMPDIR\n'.format(os.path.join(indir, tasmin)))
        jobfile.write('cp {} $TMPDIR\n'.format(os.path.join(indir, tasmax)))

        jobfile.write('\n')
        jobfile.write('echo "$(date) Generating snow daily file"\n')
        jobfile.write('python scripts/generate_prsn -p $TMPDIR/{} -n $TMPDIR/{} -x $TMPDIR/{} -o $TMPDIR -f {}\n'.format(pr, tasmin, tasmax, snow))
        jobfile.write('ncrename -v prsn,pr $TMPDIR/{}\n'.format(snow)) 

        jobfile.write('\n')
        jobfile.write('echo "$(date) Generating rain daily file from difference between pr and snow"\n')
        jobfile.write('ncdiff $TMPDIR/{} $TMPDIR/{} $TMPDIR/{}\n'.format(pr, snow, rain))
        jobfile.write('ncrename -v pr,snow $TMPDIR/{}\n'.format(snow))
        jobfile.write('ncrename -v pr,rain $TMPDIR/{}\n'.format(rain))

        jobfile.write('\n')
        jobfile.write('echo "$(date) Generating pr climos"\n')
        jobfile.write('python scripts/generate_climos -c 7100 -c 8110 -c 9120 -c 2020 -c 2050 -c 2080 -o {}/Derived -p mean $TMPDIR/{}\n'.format(indir, pr))

        jobfile.write('\n')
        jobfile.write('echo "$(date) Generating snow climos"\n')
        jobfile.write('python scripts/generate_climos -c 7100 -c 8110 -c 9120 -c 2020 -c 2050 -c 2080 -o {}/Derived -p mean $TMPDIR/{}\n'.format(indir, snow))

        jobfile.write('\n')
        jobfile.write('echo "$(date) Generating rain climos"\n')
        jobfile.write('python scripts/generate_climos -c 7100 -c 8110 -c 9120 -c 2020 -c 2050 -c 2080 -o {}/Derived -p mean $TMPDIR/{}\n'.format(indir, rain))

        jobfile.write('\n')
        jobfile.write('echo "$(date) Discarding used files"\n')
        jobfile.write('rm $TMPDIR/{}\n'.format(pr))
        jobfile.write('rm $TMPDIR/{}\n'.format(tasmin))
        jobfile.write('rm $TMPDIR/{}\n'.format(tasmax))
        jobfile.write('rm $TMPDIR/{}\n'.format(snow))
        jobfile.write('rm $TMPDIR/{}\n'.format(rain))

def main(args):
    file_trios = get_file_trios(args.indir)
    id = 0
    for trio in file_trios:
        build_job_file(trio, args.indir, args.outdir, args.model, id)
        id += 1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('indir', metavar='indir', help='Directory containing input data files')
    parser.add_argument('outdir', metavar='outdir', help='Directory containing output data files')
    parser.add_argument('model', metavar='model', help='Climate model on which to compute climatologies')
    args = parser.parse_args()
    main(args)
