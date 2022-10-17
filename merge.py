import pandas as pd
import matplotlib.pyplot as plt
import sys

aj   = pd.read_csv(sys.argv[1],sep='\t', names=["chr", "position", "orientation", "nucleotide","methylated","coverage","index"])
balb = pd.read_csv(sys.argv[2],sep='\t', names=["chr", "position", "orientation", "nucleotide","methylated","coverage","index"])
blk6 = pd.read_csv(sys.argv[3],sep='\t', names=["chr", "position", "orientation", "nucleotide","methylated","coverage","index"])
cast = pd.read_csv(sys.argv[4],sep='\t', names=["chr", "position", "orientation", "nucleotide","methylated","coverage","index"])
dba  = pd.read_csv(sys.argv[5],sep='\t', names=["chr", "position", "orientation", "nucleotide","methylated","coverage","index"])
fvb  = pd.read_csv(sys.argv[6],sep='\t', names=["chr", "position", "orientation", "nucleotide","methylated","coverage","index"])
pwk  = pd.read_csv(sys.argv[7],sep='\t', names=["chr", "position", "orientation", "nucleotide","methylated","coverage","index"])
wsb  = pd.read_csv(sys.argv[8],sep='\t', names=["chr", "position", "orientation", "nucleotide","methylated","coverage","index"])
bed_file=pd.read_csv(sys.argv[9],sep='\t', names=["chr", "position1", "position","nucleotide","index"])

# chr1	3055043	3055044	CGG;-	0.0003

aj  ['fraction_aj'] = aj['methylated'] / aj['coverage']
balb['fraction_balb'] = balb['methylated'] / balb['coverage']
blk6['fraction_blk6'] = blk6['methylated'] / blk6['coverage']
cast['fraction_cast'] = cast['methylated'] / cast['coverage']
dba ['fraction_dba'] = dba['methylated'] / dba['coverage']
fvb ['fraction_fvb'] = fvb['methylated'] / fvb['coverage']
pwk ['fraction_pwk'] = pwk['methylated'] / pwk['coverage']
wsb ['fraction_wsb'] = wsb['methylated'] / wsb['coverage']



res  = pd.merge(aj, balb, on=["position","chr","index"])
res1 = pd.merge(blk6, cast, on=["position","chr","index"])
res3 = pd.merge(dba, fvb, on=["position","chr","index"])
res4 = pd.merge(pwk, wsb, on=["position","chr","index"])

res5 = pd.merge(res,res1,on=["chr","position","index"])
res6 = pd.merge(res3,res4,on=["chr","position","index"])


res7 = pd.merge(res5,res6,on=["chr","position"])

result=pd.merge(res7,bed_file)

result.columns =   ['chr', 'position','orientation_aj','nucleotide_aj','methylated_aj','coverage_aj','index','fraction_aj',
                   'orientation_balb','nucleotide_balb','methylated_balb','coverage_balb','fraction_balb',
                   'orientation_blk6','nucleotide_blk6','methylated_blk6','coverage_blk6','fraction_blk6',
                   'orientation_cast','nucleotide_cast','methylated_cast','coverage_cast','fraction_cast',
                   'orientation_dba','nucleotide_dba','methylated_dba','coverage_dba','fraction_dba',
                   'orientation_fvb','nucleotide_fvb','methylated_fvb','coverage_fvb','fraction_fvb',
                   'orientation_pwk','nucleotide_pwk','methylated_pwk','coverage_pwk','fraction_pwk',
                   'orientation_wsb','nucleotide_wsb','methylated_wsb','coverage_wsb','fraction_wsb']

                   