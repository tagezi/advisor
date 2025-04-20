#     This code is a part of program Advisor
#     Copyright (C) 2022 contributors Advisor
#     The full list is available at the link
#     https://github.com/tagezi/advisor/blob/master/contributors.txt
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Read the data from disk
data = pd.read_csv('../files/SBER_230101_230730.csv', parse_dates=[['<DATE>', '<TIME>']], index_col='<DATE>_<TIME>')

data.rename(columns={'<DATE>_<TIME>': 'datetime',
                     '<OPEN>': 'Open',
                     '<HIGH>': 'High',
                     '<LOW>': 'Low',
                     '<CLOSE>': 'Close',
                     '<VOL>': 'Volume'}, inplace=True)

dtVol = data['Close']

print(dtVol, dtVol.pct_change(), dtVol.pct_change().value_counts())
print(dtVol.describe())
