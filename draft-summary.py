
import pandas as pd
import numpy as np

DF = pd.read_csv('tgfbi_all.csv')

f = open('league_summaries.txt', 'w')

picktotals = np.concatenate([list(DF[DF['Overall Pick'] == 1].index),[len(DF)]])

for league in range(0, len(picktotals)-1):
    summary = 'League {}: {} picks'.format(league+1062, picktotals[league+1] - picktotals[league])
    print(summary)
    f.write(summary + '\n')

f.close()
