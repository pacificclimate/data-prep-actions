'''Outputs region pbs job files for rules engine calculation'''

# fill in these variables
connection = "postgresql://use:password@server/database"
log_dir = "/path/to/logs/"
venv = "/path/to/p2a-rule-engine/"
data = "/path/to/data/output/"
ensemble = "p2a_rules"

climatologies = [2020, 2050, 2080]
regions = [
    "bc", "alberni_clayoquot", "boreal_plains", "bulkley_nechako", "capital",
    "cariboo", "central_coast", "central_kootenay", "central_okanagan",
    "columbia_shuswap", "comox_valley", "cowichan_valley", "east_kootenay",
    "fraser_fort_george", "fraser_valley", "greater_vancouver",
    "kitimat_stikine", "kootenay_boundary", "mt_waddington", "nanaimo",
    "northern_rockies", "north_okanagan", "okanagan_similkameen",
    "peace_river", "powell_river", "skeena_queen_charlotte",
    "squamish_lillooet", "stikine", "strathcona", "sunshine_coast",
    "thompson_nicola", "interior", "northern", "vancouver_coast",
    "vancouver_fraser", "vancouver_island", "central_interior",
    "coast_and_mountains", "georgia_depression", "northern_boreal_mountains",
    "southern_interior", "southern_interior_mountains", "sub_boreal_mountains",
    "taiga_plains", "kootenay_/_boundary", "northeast", "omineca", "skeena",
    "south_coast", "thompson_okanagan", "west_coast"]

def outname(region):
    return "kootenay_boundary" if region == "kootenay_/_boundary" else region

for region in regions:
    with open("{}.pbs".format(outname(region)), "w") as outfile:
        # headers
        outfile.writelines([
            "#!/bin/bash\n",
            "#PBS -l nodes=1:ppn=1\n",
            "#PBS -l vmem=12000mb\n",
            "#PBS -l walltime=3:00:00\n",
            "#PBS -o {}\n".format(log_dir),
            "#PBS -e {}\n".format(log_dir),
            "#PBS -m abe\n",
            "#PBS -N p2a_rules_{}\n".format(region)
            ])
        
        #load environment
        outfile.write("\n")
        outfile.write("source {}venv/bin/activate\n".format(venv))
        
        for climo in climatologies:
            outfile.write("python {}scripts/process.py -c {}data/rules.csv -r {} -d {} -e {} -x {} -l CRITICAL > {}_{}.json\n".format(venv, venv, region, climo, ensemble, connection, outname(region), climo))
            outfile.write("cp {}_{}.json {}\n\n".format(outname(region), climo, data))
        
        
