from argparse import ArgumentParser
import os
import glob


def get_file_trios(indir):
    search_string = os.path.join(indir, '*.nc')
    files = [os.path.basename(file) for file in glob.glob(search_string)]
    parts = {f.split('_', 1)[1] for f in files}
    return [['pr_' + part, 'tasmin_' + part, 'tasmax_' + part] for part in parts]


def build_job_file(trio, indir, outdir, id):
    pr, tasmin, tasmax = trio
    prsn = 'prsn_output.nc'
    filepath = os.path.join(outdir, 'prsn_gen_{}.pbs'.format(id))
    with open(filepath, 'w+') as jobfile:
        jobfile.write('''#!/bin/bash
#PBS -l nodes=1:ppn=4
#PBS -l vmem=12000mb
#PBS -l walltime=24:00:00
#PBS -o /path/to/logs
#PBS -e /path/to/errors
#PBS -m abe
#PBS -N prsn_climo
''')

        jobfile.write('\n')
        jobfile.write('echo "$(date) Setting up virtual environment"')
        jobfile.write('''
ce_dp=/path/to/climate-explorer-data-prep/
cd $ce_dp
source venv/bin/activate
''')

        jobfile.write('\n')
        jobfile.write('echo "$(date) Loading modules"')
        jobfile.write('''
module load cdo-bin
module load netcdf-bin
''')

        jobfile.write('\n')
        jobfile.write('echo "$(date) Copying pr/tasmin/tasmax datafiles"\n')
        jobfile.write('cp {} $TMPDIR\n'.format(os.path.join(indir, pr)))
        jobfile.write('cp {} $TMPDIR\n'.format(os.path.join(indir, tasmin)))
        jobfile.write('cp {} $TMPDIR\n'.format(os.path.join(indir, tasmax)))

        jobfile.write('\n')
        jobfile.write('echo "$(date) Generating prsn daily file"\n')
        jobfile.write('python scripts/generate_prsn -p $TMPDIR/{} -n $TMPDIR/{} -x $TMPDIR/{} -o $TMPDIR -f {}\n'.format(pr, tasmin, tasmax, prsn))

        jobfile.write('\n')
        jobfile.write('echo "$(date) Generating prsn climos"\n')
        jobfile.write('python scripts/generate_climos -o /path/to/file/output -p mean $TMPDIR/{}\n'.format(prsn))

        jobfile.write('\n')
        jobfile.write('echo "$(date) Discarding used files"\n')
        jobfile.write('rm $TMPDIR/{}\n'.format(pr))
        jobfile.write('rm $TMPDIR/{}\n'.format(tasmin))
        jobfile.write('rm $TMPDIR/{}\n'.format(tasmax))
        jobfile.write('rm $TMPDIR/{}\n'.format(prsn))


def main(args):
    file_trios = get_file_trios(args.indir)
    id = 0
    for trio in file_trios:
        build_job_file(trio, args.indir, args.outdir, id)
        id += 1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('indir', metavar='indir', help='Directory containing input data files')
    parser.add_argument('outdir', metavar='outdir', help='Directory containing output data files')
    args = parser.parse_args()
    main(args)
