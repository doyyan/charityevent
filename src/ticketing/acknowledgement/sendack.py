import pandas as pd
import numpy as np

form = pd.read_excel('TicketForm.xlsx')
form['Acknowledged'] = "No"

for i, row in form.iterrows():
    print(row)

form.to_excel('TicketFormProcessed.xlsx', index=False)